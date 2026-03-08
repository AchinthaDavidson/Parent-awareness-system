# Quick Start Guide

## 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

## 2. Set Up Groq API Key

1. Get your API key from: https://console.groq.com/
2. Edit `.env` file and replace `your_groq_api_key_here` with your actual key:
   ```
   GROQ_API_KEY=gsk_your_actual_key_here
   ```

## 3. Add PDFs to Knowledge Base

Place your PDF files in: `backend/parentdashboard/data/pdfs/`

The PDFs should contain information about:
- Phonological issues
- Speech therapy techniques
- Child speech development guidance

## 4. Run the Backend

```bash
python main.py
```

The API will start at: http://localhost:8000

- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/parentdashboard/health

## 5. Test the API

You can test using the interactive docs at http://localhost:8000/docs or use curl:

```bash
curl -X POST "http://localhost:8000/parentdashboard/ask" \
  -H "Content-Type: application/json" \
  -d '{"question": "How can I help my child with speech therapy?"}'
```

## 6. Run Flutter Frontend

In a separate terminal:

```bash
cd ../vocaBuddy-flutter-frontend
flutter pub get
flutter run -d chrome
```

The frontend is configured to connect to `http://localhost:8000` by default.

## Troubleshooting

- **"GROQ_API_KEY not found"**: Make sure `.env` file exists and has your API key
- **"No PDFs found"**: Add PDF files to `backend/parentdashboard/data/pdfs/`
- **Connection errors**: Make sure backend is running on port 8000
- **Import errors**: Run `pip install -r requirements.txt` again

## Reload Knowledge Base

After adding new PDFs, call:
```bash
curl -X POST "http://localhost:8000/parentdashboard/reload"
```

Or restart the server.

