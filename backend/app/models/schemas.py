from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    cypher: str = Field(min_length=1)
    limit: int = Field(default=200, ge=1, le=2000)


class PromptRequest(BaseModel):
    prompt: str = Field(min_length=1)


class ChatResponse(BaseModel):
    cypher: str
    explanation: str


class GraphResponse(BaseModel):
    nodes: list[dict]
    relationships: list[dict]
    rows: int
