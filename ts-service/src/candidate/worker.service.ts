import { Inject, Injectable, Logger, OnModuleInit } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';

import { CandidateDocument } from '../entities/candidate-document.entity';
import { CandidateSummary } from '../entities/candidate-summary.entity';
import { SUMMARIZATION_PROVIDER, SummarizationProvider } from '../llm/summarization-provider.interface';
import { EnqueuedJob, QueueService } from '../queue/queue.service';

@Injectable()
export class WorkerService implements OnModuleInit {
  private readonly logger = new Logger(WorkerService.name);

  constructor(
    private readonly queueService: QueueService,
    @InjectRepository(CandidateSummary)
    private readonly summaryRepository: Repository<CandidateSummary>,
    @InjectRepository(CandidateDocument)
    private readonly documentRepository: Repository<CandidateDocument>,
    @Inject(SUMMARIZATION_PROVIDER)
    private readonly summarizationProvider: SummarizationProvider,
  ) {}

  onModuleInit() {
    this.queueService.on('enqueue', (job: EnqueuedJob) => {
      if (job.name === 'generate-summary') {
        this.processSummaryJob(job).catch((err) => {
          this.logger.error(`Unhandled error processing job ${job.id}: ${err.message}`, err.stack);
        });
      }
    });
    this.logger.log('WorkerService initialized and listening for jobs.');
  }

  private async processSummaryJob(job: EnqueuedJob) {
    const { summaryId, candidateId, workspaceId } = job.payload as any;
    this.logger.log(`Processing summary job for candidate ${candidateId}, summary ${summaryId}`);

    const summary = await this.summaryRepository.findOne({ where: { id: summaryId } });
    if (!summary) return;

    try {
      // 1. Gather documents
      const docs = await this.documentRepository.find({
        where: { candidateId, workspaceId },
      });

      if (docs.length === 0) {
        throw new Error('No documents found for this candidate.');
      }

      // 2. Call LLM
      const result = await this.summarizationProvider.generateCandidateSummary({
        candidateId,
        documents: docs.map((d) => d.rawText),
      });

      // 3. Persist results
      summary.status = 'completed';
      summary.score = result.score;
      summary.strengths = result.strengths;
      summary.concerns = result.concerns;
      summary.summary = result.summary;
      summary.recommendedDecision = result.recommendedDecision;
      summary.provider = 'gemini-2.0-flash';
      summary.promptVersion = 'v1';

      await this.summaryRepository.save(summary);
      this.logger.log(`Summary ${summaryId} completed successfully.`);
    } catch (error: any) {
      this.logger.error(`Job failed: ${error.message}`);
      summary.status = 'failed';
      summary.errorMessage = error.message;
      await this.summaryRepository.save(summary);
    }
  }
}
