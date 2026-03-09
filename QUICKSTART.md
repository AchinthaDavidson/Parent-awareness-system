# QUICKSTART - Parent Dashboard Backend

## Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Groq API key
- Firebase service account key (`serviceAccountKey.json`)

## Installation

### Step 1: Navigate to the parentdashboard directory
```bash
cd parentdashboard
```

### Step 2: Install dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Configure environment
Edit the `.env` file and add your Groq API key:
```env
GROQ_API_KEY=your_actual_api_key_here
```

### Step 4: Setup Firebase credentials
Ensure `serviceAccountKey.json` is in the project root:
```
backend/
├── serviceAccountKey.json    # ← Must be here
└── parentdashboard/
    ├── main.py
    └── ...
```

If you don't have it:
1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Select your project
3. Go to Project Settings → Service Accounts
4. Click "Generate New Private Key"
5. Save as `serviceAccountKey.json` in the `backend/` folder

## Running the Server

### Option 1: Using Python directly
```bash
python main.py
```

### Option 2: Using the startup script (Windows)
```bash
start_server.bat
```

The server will start on **http://localhost:8000**

## Testing the API

### 1. Open API Documentation
Visit: http://localhost:8000/docs

### 2. Test Health Endpoint
```bash
curl http://localhost:8000/parentdashboard/health
```

Expected response:
```json
{"status": "healthy", "service": "Parent Dashboard AI Assistant"}
```

### 3. Ask a Question
```bash
curl -X POST "http://localhost:8000/parentdashboard/ask" \
  -H "Content-Type: application/json" \
  -d '{"question": "What are speech sound disorders?", "child_id": ""}'
```

### 4. Get Child Progress
```bash
curl "http://localhost:8000/parentdashboard/speech-progress?child_id=child_001"
```

### 5. List PDFs
```bash
curl http://localhost:8000/parentdashboard/pdfs
```

### 6. Upload a PDF
```bash
curl -X POST "http://localhost:8000/parentdashboard/pdfs/upload" \
  -F "file=@path/to/your/file.pdf"
```

## Default Configuration

- **Server Port**: 8000
- **Database**: ChromaDB (persistent in `chroma_db/`)
- **Firebase**: Firestore (via `serviceAccountKey.json`)
- **LLM**: Groq with `llama-3.3-70b-versatile`
- **Languages**: Sinhala + English bilingual

## Common Issues

### Port already in use
If port 8000 is already in use, edit `main.py` and change the port number in line 67.

### GROQ_API_KEY error
Make sure:
1. The `.env` file exists in the `parentdashboard` directory
2. The API key is correctly formatted
3. There are no extra spaces in the `.env` file

### Firebase initialization error
Check that:
1. `serviceAccountKey.json` exists at `backend/serviceAccountKey.json`
2. The file has valid JSON content
3. Your Firebase project has Firestore enabled

### ChromaDB errors
If you get database errors:
```bash
# Delete Chroma DB and restart
rm -rf chroma_db/
python main.py
```
The system will recreate the database automatically.

### No PDFs showing
Upload PDFs using:
1. API endpoint: `/parentdashboard/pdfs/upload`
2. Or manually place them in `parentdashboard/data/pdfs/` folder
3. Then call `/parentdashboard/reload` to refresh

## Next Steps

1. Review the full [README.md](README.md) for detailed documentation
2. Check the API documentation at http://localhost:8000/docs
3. Explore the RAG pipeline in `rag/` directory
4. Customize prompts in `ai/prompt.py`
5. Adjust configuration in `config.py`

## Available Endpoints Summary

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/parentdashboard/health` | Health check |
| POST | `/parentdashboard/ask` | Ask AI a question |
| GET | `/parentdashboard/speech-progress` | Get speech stats |
| GET | `/parentdashboard/child-summary` | Get child summary |
| GET | `/parentdashboard/child-stats/{child_id}` | Detailed stats |
| GET | `/parentdashboard/pdfs` | List all PDFs |
| POST | `/parentdashboard/pdfs/upload` | Upload PDF |
| PUT | `/parentdashboard/pdfs/update` | Rename PDF |
| DELETE | `/parentdashboard/pdfs/delete` | Delete PDF |
| POST | `/parentdashboard/reload` | Reload knowledge base |

## Support

For issues or questions, refer to:
- API Documentation: http://localhost:8000/docs
- Full README: [README.md](README.md)
- Check server logs for detailed error messages
