TEMPLATE - Production-ready Python template

Minimal boilerplate to bootstrap a production-oriented Python service.

Quickstart

1. Create a virtualenv and install dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. Run the app in development:

```powershell
$env:PYTHONPATH = '.'
uvicorn --factory src.app.factory:create_app --reload --port 8000
```

3. Run tests and linters:

```powershell
$env:PYTHONPATH = '.'
ruff check .
pytest -q
```

Documentation

Extended documentation is in the `docs/` folder. See [docs/README.md](docs/README.md) for details.

Deployment notes

- Use `.env` only for local Compose. Set `ENV_FILE=.env` locally when you want Compose services to load it. The Docker image excludes `.env`; set production secrets in the platform panel.
- Coolify deployments should use `POSTGRES_INTERNAL_PORT=5432` for container-to-container traffic and `POSTGRES_HOST_PORT` only for optional host exposure.
- Production proxy deployments should set `ENV=production`, `FORCE_HTTPS=true`, and `SESSION_COOKIE_SECURE=true`.
- See [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) and [troubleshooting-coolify.md](troubleshooting-coolify.md).

