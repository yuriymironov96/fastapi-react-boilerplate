# Install locally

Install package manager

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Install deps

```bash
uv sync --group dev
```

Copy env variables

```bash
cp .env.example .env
```

Set up database

```bash
docker-compose up postgres
```

Seed data

```bash
uv run python -m app.initial_data
```

Install pre-commit hooks

```bash
uv run pre-commit install
```

# run locally

```bash
docker compose up postgres
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

# Migrations

Generate after model changes:
```bash
uv run alembic revision -m "your-migration-name" --autogenerate
```

Apply:
```bash
uv run alembic upgrade head
```

# Tests

```bash
uv run pytest
```

# Linters

Run manually:
```bash
uv run mypy --explicit-package-bases app
uv run ruff check .
```

# Pre-commit hooks

Pre-commit hooks are set up to automatically run linters before each commit.

The hooks will automatically run `ruff` and `mypy` on every commit. To run them manually:
```bash
uv run pre-commit run --all-files
```

# TODO:

- auth
- task manager (taskiq?)
- S3
- frontend, generate schema, tanstack
- deploy config
- healthcheck
- maybe dependabot or some other development experience goodies
- smtp - maybe not priority, just use https://sabuhish.github.io/fastapi-mail/
