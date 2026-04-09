from fastapi import APIRouter

from app.models.schemas import ChatResponse, PromptRequest
from app.services.agent_service import agent_service

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/draft-cypher", response_model=ChatResponse)
def draft_cypher(payload: PromptRequest) -> ChatResponse:
    cypher, explanation = agent_service.draft_cypher(payload.prompt)
    return ChatResponse(cypher=cypher, explanation=explanation)
