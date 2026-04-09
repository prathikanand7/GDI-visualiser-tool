from __future__ import annotations

from neo4j import GraphDatabase

from app.config import settings


WRITE_PREFIXES = (
    "create", "merge", "delete", "set", "drop", "remove", "call dbms", "call apoc.periodic",
)


class Neo4jService:
    def __init__(self) -> None:
        if settings.neo4j_password:
            self.driver = GraphDatabase.driver(
                settings.neo4j_uri,
                auth=(settings.neo4j_user, settings.neo4j_password),
            )
        else:
            self.driver = GraphDatabase.driver(settings.neo4j_uri)

    def close(self) -> None:
        self.driver.close()

    def verify(self) -> None:
        self.driver.verify_connectivity()

    def _guard_query(self, cypher: str) -> None:
        if settings.allow_write_queries:
            return
        normalized = cypher.strip().lower()
        if normalized.startswith(WRITE_PREFIXES):
            raise ValueError("Write queries are disabled. Use read-only Cypher.")

    def run_table(self, cypher: str, params: dict | None = None) -> list[dict]:
        self._guard_query(cypher)
        params = params or {}
        with self.driver.session(database=settings.neo4j_database) as session:
            return [record.data() for record in session.run(cypher, params)]

    def run_graph(self, cypher: str, params: dict | None = None) -> tuple[list[dict], list[dict]]:
        self._guard_query(cypher)
        params = params or {}
        node_map: dict[str, dict] = {}
        rel_map: dict[str, dict] = {}

        with self.driver.session(database=settings.neo4j_database) as session:
            records = list(session.run(cypher, params))

        for record in records:
            for value in record.values():
                if hasattr(value, "element_id") and hasattr(value, "labels"):
                    node_map[value.element_id] = {
                        "id": value.element_id,
                        "labels": list(value.labels),
                        "properties": dict(value.items()),
                    }
                elif hasattr(value, "element_id") and hasattr(value, "type") and hasattr(value, "start_node"):
                    rel_map[value.element_id] = {
                        "id": value.element_id,
                        "type": value.type,
                        "source": value.start_node.element_id,
                        "target": value.end_node.element_id,
                        "properties": dict(value.items()),
                    }

        return list(node_map.values()), list(rel_map.values())


neo4j_service = Neo4jService()
