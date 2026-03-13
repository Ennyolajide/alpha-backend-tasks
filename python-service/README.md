# InsightOps Python Service: Briefing Generator

FastAPI service for generating and managing investment briefing reports.

This service provides a complete API for creating, validating, and generating HTML reports for company briefings, including key points, risks, metrics, and analyst recommendations.

## Features

- **Briefing Management**: Create, retrieve, and list investment briefings
- **Data Validation**: Strict schema validation with Pydantic
- **HTML Report Generation**: Jinja2 templated reports with snapshot storage
- **Database Integration**: PostgreSQL with SQLAlchemy ORM
- **Testing**: Comprehensive pytest suite with in-memory SQLite

## Prerequisites

- Python 3.12+
- PostgreSQL (via Docker Compose from repository root)

## Setup

1. **Start PostgreSQL**:
   ```bash
   docker compose up -d postgres
   ```

2. **Create Virtual Environment**:
   ```bash
   cd python-service
   python3.12 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install Dependencies**:
   ```bash
   python -m pip install -r requirements.txt
   ```

4. **Configure Environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your database URL and other settings
   ```

## Environment Variables

Key variables in `.env`:

- `DATABASE_URL`: PostgreSQL connection string
- `APP_ENV`: Environment (development/production)
- `APP_PORT`: Port for the service (default: 8000)

## Run Migrations

Apply database migrations:

```bash
source .venv/bin/activate
python -m app.db.run_migrations up
```

Rollback migrations:

```bash
source .venv/bin/activate
python -m app.db.run_migrations down --steps 1
```

## Run Service

Start the FastAPI server:

```bash
source .venv/bin/activate
python -m uvicorn app.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`

## Run Tests

Execute the test suite:

```bash
source .venv/bin/activate
python -m pytest
```

Tests use an in-memory SQLite database for isolation.

## API Endpoints

- `POST /briefings` - Create a new briefing
- `GET /briefings` - List all briefings
- `GET /briefings/{id}` - Get a specific briefing
- `POST /briefings/{id}/generate` - Generate HTML report
- `GET /briefings/{id}/html` - View generated HTML report
- `GET /health` - Health check

## Project Layout

- `app/main.py`: FastAPI application bootstrap
- `app/config.py`: Environment configuration
- `app/db/`: Database session and migration management
- `db/migrations/`: SQL migration files
- `app/models/`: SQLAlchemy ORM models
- `app/schemas/`: Pydantic validation schemas
- `app/services/`: Business logic and formatting
- `app/api/`: FastAPI route handlers
- `app/templates/`: Jinja2 HTML templates
- `tests/`: Test suite

## Assumptions and Tradeoffs

- **Database Choice**: PostgreSQL for production reliability; tests use SQLite for simplicity
- **Template Storage**: HTML reports are pre-rendered and stored as snapshots for performance, trading storage for faster retrieval
- **Validation**: Strict schema constraints ensure data quality but may require more upfront data preparation
- **No Authentication**: Assumes the service runs behind an authenticated gateway
- **Single Service**: Designed as a monolithic service; could be split into microservices for larger scale

## Notes

### Design Decisions

- **Service Layer Pattern**: Used `briefing_service.py` to separate business logic from API handlers, preventing fat controllers and ensuring clean separation of concerns.
- **Formatter Layer**: Introduced a dedicated layer to transform database models into view models before Jinja2 rendering, decoupling data processing from presentation.
- **Snapshot Storage**: Reports are pre-rendered and stored as HTML strings in the database, ensuring immutable snapshots that persist even if underlying data changes.

### Schema Decisions

- **Normalized Relational Structure**: Chose separate tables (`briefings`, `briefing_points`, `briefing_risks`, `briefing_metrics`) over JSON columns for better data integrity, query performance, and future analytics capabilities.
- **Constraints and Indexes**: Applied unique constraints on metric names per briefing and indexes on frequently queried columns (`ticker`, `status`) for efficient data retrieval and enforcement of business rules.

### Potential Improvements (Given More Time)

- **Background Processing**: Implement async task queues (e.g., Celery) for report generation to handle high-volume scenarios without blocking the API.
- **Multiple Output Formats**: Extend support for PDF, JSON, or other formats using libraries like WeasyPrint.
- **Versioning System**: Add report versioning to track changes over time and enable historical comparisons.
- **Caching Layer**: Integrate Redis for caching list and get operations to reduce database load.
