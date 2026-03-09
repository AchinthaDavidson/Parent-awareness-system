# Parent Dashboard Backend

Standalone FastAPI backend for AI-powered parent dashboard with RAG-based Q&A system.

## Features

- **AI-Powered Q&A**: Answer parent questions using RAG (Retrieval Augmented Generation) with Groq LLM
- **Multi-language Support**: Bilingual support for Sinhala and English
- **PDF Knowledge Base**: Upload, manage, and query speech therapy PDF documents
- **Child Progress Analytics**: Track speech accuracy, weekly trends, and session performance
- **Firebase Integration**: Real-time data from Firestore for child sessions and practice records
- **Vector Search**: ChromaDB-based semantic search over PDF content
- **Background Processing**: Async PDF upload and processing

## Project Structure

```
parentdashboard/
├── ai/
│   ├── llm.py                 # Groq LLM client
│   └── prompt.py              # Prompt engineering & language detection
├── api/
│   └── routes.py              # FastAPI endpoints
├── data/
│   ├── pdfs/                  # PDF knowledge base files
│   └── firebase_client.py     # Firebase/Firestore initialization
├── rag/
│   ├── chunker.py             # Text chunking for RAG
│   ├── embeddings.py          # Embedding model wrapper
│   ├── loader.py              # PDF loader
│   ├── rag_pipeline.py        # Complete RAG workflow
│   ├── retriever.py           # Vector retrieval logic
│   └── vector_store.py        # ChromaDB vector store
├── schemas/
│   ├── request.py             # Pydantic request models
│   ├── response.py            # Pydantic response models
│   └── speech_stats.py        # Speech statistics schemas
├── services/
│   ├── qa_service.py          # Q&A business logic
│   ├── service.py             # Speech stats & Firestore operations
│   └── weekly_chart.py        # Weekly trend calculation
├── config.py                  # Configuration & environment settings
├── main.py                    # FastAPI application entry point
├── requirements.txt           # Python dependencies
└── .env                       # Environment variables
```

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- Firebase service account key (`serviceAccountKey.json`)
- Groq API key

### 1. Install Dependencies

```bash
cd parentdashboard
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create a `.env` file in the `parentdashboard` directory:

```env
GROQ_API_KEY=your_groq_api_key_here
```

### 3. Setup Firebase

Ensure `serviceAccountKey.json` is located in the project root (one level above `parentdashboard/`):

```
backend/
├── serviceAccountKey.json    # Firebase credentials
└── parentdashboard/
    ├── main.py
    └── ...
