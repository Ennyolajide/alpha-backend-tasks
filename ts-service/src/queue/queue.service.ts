import { randomUUID } from 'crypto';
import { EventEmitter } from 'events';

import { Injectable } from '@nestjs/common';

export interface EnqueuedJob<TPayload = unknown> {
  id: string;
  name: string;
  payload: TPayload;
  enqueuedAt: string;
}

@Injectable()
export class QueueService extends EventEmitter {
  private readonly jobs: EnqueuedJob[] = [];

  enqueue<TPayload>(name: string, payload: TPayload): EnqueuedJob<TPayload> {
    const job: EnqueuedJob<TPayload> = {
      id: randomUUID(),
      name,
      payload,
      enqueuedAt: new Date().toISOString(),
    };

    this.jobs.push(job);
    this.emit('enqueue', job);
    return job;
  }

  getQueuedJobs(): readonly EnqueuedJob[] {
    return this.jobs;
  }
}
