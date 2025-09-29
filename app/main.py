from fastapi import APIRouter, FastAPI

from . import VERSION
from .routers import about, default

app = FastAPI(
    title="Safe Queue Service",
    description="Service for handling offchain Safe Multisig Transactions",
    version=VERSION,
    docs_url=None,
    redoc_url=None,
)

# Router configuration
api_v1_router = APIRouter(
    prefix="/api/v1",
)
api_v1_router.include_router(about.router)
app.include_router(api_v1_router)
app.include_router(default.router)
