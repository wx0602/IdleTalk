"""FastAPI application entry point."""

from __future__ import annotations

from fastapi import FastAPI

from app.api.chat import router as chat_router

app = FastAPI(
    title="Wang Zengqi Multi-Agent System",
    version="0.1.0",
    description="A lightweight multi-agent literary persona backend.",
)

app.include_router(chat_router)


@app.get("/")
def root() -> dict[str, str]:
    """Simple root endpoint for service check."""
    return {"message": "Wang Zengqi multi-agent backend is running."}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
