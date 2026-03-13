import { randomUUID } from 'crypto';

import { Injectable, NotFoundException, ForbiddenException } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';

import { AuthUser } from '../auth/auth.types';
import { CandidateDocument } from '../entities/candidate-document.entity';
import { CandidateSummary } from '../entities/candidate-summary.entity';
import { SampleCandidate } from '../entities/sample-candidate.entity';
import { QueueService } from '../queue/queue.service';
import { CreateCandidateDocumentDto } from './dto/create-candidate-document.dto';

@Injectable()
export class CandidateService {
  constructor(
    @InjectRepository(SampleCandidate)
    private readonly candidateRepository: Repository<SampleCandidate>,
    @InjectRepository(CandidateDocument)
    private readonly documentRepository: Repository<CandidateDocument>,
    @InjectRepository(CandidateSummary)
    private readonly summaryRepository: Repository<CandidateSummary>,
    private readonly queueService: QueueService,
  ) {}

  async uploadDocument(
    user: AuthUser,
    candidateId: string,
    dto: CreateCandidateDocumentDto,
  ): Promise<CandidateDocument> {
    const candidate = await this.ensureCandidateAccess(user, candidateId);

    const document = this.documentRepository.create({
      id: randomUUID(),
      candidateId: candidate.id,
      workspaceId: user.workspaceId,
      documentType: dto.documentType,
      fileName: dto.fileName,
      storageKey: `local://${randomUUID()}-${dto.fileName}`,
      rawText: dto.rawText,
    });

    return this.documentRepository.save(document);
  }

  async queueSummaryGeneration(user: AuthUser, candidateId: string): Promise<CandidateSummary> {
    const candidate = await this.ensureCandidateAccess(user, candidateId);

    const summary = this.summaryRepository.create({
      id: randomUUID(),
      candidateId: candidate.id,
      workspaceId: user.workspaceId,
      status: 'pending',
    });

    const savedSummary = await this.summaryRepository.save(summary);

    // Enqueue background job
    this.queueService.enqueue('generate-summary', {
      summaryId: savedSummary.id,
      candidateId: candidate.id,
      workspaceId: user.workspaceId,
    });

    return savedSummary;
  }

  async listSummaries(user: AuthUser, candidateId: string): Promise<CandidateSummary[]> {
    await this.ensureCandidateAccess(user, candidateId);

    return this.summaryRepository.find({
      where: { candidateId, workspaceId: user.workspaceId },
      order: { createdAt: 'DESC' },
    });
  }

  async getSummary(user: AuthUser, candidateId: string, summaryId: string): Promise<CandidateSummary> {
    const summary = await this.summaryRepository.findOne({
      where: { id: summaryId, candidateId, workspaceId: user.workspaceId },
    });

    if (!summary) {
      throw new NotFoundException(`Summary ${summaryId} not found for candidate ${candidateId}`);
    }

    return summary;
  }

  private async ensureCandidateAccess(user: AuthUser, candidateId: string): Promise<SampleCandidate> {
    const candidate = await this.candidateRepository.findOne({
      where: { id: candidateId },
    });

    if (!candidate) {
      throw new NotFoundException(`Candidate ${candidateId} not found`);
    }

    if (candidate.workspaceId !== user.workspaceId) {
      throw new ForbiddenException('You do not have access to this candidate');
    }

    return candidate;
  }
}
