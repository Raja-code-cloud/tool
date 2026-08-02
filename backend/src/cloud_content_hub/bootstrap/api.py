from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

from cloud_content_hub.api.errors import install_exception_handlers
from cloud_content_hub.api.middleware.request_context import RequestContextMiddleware
from cloud_content_hub.api.openapi import configure_openapi
from cloud_content_hub.api.routers.v1.router import root_router
from cloud_content_hub.bootstrap.container import Container
from cloud_content_hub.bootstrap.handlers import wire_handlers
from cloud_content_hub.bootstrap.startup import bootstrap_lifespan
from cloud_content_hub.core.config import Settings, load_settings
from cloud_content_hub.core.logging import configure_logging
from cloud_content_hub.infrastructure.identity.config import IdentitySettings
from cloud_content_hub.infrastructure.identity.factory import IdentityFactory
from cloud_content_hub.infrastructure.identity.middleware import AuthenticationMiddleware


def create_app(settings: Settings | None = None) -> FastAPI:
    resolved_settings = settings or load_settings()
    configure_logging(resolved_settings)
    app = FastAPI(
        title="Cloud Content Hub AI REST API",
        summary="Public v1 contract; success envelopes and RFC 9457-compatible failures.",
        version=resolved_settings.service_version,
        docs_url="/docs" if resolved_settings.openapi_enabled else None,
        redoc_url=None,
        openapi_url="/openapi.json" if resolved_settings.openapi_enabled else None,
        swagger_ui_parameters={
            "displayRequestDuration": True,
            "filter": True,
            "persistAuthorization": True,
        },
        lifespan=bootstrap_lifespan,
    )

    container = Container.create(resolved_settings)
    app.state.container = container
    app.state.handlers = wire_handlers(container)

    identity_factory = IdentityFactory(
        IdentitySettings(environment=resolved_settings.environment.value)
    )
    app.state.identity_factory = identity_factory

    app.add_middleware(
        GZipMiddleware,
        minimum_size=resolved_settings.http_compression_minimum_size,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=resolved_settings.http_allowed_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=[
            "Authorization",
            "Content-Type",
            "Idempotency-Key",
            "If-Match",
            "If-None-Match",
            "X-Correlation-ID",
            "X-CSRF-Token",
            "X-Workspace-ID",
        ],
        expose_headers=["X-Request-ID", "X-Correlation-ID", "ETag", "Location", "Retry-After"],
    )
    app.add_middleware(AuthenticationMiddleware, jwt_service=identity_factory.jwt_service)
    app.add_middleware(RequestContextMiddleware)
    install_exception_handlers(app)
    configure_openapi(app, service_name=resolved_settings.service_name)
    app.include_router(root_router)
    return app
