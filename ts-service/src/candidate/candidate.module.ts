import { Module } from '@nestjs/common';
import { TypeOrmModule } from '@nestjs/typeorm';

import { AuthModule } from '../auth/auth.module';
import { CandidateDocument } from '../entities/candidate-document.entity';
import { CandidateSummary } from '../entities/candidate-summary.entity';
import { SampleCandidate } from '../entities/sample-candidate.entity';
import { LlmModule } from '../llm/llm.module';
import { QueueModule } from '../queue/queue.module';
import { CandidateController } from './candidate.controller';
import { CandidateService } from './candidate.service';
import { WorkerService } from './worker.service';

@Module({
  imports: [
    TypeOrmModule.forFeature([
      CandidateDocument,
      CandidateSummary,
      SampleCandidate,
    ]),
    AuthModule,
    QueueModule,
    LlmModule,
  ],
  controllers: [CandidateController],
  providers: [CandidateService, WorkerService],
})
export class CandidateModule {}
