from pathlib import Path
import uuid
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .config.settings import settings
from .routes.root import router as root_router
from .routes.health import router as health_router
from .logging_config import configure_logging


APP_DIR = Path(__file__).parent
STATIC_DIR = APP_DIR / "static"


def _forwarded_proto(request: Request) -> str:
    """Return the original scheme reported by a trusted reverse proxy."""
    value = request.headers.get("x-forwarded-proto")
    if value:
        return value.split(",", 1)[0].strip().lower()
    return request.url.scheme


def create_app() -> FastAPI:
    """Create and configure the FastAPI application instance."""
    configure_logging()
    app = FastAPI(title="TEMPLATE")
    app.mount(
        "/static",
        StaticFiles(directory=str(STATIC_DIR), check_dir=False),
        name="static",
    )
    templates = Jinja2Templates(directory=str(APP_DIR / "templates"))
    # Wrap Jinja2 get_template to avoid passing context dict as "globals" to
    # Jinja2's cache key (some package versions cause a TypeError when a dict
    # is used as part of the cache key). We always call the original
    # get_template without globals so rendering still receives the context.
    try:
        _orig_get_template = templates.env.get_template

        def _safe_get_template(name, parent=None, globals=None):
            return _orig_get_template(name, parent=parent, globals=None)

        templates.env.get_template = _safe_get_template
    except Exception:
        # If env isn't present or wrapping fails, silently continue — the
        # runtime will surface issues as before.
        pass
    app.state.templates = templates

    @app.middleware("http")
    async def add_correlation_id(request: Request, call_next):
        cid = request.headers.get("X-Correlation-ID") or str(uuid.uuid4())
        request.state.correlation_id = cid
        proto = _forwarded_proto(request)
        if settings.force_https and proto != "https":
            response = RedirectResponse(
                str(request.url.replace(scheme="https")),
                status_code=307,
            )
        else:
            response = await call_next(request)
        response.headers["X-Correlation-ID"] = cid
        if settings.force_https or settings.env.lower() == "production":
            response.headers.setdefault(
                "Content-Security-Policy",
                "upgrade-insecure-requests",
            )
        if proto == "https":
            response.headers.setdefault(
                "Strict-Transport-Security",
                "max-age=31536000; includeSubDomains",
            )
        return response

    @app.get("/favicon.ico", include_in_schema=False)
    async def favicon():
        return RedirectResponse(url="/static/favicon.svg", status_code=308)

    app.include_router(root_router)
    app.include_router(health_router)
    return app
