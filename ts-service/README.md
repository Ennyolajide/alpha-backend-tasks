# TalentFlow TypeScript Service: Candidate Document Intake + Summary

NestJS service implementing a complete candidate document intake and summary workflow for the backend assessment.

This service provides a full API for uploading candidate documents, generating AI-powered summaries asynchronously through a queue-based system, and retrieving structured candidate evaluations.

## Features

- **Document Management**: Upload and store candidate documents (resumes, cover letters) with metadata
- **Asynchronous Summary Generation**: Queue-based processing using LLM providers for candidate evaluation
- **Workspace-Based Access Control**: Recruiters can only access candidates within their workspace
- **Provider Abstraction**: Extensible LLM interface supporting multiple providers (Gemini, fake for testing)
- **Automatic Fallback**: Seamlessly uses fake provider when no API key is configured
- **Structured Output**: AI-generated summaries with scores, strengths, concerns, and recommendations
- **Database Integration**: PostgreSQL with TypeORM and migration-based schema management
- **Comprehensive Testing**: Jest suite with e2e tests using fake LLM provider

## Prerequisites

- Node.js 22+
- npm
- PostgreSQL running from repository root:

```bash
docker compose up -d postgres
```

## Setup

```bash
cd ts-service
npm install
cp .env.example .env
```

## Environment

- `PORT`
- `DATABASE_URL`
- `NODE_ENV`
- `GEMINI_API_KEY` (leave blank to use fake provider)
- `USE_FAKE_LLM` (defaults to `true`; automatically enabled if `GEMINI_API_KEY` is not provided)

Do not commit API keys or secrets.

The service automatically uses the fake LLM provider if no Gemini API key is provided, making it easy to test and develop without external API dependencies.

## Run Migrations

```bash
cd ts-service
npm run migration:run
```

## Run Service

```bash
cd ts-service
npm run start:dev
```

## Run Tests

```bash
cd ts-service
npm test
npm run test:e2e
```

## API Endpoints

### Authentication
All endpoints require workspace-scoped authentication headers:
- `x-user-id`: User identifier (e.g., `user-1`)
- `x-workspace-id`: Workspace identifier (e.g., `workspace-1`)

### Sample Endpoints
- `POST /sample/candidates` - Create a sample candidate

### Candidate Document Endpoints
- `POST /candidates/:candidateId/documents` - Upload candidate document
- `POST /candidates/:candidateId/summaries/generate` - Request summary generation
- `GET /candidates/:candidateId/summaries` - List candidate summaries
- `GET /candidates/:candidateId/summaries/:summaryId` - Get specific summary

### Health Check
- `GET /health` - Service health status

## Project Layout

- `src/auth/`: fake auth guard, user decorator, auth types
- `src/entities/`: starter entities + candidate document/summary entities
- `src/sample/`: tiny example module (controller/service/dto)
- `src/candidate/`: candidate document and summary management
- `src/queue/`: in-memory queue abstraction
- `src/llm/`: provider interface + fake + Gemini providers
- `src/migrations/`: TypeORM migration files
- `src/config/`: TypeORM configuration
- `test/`: Jest test suite

## Assumptions and Tradeoffs

### Assumptions
- Documents are provided as text content (no file upload handling for simplicity)
- Single LLM provider active at a time (configurable via environment)
- PostgreSQL as the database (configured for the assessment)
- In-memory queue sufficient for development/testing scenarios
- Workspace-based access control meets the security requirements

### Tradeoffs
- **Local File Storage**: Documents stored as local file paths rather than cloud storage for assessment focus
- **Text-Based Intake**: Simplified document handling to focus on core workflow logic
- **In-Memory Queue**: Suitable for development but would need Redis for production scaling
- **Basic Auth**: Fake authentication guard for assessment; production would require proper JWT/OAuth
- **Single Provider**: No fallback providers implemented; production might need redundancy
- **No Caching**: Summary results not cached; could be added for performance optimization
- **Limited Validation**: Basic DTO validation; production might need more comprehensive business rules

## Notes

### Design Decisions

- **Service Layer Pattern**: Used `CandidateService` to separate business logic from controllers, preventing fat controllers and ensuring clean separation of concerns.
- **Provider Abstraction**: Implemented `SummarizationProvider` interface to decouple LLM logic from business services, allowing easy provider switching and testing.
- **Queue-Based Processing**: Used Bull queue for async summary generation to avoid blocking API responses and enable horizontal scaling.
- **Workspace Isolation**: Applied workspace-based filtering at the service layer to ensure data isolation and security.

### Schema Decisions

- **Normalized Relational Structure**: Chose separate tables (`candidate_documents`, `candidate_summaries`) over JSON columns for better data integrity, query performance, and future extensibility.
- **Foreign Key Constraints**: Applied proper foreign keys and indexes for referential integrity and query optimization.
- **Status Tracking**: Implemented status enum for summaries (`pending`, `completed`, `failed`) to track async processing state.

### Potential Improvements (Given More Time)

- **File Upload Support**: Implement proper multipart file uploads with cloud storage integration (AWS S3, Google Cloud Storage)
- **Background Processing**: Add Redis-based queue for production scalability and persistence
- **Multiple LLM Providers**: Implement provider fallback and load balancing for reliability
- **Caching Layer**: Add Redis caching for frequently accessed summaries and documents
- **Rate Limiting**: Implement API rate limiting to prevent abuse and manage LLM costs
- **Audit Logging**: Add comprehensive logging for document access and summary generation
- **Document Processing**: Integrate document parsing (PDF, DOCX) for richer text extraction
- **Summary Versioning**: Track changes to summaries over time with version history
