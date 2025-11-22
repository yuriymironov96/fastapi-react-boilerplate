# Install locally

Install package manager

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Install deps

```bash
uv sync
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

# run locally

```bash
docker compose up postgres
uv run uvicorn main:app --host 0.0.0.0 --port 8000 --reload
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

# todo:
- auth
- admin panel
- task manager (taskiq?)
- frontend, generate schema, tanstack
- deploy config