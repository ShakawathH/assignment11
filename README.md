# Assignment 11: Assignment-Implement and Test a Calculation Model with Optional Factory Pattern

Defining a Calculation model using SQLAlchemy and creating robust validation with Pydantic schemas. You will also optionally implement a factory pattern for extensibility and reinforce your CI/CD pipeline by testing the new functionality.

**Docker Hub repository:** https://hub.docker.com/r/shakawathh/assignment11

## What this module adds

- **`Calculation` SQLAlchemy model** (`app/models/calculation.py`): columns `id`, `a`, `b`, `type`, `result`, optional `user_id` (foreign key to `users.id`, `ON DELETE CASCADE`), `created_at`. The `result` is **stored** at creation time. Database `CHECK` constraints reject unknown types and division by zero.
- **Pydantic schemas** (`app/schemas/calculation.py`): `CalculationCreate` (`a`, `b`, `type` = Add / Sub / Multiply / Divide, case-insensitive; rejects bad types, non-numeric / NaN / infinite operands and division by zero) and `CalculationRead` (`id`, `a`, `b`, `type`, `result`, `user_id`, `created_at`).
- **Factory pattern** (`app/operations/factory.py`): `CalculationFactory.get_operation(type)` returns the right `Operation` class; new operations can be added with `CalculationFactory.register`.

## Project structure

| Path | Purpose |
| --- | --- |
| `app/models/calculation.py`, `app/models/user.py` | SQLAlchemy `Calculation` and `User` models |
| `app/schemas/calculation.py` | Pydantic `CalculationCreate`, `CalculationRead`, `CalculationType` |
| `app/operations/` | Calculator functions and the calculation factory |
| `main.py` | FastAPI app (`/`, `/add`, `/subtract`, `/multiply`, `/divide`, `/health`) |
| `tests/unit` | Operations, factory, schemas and model logic (no database) |
| `tests/integration` | Calculation/User records in PostgreSQL, error cases, API tests |
| `tests/e2e` | Playwright browser tests |
| `.github/workflows/test.yml` | CI/CD: test -> Trivy scan -> Docker Hub deploy |
| `REFLECTION.md` | Reflection on the assignment |

## Run the tests locally

1. Create a virtual environment and install dependencies:

   ```bash
   python3 -m venv venv
   source venv/bin/activate        # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   playwright install chromium
   ```

2. Start PostgreSQL (the tests need it, default URL `postgresql://postgres:postgres@localhost:5432/fastapi_db`):

   ```bash
   docker compose up -d db
   ```

   If the container exits with a data-directory error, reset the old volume:
   `docker compose down -v && docker compose up -d db`.

3. Run everything:

   ```bash
   pytest
   ```

   Or by suite: `pytest tests/unit/`, `pytest tests/integration/`, `pytest tests/e2e/`.
   Only the calculation tests: `pytest tests/unit/test_calculation_*.py tests/integration/test_calculation_db.py`.

   The integration tests read `DATABASE_URL` (default `postgresql://postgres:postgres@localhost:5432/fastapi_db`); set it to point at a different database.

## Run the application

```bash
python main.py            # http://127.0.0.1:8000
# or with Docker Compose
docker compose up --build
```

## Run the published Docker image

```bash
docker pull shakawathh/assignment11:latest
docker run -p 8000:8000 shakawathh/assignment11:latest
```

Then open http://localhost:8000 (health check: http://localhost:8000/health).

## CI/CD pipeline

On every push / pull request to `main`, GitHub Actions:

1. **test** – starts a PostgreSQL 16 service (`DATABASE_URL` is set for the job), installs dependencies, runs the unit (user + calculation), integration (database) and e2e tests.
2. **security** – builds the Docker image and scans it with Trivy (fails on fixable HIGH/CRITICAL issues).
3. **deploy** – on `main` only, builds and pushes the image to Docker Hub.

Required repository secrets: `DOCKERHUB_USERNAME`, `DOCKERHUB_TOKEN`.
