from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.chat import router as chat_router
from app.routes.graph import router as graph_router
from app.routes.health import router as health_router
from app.services.neo4j_service import neo4j_service


@asynccontextmanager
async def lifespan(_: FastAPI):
    try:
        neo4j_service.verify()
    except Exception as exc:
        print(f"WARNING: Neo4j connectivity check failed during startup: {exc}")
    yield
    neo4j_service.close()


app = FastAPI(title="GDI visualiser tool API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_origin_regex=r"http://(localhost|127\.0\.0\.1):517\d",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(graph_router)
app.include_router(chat_router)


@app.get("/")
def root() -> dict:
    return {"name": "GDI visualiser tool API", "status": "running"}
