import {
  Body,
  Controller,
  Get,
  Param,
  Post,
  UseGuards,
} from '@nestjs/common';

import { AuthUser } from '../auth/auth.types';
import { CurrentUser } from '../auth/auth-user.decorator';
import { FakeAuthGuard } from '../auth/fake-auth.guard';
import { CandidateService } from './candidate.service';
import { CreateCandidateDocumentDto } from './dto/create-candidate-document.dto';

@Controller('candidates')
@UseGuards(FakeAuthGuard)
export class CandidateController {
  constructor(private readonly candidateService: CandidateService) {}

  @Post(':candidateId/documents')
  async uploadDocument(
    @CurrentUser() user: AuthUser,
    @Param('candidateId') candidateId: string,
    @Body() dto: CreateCandidateDocumentDto,
  ) {
    return this.candidateService.uploadDocument(user, candidateId, dto);
  }

  @Post(':candidateId/summaries/generate')
  async generateSummary(
    @CurrentUser() user: AuthUser,
    @Param('candidateId') candidateId: string,
  ) {
    return this.candidateService.queueSummaryGeneration(user, candidateId);
  }

  @Get(':candidateId/summaries')
  async listSummaries(
    @CurrentUser() user: AuthUser,
    @Param('candidateId') candidateId: string,
  ) {
    return this.candidateService.listSummaries(user, candidateId);
  }

  @Get(':candidateId/summaries/:summaryId')
  async getSummary(
    @CurrentUser() user: AuthUser,
    @Param('candidateId') candidateId: string,
    @Param('summaryId') summaryId: string,
  ) {
    return this.candidateService.getSummary(user, candidateId, summaryId);
  }
}
