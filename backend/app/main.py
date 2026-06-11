from fastapi import FastAPI

from backend.app.api.auth import router as auth_router
from backend.app.api.posts import router as posts_router

app = FastAPI(
    title="AI Development Q&A Board API",
    version="0.1.0",
)

app.include_router(auth_router, prefix="/api")
app.include_router(posts_router, prefix="/api")


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}
