from fastapi import APIRouter

from app.services.neo4j_service import neo4j_service

router = APIRouter(prefix="/health", tags=["health"])


@router.get("")
def health() -> dict:
    try:
        neo4j_service.verify()
        return {"status": "ok"}
    except Exception as exc:
        return {"status": "degraded", "detail": str(exc)}
