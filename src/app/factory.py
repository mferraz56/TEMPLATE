from pathlib import Path
import uuid
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates

from .routes.root import router as root_router
from .routes.health import router as health_router
from .logging_config import configure_logging


def create_app() -> FastAPI:
    """Create and configure the FastAPI application instance."""
    configure_logging()
    app = FastAPI(title="TEMPLATE")
    templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))
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
        response = await call_next(request)
        response.headers["X-Correlation-ID"] = cid
        return response

    app.include_router(root_router)
    app.include_router(health_router)
    return app
