from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from src.api.router import router as api_router
from src.settings import app_settings


def create_app() -> FastAPI:
    app = FastAPI(
        title='fastapi-app',
        default_response_class=ORJSONResponse,
        swagger_ui_parameters={'defaultModelsExpandDepth': -1},
        docs_url='/docs' if app_settings.environment == 'development' else None,
        redoc_url='/redoc' if app_settings.environment == 'development' else None,
        openapi_url='/openapi.json' if app_settings.environment == 'development' else None,
    )
    app.include_router(api_router)

    return app
