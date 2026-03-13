import { Test, TestingModule } from '@nestjs/testing';
import { INestApplication, ValidationPipe } from '@nestjs/common';
import request from 'supertest';
import { DataSource } from 'typeorm';
import { AppModule } from '../src/app.module';

describe('CandidateController (e2e)', () => {
  let app: INestApplication;

  beforeAll(async () => {
    // Force fake LLM for tests to avoid external API calls
    process.env.USE_FAKE_LLM = 'true';
    
    const moduleFixture: TestingModule = await Test.createTestingModule({
      imports: [AppModule],
    }).compile();

    app = moduleFixture.createNestApplication();
    app.useGlobalPipes(new ValidationPipe());
    await app.init();

    // Run migrations to ensure database schema is up to date
    const dataSource = app.get(DataSource);
    await dataSource.runMigrations();
  });

  afterAll(async () => {
    await app.close();
  });

  it('should flow: upload doc -> generate -> get result', async () => {
    // 1. Setup - Create a candidate (using sample endpoint)
    const candidateResponse = await request(app.getHttpServer())
      .post('/sample/candidates')
      .set('x-user-id', 'test-user')
      .set('x-workspace-id', 'test-ws')
      .send({ fullName: 'John Doe', email: 'john@example.com' })
      .expect(201);

    const candidateId = candidateResponse.body.id;

    // 2. Upload Document
    await request(app.getHttpServer())
      .post(`/candidates/${candidateId}/documents`)
      .set('x-user-id', 'test-user')
      .set('x-workspace-id', 'test-ws')
      .send({
        documentType: 'resume',
        fileName: 'resume.txt',
        rawText: 'John is a great developer with 10 years of experience.'
      })
      .expect(201);

    // 3. Request Summary Generation
    const summaryResponse = await request(app.getHttpServer())
      .post(`/candidates/${candidateId}/summaries/generate`)
      .set('x-user-id', 'test-user')
      .set('x-workspace-id', 'test-ws')
      .expect(201);

    const summaryId = summaryResponse.body.id;
    expect(summaryResponse.body.status).toBe('pending');

    // 4. Check status (Wait for async processing)
    // The worker is event-driven and in-memory, so it should be near-instant.
    await new Promise(resolve => setTimeout(resolve, 1000));

    const getResponse = await request(app.getHttpServer())
      .get(`/candidates/${candidateId}/summaries/${summaryId}`)
      .set('x-user-id', 'test-user')
      .set('x-workspace-id', 'test-ws')
      .expect(200);

    expect(getResponse.body.status).toBe('completed');
    expect(getResponse.body.summary).toContain('Fake summary');
    expect(getResponse.body.score).toBeDefined();
  });

  it('should block access from another workspace', async () => {
     // Create candidate in WS-A
     const candidateResponse = await request(app.getHttpServer())
      .post('/sample/candidates')
      .set('x-user-id', 'user-a')
      .set('x-workspace-id', 'ws-a')
      .send({ fullName: 'Alice', email: 'alice@example.com' })
      .expect(201);

    const candidateId = candidateResponse.body.id;

    // Try to access from WS-B
    await request(app.getHttpServer())
      .get(`/candidates/${candidateId}/summaries`)
      .set('x-user-id', 'user-b')
      .set('x-workspace-id', 'ws-b')
      .expect(403);
  });
});
