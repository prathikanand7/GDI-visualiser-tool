# GDI visualiser tool

FastAPI + React app for exploring a Neo4j graph in two ways:
1. write Cypher directly and render the graph, or
2. type natural language, get a drafted Cypher query, then render it.

---

## What this app does

- Connects to Neo4j from a Python backend.
- Exposes API routes to:
  - check health,
  - fetch graph schema metadata,
  - execute a graph query,
  - draft Cypher from natural language.
- Uses a React frontend to:
  - show a chat input (NL → Cypher),
  - show/edit Cypher text,
  - call backend APIs,
  - visualize nodes/relationships with `react-force-graph`.

---

## Project structure

- `backend` — FastAPI backend + Neo4j services
- `frontend` — React + Vite frontend
- `docs` — architecture notes

---

## Full flow (exact runtime behavior)

### 0) Process startup

#### Backend startup (`backend/app/main.py`)
1. FastAPI app starts with a lifespan hook.
2. On startup, `neo4j_service.verify()` runs immediately.
	- If Neo4j is unreachable/invalid, startup fails.
3. CORS allows requests from `http://localhost:5173`.
4. Routers are mounted: `/health`, `/graph`, `/chat`.
5. On shutdown, `neo4j_service.close()` closes the Neo4j driver.

#### Frontend startup (`frontend/src/main.tsx`, `App.tsx`)
1. React mounts `App`.
2. `App` initializes state:
	- default Cypher: `MATCH (n)-[r]-(m) RETURN n, r, m LIMIT 100`
	- empty prompt/explanation/error
	- empty graph payload (`nodes`, `relationships`, `rows`)
3. On first render, `fetchSchema()` is called.
4. UI schema text becomes:
	- success: `X labels • Y rel-types`
	- failure: `schema unavailable`

---

### 1) Health check flow

1. Client hits `GET /health`.
2. Route calls `neo4j_service.verify()`.
3. Returns `{ "status": "ok" }` if Neo4j connectivity is valid.

---

### 2) Schema load flow (`GET /graph/schema`)

1. Frontend calls `/graph/schema`.
2. Backend executes three read queries:
	- labels: `CALL db.labels()`
	- relationship types: `CALL db.relationshipTypes()`
	- property keys: `CALL db.propertyKeys()`
3. Response shape:
	```json
	{
	  "labels": ["..."],
	  "relationshipTypes": ["..."],
	  "propertyKeys": ["..."]
	}
	```
4. Frontend only displays label/relationship counts in the header line.

---

### 3) Natural language → Cypher draft flow (`POST /chat/draft-cypher`)

1. User types in `ChatPanel` and clicks **Draft Cypher**.
2. Frontend calls `/chat/draft-cypher` with:
	```json
	{ "prompt": "..." }
	```
3. Pydantic validates `prompt` with `min_length=1`.
4. `AgentService.draft_cypher(prompt)` runs:
	- fetches labels from Neo4j for context,
	- rule-maps prompt text:
	  - contains `call` or `dependency` → `MATCH (n)-[r:CppCalls]->(m) RETURN n, r, m LIMIT 100`
	  - contains `folder` → `MATCH (n:Folder)-[r:ParentFolder]->(m:Folder) RETURN n, r, m LIMIT 100`
	  - otherwise generic fallback → `MATCH (n)-[r]-(m) RETURN n, r, m LIMIT 100`
	- appends up to 8 detected labels to the explanation.
5. Backend returns:
	```json
	{
	  "cypher": "...",
	  "explanation": "..."
	}
	```
6. Frontend behavior:
	- replaces the Cypher editor content with drafted Cypher,
	- displays explanation text under chat,
	- does **not** auto-run query; user must click **Render Graph**.

---

### 4) Query execution and graph rendering flow (`POST /graph/query`)

1. User clicks **Render Graph** in `QueryPanel`.
2. Frontend calls `/graph/query` with:
	```json
	{ "cypher": "...", "limit": 200 }
	```
3. Pydantic validates:
	- `cypher` must be non-empty,
	- `limit` defaults to `200`, min `1`, max `2000`.
4. Backend route behavior:
	- trims `cypher`,
	- if query text does not include `limit` (case-insensitive), appends `LIMIT {payload.limit}`.
5. `Neo4jService.run_graph(cypher)` executes:
	- guardrail check blocks write-like prefixes when `allow_write_queries=false`:
	  - `create`, `merge`, `delete`, `set`, `drop`, `remove`, `call dbms`, `call apoc.periodic`
	- runs query in configured Neo4j database,
	- iterates over every returned value in every record,
	- extracts:
	  - nodes (by `element_id`, labels, properties),
	  - relationships (id, type, source element id, target element id, properties),
	- de-duplicates via maps keyed by `element_id`.
6. Route returns:
	```json
	{
	  "nodes": [ ... ],
	  "relationships": [ ... ],
	  "rows": <relationship_count>
	}
	```
	Note: `rows` is currently set to `len(relationships)`.
7. Frontend sets graph state and renders with `react-force-graph`:
	- node label tooltip: first label + `name|label|id`
	- link label tooltip: relationship type
	- node color groups by first label
	- canvas text draws `name|label|id` on each node

---

### 5) Error flow (frontend + backend)

- Frontend actions (`Draft Cypher`, `Render Graph`) set `loading=true`, clear old error, then restore `loading=false` in `finally`.
- If request fails, frontend displays:
  - server error message if present,
  - fallback `Draft failed` or `Query failed`.
- `/graph/query` catches exceptions and returns HTTP 400 with exception detail.

---

## Data contracts

- `POST /chat/draft-cypher`
  - request: `{ prompt: string }`
  - response: `{ cypher: string, explanation: string }`

- `POST /graph/query`
  - request: `{ cypher: string, limit?: number }`
  - response: `{ nodes: object[], relationships: object[], rows: number }`

- `GET /graph/schema`
  - response: `{ labels: string[], relationshipTypes: string[], propertyKeys: string[] }`

---

## Configuration

Backend settings (`backend/app/config.py`) come from environment / `.env`:

- `neo4j_uri` (default: `bolt://localhost:7687`)
- `neo4j_user` (default: `neo4j`)
- `neo4j_password` (default: empty)
- `neo4j_database` (default: `neo4j`)
- `allow_write_queries` (default: `false`)
- `llm_provider` (default: `mock`)
- `llm_api_key` (default: empty)

---

## Run locally

### Backend
```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Frontend
```powershell
cd frontend
npm install
npm run dev
```

Open: `http://localhost:5173`

---

## One-command helper

From repo root:
```powershell
.\run-all.ps1
```

This opens two PowerShell windows:
- backend: creates venv, installs requirements, runs uvicorn
- frontend: installs npm packages, runs Vite dev server

---

## MCP / production note

`AgentService` is rule-based and intentionally simple. It is structured so you can swap in an LLM + tool-calling layer (including MCP-compatible tools) without changing frontend UX or route contracts.
