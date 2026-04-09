from __future__ import annotations

from neo4j.exceptions import ServiceUnavailable

from app.services.neo4j_service import neo4j_service


class AgentService:
    def draft_cypher(self, prompt: str) -> tuple[str, str]:
        labels: list[str] = []
        try:
            schema = neo4j_service.run_table(
                "CALL db.labels() YIELD label RETURN collect(label) AS labels"
            )
            labels = schema[0]["labels"] if schema else []
        except ServiceUnavailable:
            labels = []

        prompt_lower = prompt.lower()
        if "call" in prompt_lower or "dependency" in prompt_lower:
            cypher = "MATCH (n)-[r:CppCalls]->(m) RETURN n, r, m LIMIT 100"
            explanation = "Mapped your prompt to a call/dependency relationship graph."
        elif "folder" in prompt_lower:
            cypher = "MATCH (n:Folder)-[r:ParentFolder]->(m:Folder) RETURN n, r, m LIMIT 100"
            explanation = "Mapped your prompt to folder hierarchy relationships."
        else:
            cypher = "MATCH (n)-[r]-(m) RETURN n, r, m LIMIT 100"
            explanation = (
                "Using a generic graph query. Replace with LLM tool-calling in production "
                "(GitHub Models/OpenAI/Azure OpenAI + MCP tools)."
            )

        if labels:
            explanation += f" Detected labels: {', '.join(labels[:8])}."

        return cypher, explanation


agent_service = AgentService()
