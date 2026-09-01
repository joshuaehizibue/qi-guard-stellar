from fastapi import APIRouter
from app.api.v1.analyze import router as analyze_router
from app.api.v1.resilience import router as resilience_router
from app.api.v1.benchmarks import router as benchmarks_router

api_router = APIRouter()
api_router.include_router(analyze_router, prefix="/analyze", tags=["Analyze"])
api_router.include_router(resilience_router, prefix="/resilience", tags=["Resilience"])
api_router.include_router(benchmarks_router, prefix="/benchmarks", tags=["Benchmarks"])
