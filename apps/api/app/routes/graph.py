from fastapi import APIRouter, HTTPException

from app.models.schemas import GraphResponse, QueryRequest
from app.services.neo4j_service import neo4j_service

router = APIRouter(prefix="/graph", tags=["graph"])


@router.post("/query", response_model=GraphResponse)
def graph_query(payload: QueryRequest) -> GraphResponse:
    cypher = payload.cypher.strip()
    if "limit" not in cypher.lower():
        cypher = f"{cypher}\nLIMIT {payload.limit}"

    try:
        nodes, relationships = neo4j_service.run_graph(cypher)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return GraphResponse(nodes=nodes, relationships=relationships, rows=len(relationships))


@router.get("/schema")
def schema() -> dict:
    labels = neo4j_service.run_table(
        "CALL db.labels() YIELD label RETURN label ORDER BY label"
    )
    rels = neo4j_service.run_table(
        "CALL db.relationshipTypes() YIELD relationshipType RETURN relationshipType ORDER BY relationshipType"
    )
    props = neo4j_service.run_table(
        "CALL db.propertyKeys() YIELD propertyKey RETURN propertyKey ORDER BY propertyKey"
    )

    return {
        "labels": [row["label"] for row in labels],
        "relationshipTypes": [row["relationshipType"] for row in rels],
        "propertyKeys": [row["propertyKey"] for row in props],
    }
