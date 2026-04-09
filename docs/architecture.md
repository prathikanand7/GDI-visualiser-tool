# GDI visualiser tool architecture

## Purpose

This system lets users explore a Neo4j graph through:
- direct Cypher execution, and
- natural language drafting of Cypher, followed by manual execution.

It is intentionally split into a thin React client and a backend that owns all Neo4j access and query guardrails.

## System components

### Frontend (frontend)

- Framework: React + Vite
- API client: Axios with base URL http://localhost:8000
- UI modules:
	- ChatPanel: prompt input and draft trigger
	- QueryPanel: Cypher editor and run trigger
	- GraphPanel: graph visualization using react-force-graph

### Backend (backend)

- Framework: FastAPI
- Routes:
	- GET /health
	- GET /graph/schema
	- POST /graph/query
	- POST /chat/draft-cypher
- Services:
	- Neo4jService: connectivity, query guardrails, query execution, graph transformation
	- AgentService: rule-based NL → Cypher draft selection

### Data layer

- Neo4j over Bolt
- Configurable by environment: URI, user, password, database

## Startup lifecycle

1. FastAPI bootstraps with a lifespan hook.
2. On startup, Neo4j connectivity is verified once.
3. CORS allows frontend origin http://localhost:5173.
4. Routers are mounted.
5. On shutdown, the Neo4j driver is closed.

Frontend startup:
1. React mounts App.
2. App initializes default Cypher and empty graph state.
3. App immediately calls GET /graph/schema.
4. Header displays schema availability and basic counts.

## Request/response flow

### A) Schema metadata flow

Client action:
- App startup calls GET /graph/schema.

Backend processing:
- Executes:
	- CALL db.labels()
	- CALL db.relationshipTypes()
	- CALL db.propertyKeys()
- Returns normalized arrays: labels, relationshipTypes, propertyKeys.

Frontend result:
- Displays only label and relationship-type counts in the page subtitle.

### B) Natural language draft flow

Client action:
- User enters prompt in ChatPanel and clicks Draft Cypher.

Backend processing:
1. Pydantic validates non-empty prompt.
2. AgentService fetches current labels for context.
3. Prompt is mapped by simple rules:
	 - contains call or dependency → CppCalls query
	 - contains folder → folder hierarchy query
	 - else → generic graph query
4. Explanation is returned with up to 8 detected labels appended.

Frontend result:
- Cypher editor is replaced with drafted query.
- Explanation text is shown.
- Query is not auto-executed; user explicitly runs it.

### C) Graph query execution flow

Client action:
- User clicks Render Graph in QueryPanel.

Backend processing:
1. Pydantic validates:
	 - cypher non-empty
	 - limit in range 1..2000 (default 200)
2. If Cypher text has no LIMIT clause (case-insensitive), route appends LIMIT {limit}.
3. Neo4jService guardrails run:
	 - if allow_write_queries is false, block query prefixes:
		 create, merge, delete, set, drop, remove, call dbms, call apoc.periodic
4. Query executes in configured database.
5. Records are transformed into graph payload:
	 - node objects from Neo4j node values
	 - relationship objects from Neo4j relationship values
	 - deduplication by element_id maps
6. Response is returned as GraphResponse.

Frontend result:
- Graph state is updated.
- GraphPanel renders force graph:
	- node color grouped by first label
	- node label text from name, label, or id
	- link tooltip as relationship type

## Error handling behavior

Frontend:
- Both draft and run paths set loading state, clear previous errors, and restore loading in finally.
- Errors render as inline message text.

Backend:
- /graph/query wraps execution and returns HTTP 400 on exceptions with detail message.

## Security and guardrails

- Write queries are disabled by default via allow_write_queries=false.
- Neo4j credentials remain server-side only.
- CORS is explicitly scoped to local frontend dev origin.

## Current constraints and known behavior

- AgentService is deterministic rule-based logic, not an LLM.
- Graph extraction depends on records containing Neo4j Node/Relationship values.
- GraphResponse.rows currently reports relationship count from the response assembly path.

## MCP-ready agent evolution path

Current API contracts already support replacing AgentService with a tool-calling LLM orchestration layer.

Recommended MCP tool surface:
- neo4j.get_schema
- neo4j.validate_cypher
- neo4j.run_read_query

This keeps frontend UX unchanged while improving draft quality and safety checks.
