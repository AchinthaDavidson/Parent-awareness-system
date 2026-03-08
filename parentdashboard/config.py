"""
Configuration module for Parent Dashboard backend.
Handles environment variables and settings.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
# Use file-based path resolution to work from any IDE or terminal
BASE_DIR_FOR_ENV = Path(__file__).parent.parent
ENV_FILE = BASE_DIR_FOR_ENV / ".env"

# Try loading from explicit path first, then fallback to default behavior
if ENV_FILE.exists():
    load_dotenv(dotenv_path=ENV_FILE)
else:
    # Fallback: try loading from current directory or parent directories
    load_dotenv()

# Base directory
BASE_DIR = Path(__file__).parent.parent

# PDFs directory
PDFS_DIR = BASE_DIR / "parentdashboard" / "data" / "pdfs"

# Chroma DB directory
CHROMA_DB_DIR = BASE_DIR / "chroma_db"

# API Configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    env_file_path = ENV_FILE.absolute()
    raise ValueError(
        f"GROQ_API_KEY not found in environment variables.\n"
        f"Please create a .env file at: {env_file_path}\n"
        f"Add your Groq API key: GROQ_API_KEY=your_api_key_here\n"
        f"Get your API key from: https://console.groq.com/"
    )

# Groq LLM Configuration
GROQ_MODEL = "llama-3.3-70b-versatile"  # Updated to current Groq model (supports Sinhala)
GROQ_TEMPERATURE = 0.7
GROQ_MAX_TOKENS = 1500  # Increased for longer Sinhala responses

# RAG Configuration
CHUNK_SIZE = 1000  # Characters per chunk
CHUNK_OVERLAP = 200  # Overlap between chunks
EMBEDDING_MODEL = "intfloat/multilingual-e5-large"  # Multilingual model supporting Sinhala + English
TOP_K_RETRIEVAL = 5  # Increased to get more context for better answers

# Ensure directories exist
PDFS_DIR.mkdir(parents=True, exist_ok=True)
CHROMA_DB_DIR.mkdir(parents=True, exist_ok=True)

