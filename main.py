"""
FastAPI main entry point for Parent Dashboard backend.
Standalone service for AI-powered parent dashboard with RAG-based Q&A.
"""
import os
import sys
from pathlib import Path

# Ensure the backend directory is in Python path for imports
BACKEND_DIR = Path(__file__).parent.absolute()
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

# ---- LOAD .env EARLY ----
try:
    from dotenv import load_dotenv
    load_dotenv(dotenv_path=BACKEND_DIR / ".env", override=False)
except Exception as e:
    print(f"[WARN] Could not load .env: {e}")

# Optional: quick sanity check
if not os.getenv("GROQ_API_KEY"):
    print("[WARN] GROQ_API_KEY is not set. Check your .env location and format.")

from fastapi import FastAPI
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
from api.routes import router as dashboard_router

# Initialize FastAPI app
app = FastAPI(
    title="Parent Dashboard API",
    description="AI Assistant API for Parent Dashboard using RAG with Groq LLM",
    version="1.0.0"
)

# Configure CORS for Flutter frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(dashboard_router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Parent Dashboard API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/favicon.ico")
async def favicon():
    """Favicon endpoint to prevent 404 errors in logs."""
    return Response(status_code=204)


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
