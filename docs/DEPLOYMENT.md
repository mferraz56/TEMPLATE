# Deployment

Docker image build

```bash
docker build -t template:latest .
```

The image is built from `/app/project`, excludes `.env` through `.dockerignore`,
and starts Uvicorn with `--app-dir /app/project` plus proxy header support.

Run container (example)

```bash
docker run --rm -p 8000:8000 \
  -e DATABASE_URL='postgresql+psycopg://user:pass@host:5432/db' \
  -e REDIS_URL='redis://host:6379/0' \
  template:latest
```

Docker Compose

```bash
docker compose up -d --build
```

The default Compose contract is:

- `app` runs startup migrations with `RUN_MIGRATIONS=1`.
- `worker` sets `RUN_MIGRATIONS=0` to avoid scale-out races.
- `db` exposes `${POSTGRES_HOST_PORT}` on the host, while app and worker use
  `${POSTGRES_INTERNAL_PORT}` internally.
- `db` and `redis` health checks gate app and worker startup.
- `ENV_FILE` controls the Compose service `env_file`; the reusable default is
  `.env.example`, and local projects can set `ENV_FILE=.env`.

Coolify / PaaS notes
- Configure secrets in the target platform. Do not bake `.env` into the image.
- Use a complete `DATABASE_URL` from Coolify when available, or set
  `POSTGRES_HOST`, `POSTGRES_INTERNAL_PORT=5432`, `POSTGRES_USER`,
  `POSTGRES_PASSWORD`, and `POSTGRES_DB`.
- Use `POSTGRES_HOST_PORT` only when you intentionally publish Postgres to the
  host. Do not point app or worker at the published host port.
- For HTTPS behind the Coolify proxy, set `ENV=production`, `FORCE_HTTPS=true`,
  and `SESSION_COOKIE_SECURE=true`.
- Keep static assets referenced from root paths such as `/static/favicon.svg`.
- Troubleshooting details live in [../troubleshooting-coolify.md](../troubleshooting-coolify.md).

Smoke checks

```bash
docker compose --env-file .env.example config
python -m pytest tests/test_smoke.py -q
```

Security
- Do not commit real secrets; use `.env` for local development and platform secrets for production.
- Keep `SECRET_KEY` unique per environment.
