import { Test, TestingModule } from '@nestjs/testing';
import { getRepositoryToken } from '@nestjs/typeorm';
import { NotFoundException, ForbiddenException } from '@nestjs/common';

import { CandidateDocument } from '../entities/candidate-document.entity';
import { CandidateSummary } from '../entities/candidate-summary.entity';
import { SampleCandidate } from '../entities/sample-candidate.entity';
import { QueueService } from '../queue/queue.service';
import { CandidateService } from './candidate.service';

describe('CandidateService', () => {
  let service: CandidateService;

  const candidateRepository = {
    findOne: jest.fn(),
  };

  const documentRepository = {
    create: jest.fn(),
    save: jest.fn(),
    find: jest.fn(),
  };

  const summaryRepository = {
    create: jest.fn(),
    save: jest.fn(),
    find: jest.fn(),
    findOne: jest.fn(),
  };

  const queueService = {
    enqueue: jest.fn(),
  };

  beforeEach(async () => {
    jest.clearAllMocks();

    const module: TestingModule = await Test.createTestingModule({
      providers: [
        CandidateService,
        {
          provide: getRepositoryToken(SampleCandidate),
          useValue: candidateRepository,
        },
        {
          provide: getRepositoryToken(CandidateDocument),
          useValue: documentRepository,
        },
        {
          provide: getRepositoryToken(CandidateSummary),
          useValue: summaryRepository,
        },
        {
          provide: QueueService,
          useValue: queueService,
        },
      ],
    }).compile();

    service = module.get<CandidateService>(CandidateService);
  });

  describe('ensureCandidateAccess', () => {
    it('throws NotFoundException if candidate does not exist', async () => {
      candidateRepository.findOne.mockResolvedValue(null);

      await expect(
        service.uploadDocument(
          { userId: 'user-1', workspaceId: 'ws-1' },
          'invalid-id',
          { documentType: 'resume', fileName: 'cv.pdf', rawText: 'text' },
        ),
      ).rejects.toThrow(NotFoundException);
    });

    it('throws ForbiddenException if workspace id does not match', async () => {
      candidateRepository.findOne.mockResolvedValue({
        id: 'cand-1',
        workspaceId: 'ws-different',
      });

      await expect(
        service.uploadDocument(
          { userId: 'user-1', workspaceId: 'ws-1' },
          'cand-1',
          { documentType: 'resume', fileName: 'cv.pdf', rawText: 'text' },
        ),
      ).rejects.toThrow(ForbiddenException);
    });
  });

  describe('uploadDocument', () => {
    it('saves a new document for an authorized candidate', async () => {
      candidateRepository.findOne.mockResolvedValue({
        id: 'cand-1',
        workspaceId: 'ws-1',
      });
      documentRepository.create.mockImplementation((dto) => ({ ...dto, id: 'doc-1' }));
      documentRepository.save.mockImplementation(async (doc) => doc);

      const result = await service.uploadDocument(
        { userId: 'user-1', workspaceId: 'ws-1' },
        'cand-1',
        { documentType: 'resume', fileName: 'cv.pdf', rawText: 'my cv text' },
      );

      expect(documentRepository.save).toHaveBeenCalled();
      expect(result.rawText).toBe('my cv text');
      expect(result.candidateId).toBe('cand-1');
      expect(result.workspaceId).toBe('ws-1');
    });
  });

  describe('queueSummaryGeneration', () => {
    it('creates a pending summary and enqueues a job', async () => {
      candidateRepository.findOne.mockResolvedValue({
        id: 'cand-1',
        workspaceId: 'ws-1',
      });
      summaryRepository.create.mockImplementation((dto) => ({ ...dto, id: 'sum-1', status: 'pending' }));
      summaryRepository.save.mockImplementation(async (sum) => sum);

      const result = await service.queueSummaryGeneration(
        { userId: 'user-1', workspaceId: 'ws-1' },
        'cand-1',
      );

      expect(summaryRepository.save).toHaveBeenCalled();
      expect(queueService.enqueue).toHaveBeenCalledWith('generate-summary', expect.objectContaining({
        summaryId: 'sum-1',
        candidateId: 'cand-1',
      }));
      expect(result.status).toBe('pending');
    });
  });
});
