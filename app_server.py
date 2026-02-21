import asyncio
import json
from pathlib import Path

import uvicorn
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from sse_starlette.sse import EventSourceResponse

from core.agent_router import AgentRouter
from core.config import APP_ENV, DOCS_DIR, LLM_PROVIDER

app = FastAPI(title="Agentic RAG", version="2.0.0")

# Mount static files for UI
BASE_DIR = Path(__file__).parent
app.mount("/ui", StaticFiles(directory=BASE_DIR / "ui"), name="ui")

router = AgentRouter()


@app.get("/")
async def get_index():
    """Serve the main UI."""
    index_path = BASE_DIR / "ui" / "index.html"
    return HTMLResponse(index_path.read_text())


@app.get("/health")
async def health_check():
    """System health and configuration info for the UI status bar."""
    return JSONResponse(
        {
            "status": "ok",
            "provider": LLM_PROVIDER,
            "environment": APP_ENV,
        }
    )


@app.get("/stream_query")
async def stream_query(q: str):
    """
    SSE Endpoint that streams the agent workflow steps to the UI.
    """

    async def event_generator():
        try:
            async for event in router.process_query(q):
                yield json.dumps(event)
                await asyncio.sleep(0.05)
        except Exception as e:
            yield json.dumps({"step": "error", "message": str(e)})

    return EventSourceResponse(event_generator())


@app.post("/upload_document")
async def upload_document(file: UploadFile = File(...)):
    """
    Upload a document to the knowledge base.
    Files are saved to data/documents/ for future ingestion.
    """
    try:
        # Ensure documents directory exists
        DOCS_DIR.mkdir(parents=True, exist_ok=True)

        # Save file
        dest = DOCS_DIR / file.filename
        with open(dest, "wb") as f:
            content = await file.read()
            f.write(content)

        return JSONResponse(
            {
                "status": "success",
                "filename": file.filename,
                "size": len(content),
                "message": f"File '{file.filename}' uploaded. Run ingestion to index it.",
            }
        )
    except Exception as e:
        return JSONResponse({"status": "error", "message": str(e)}, status_code=500)


@app.get("/documents")
async def list_documents():
    """List all documents in the knowledge base."""
    try:
        DOCS_DIR.mkdir(parents=True, exist_ok=True)
        docs = []
        for f in DOCS_DIR.iterdir():
            if f.is_file() and not f.name.startswith("."):
                stat = f.stat()
                docs.append(
                    {
                        "name": f.name,
                        "size": stat.st_size,
                        "modified": stat.st_mtime,
                    }
                )
        return JSONResponse({"documents": docs})
    except Exception as e:
        return JSONResponse({"status": "error", "message": str(e)}, status_code=500)


@app.delete("/documents/{filename}")
async def delete_document(filename: str):
    """Delete a document from the knowledge base."""
    try:
        file_path = DOCS_DIR / filename
        if file_path.exists():
            file_path.unlink()
            return JSONResponse({"status": "success", "message": f"Deleted {filename}"})
        return JSONResponse(
            {"status": "error", "message": f"File {filename} not found"},
            status_code=404,
        )
    except Exception as e:
        return JSONResponse({"status": "error", "message": str(e)}, status_code=500)


if __name__ == "__main__":
    print("=" * 50)
    print("  Agentic RAG v2.0 — Starting Server")
    print(f"  Provider: {LLM_PROVIDER} | Environment: {APP_ENV}")
    print("  UI: http://localhost:8000")
    print("=" * 50)
    uvicorn.run("app_server:app", host="0.0.0.0", port=8000, reload=True)