```

### 4. Run the Server

```bash
python main.py
```

Or use the startup script (Windows):

```bash
start_server.bat
```

The API will be available at **http://localhost:8000**

API documentation: **http://localhost:8000/docs**

## API Endpoints

### Root & Health

- **GET /** - API info and version
- **GET /parentdashboard/health** - Service health status

### AI Q&A

- **POST /parentdashboard/ask** - Ask a question to the AI assistant
  ```json
  {
    "question": "What are speech sound disorders?",
    "child_id": "optional_child_uid"
  }
  ```

### Child Analytics

- **GET /parentdashboard/speech-progress** - Get speech accuracy statistics
- **GET /parentdashboard/child-summary** - Get high-level child progress summary
- **GET /parentdashboard/child-stats/{child_id}** - Get detailed dashboard statistics

### PDF Management

- **GET /parentdashboard/pdfs** - List all PDF files
- **POST /parentdashboard/pdfs/upload** - Upload a PDF file (async processing)
- **PUT /parentdashboard/pdfs/update** - Rename a PDF file
- **DELETE /parentdashboard/pdfs/delete?file_name=...** - Delete a PDF
- **POST /parentdashboard/reload** - Reload entire knowledge base

## Key Components

### RAG Pipeline

The Retrieval-Augmented Generation pipeline:

1. **Load**: PDFs are loaded from `data/pdfs/`
2. **Chunk**: Text is split into chunks (1000 chars, 200 overlap)
3. **Embed**: Chunks are embedded using multilingual model
4. **Store**: Vectors stored in ChromaDB
5. **Retrieve**: Top-k relevant chunks retrieved for queries
6. **Generate**: LLM generates answers using context + general knowledge

### Configuration (config.py)

- **Model**: `llama-3.3-70b-versatile` (supports Sinhala)
- **Embedding**: `intfloat/multilingual-e5-large`
- **Chunk Size**: 1000 characters
- **Top-K Retrieval**: 5 chunks
- **ChromaDB**: Persistent storage in `chroma_db/`

### Firebase Integration

Reads from Firestore path:
```
users/{child_user_id}/sessions/{sessionId}/practice/{practiceId}/attempts
```

Each attempt contains:
- `word`: Sinhala word practiced
- `status`: "success", "wrong", or "pending"
- `created_at`: Timestamp

### Child Analytics

The system calculates:

1. **Overall Accuracy**: Percentage of correct words (last 8 sessions)
2. **Weekly Progress**: Week-by-week accuracy trends (last 4 weeks)
3. **Target Sounds**: Letters practiced in recent sessions
4. **Monthly Practice Count**: Sessions in current month
5. **Word Category Progress**: Per-session accuracy bars (last 30 days)

## Caching Strategy

### In-Memory Caches

1. **Child Summary Cache**: 90 seconds TTL, invalidated on DB changes
2. **Dashboard Stats Cache**: 90 seconds TTL, checks `latest_activity_timestamp`
3. **Child Summary for AI**: 120 seconds TTL, used for personalization

Caches automatically invalidate when new sessions/practices are detected.

## Language Detection

Automatic detection between Sinhala and English:

- Detects query language
- Routes to appropriate prompt templates
- Returns responses in the same language
- Error messages also bilingual

## PDF Processing

### Upload Flow

1. File uploaded via POST
2. Saved immediately to `data/pdfs/`
3. Background task processes PDF asynchronously
4. User gets immediate response
5. PDF added to vector store without full reload

### Supported Operations

- **Upload**: Add new PDFs
- **Rename**: Update PDF names
- **Delete**: Remove PDFs from disk and vector store
- **Reload**: Full knowledge base refresh

## Response Models

### SpeechStatsResponse
```json
{
  "overall_accuracy": 75.5,
  "total_words": 100,
  "total_correct": 75,
  "phoneme_breakdown": [],
  "weekly_progress": [
    {"date": "04 Feb", "accuracy": 80.0, "total_words": 20, "correct_words": 16}
  ]
}
```

### ChildSummaryResponse
```json
{
  "id": "child_001",
  "name": "Child Name",
  "age": 5,
  "overall_accuracy": 75.5,
  "monthly_practice_count": 12,
  "target_sounds": ["ක", "ග", "ත"]
}
```

## Troubleshooting

### GROQ_API_KEY Error

Ensure:
1. `.env` file exists in `parentdashboard/`
2. API key is correctly formatted
3. No extra spaces or quotes

### Firebase Connection Error

Check:
1. `serviceAccountKey.json` exists at project root
2. Firebase Admin SDK installed: `pip install firebase-admin`
3. Service account has proper permissions

### ChromaDB Issues

If vector store fails:
1. Delete `chroma_db/` directory
2. Restart server (will recreate)
3. Re-upload PDFs or use `/reload` endpoint

### Port Already in Use

If port 8000 is occupied:
1. Edit `main.py` line 67
2. Change port number: `uvicorn.run(app, host="0.0.0.0", port=8001)`

## Testing

### Quick Health Check

```bash
curl http://localhost:8000/parentdashboard/health
```

### Test AI Question

```bash
curl -X POST "http://localhost:8000/parentdashboard/ask" \
  -H "Content-Type: application/json" \
  -d '{"question": "What is phonological awareness?"}'
```

### List PDFs

```bash
curl http://localhost:8000/parentdashboard/pdfs
```

## Performance Notes

- **First Load**: Initial PDF loading may take time (normal)
- **Subsequent Loads**: ChromaDB persists vectors (fast startup)
- **Background Tasks**: PDF uploads don't block API
- **Cache Hits**: Repeat queries served from memory (90s TTL)
- **Firestore Reads**: Minimized with caching and batch reads

## Production Considerations

### Security

- Replace `allow_origins=["*"]` with specific frontend URL
- Implement Firebase Authentication
- Validate user permissions for child data access
- Sanitize file uploads more strictly

### Scalability

- Move ChromaDB to persistent storage (e.g., PostgreSQL with pgvector)
- Use Redis for distributed caching
- Implement rate limiting
- Add request logging and monitoring

### Monitoring

- Add structured logging
- Track API response times
- Monitor Firestore read/write costs
- Set up error alerting

## Development

### Running Tests

Tests are located in `tests/` directory (if available).

### Code Style

- Type hints throughout codebase
- Docstrings for all public methods
- Protocol-based repository pattern
- Service/repository separation

## License

[Your License Here]

## Support

For issues or questions:
- API Documentation: http://localhost:8000/docs
- Check logs for detailed error messages
- Review Firebase console for database issues
