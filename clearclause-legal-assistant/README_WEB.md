# ClearClause Legal AI Assistant - Web Version

## 📌 Overview

This is the web-based version of ClearClause, converted from Streamlit to work with a modern frontend.

## 🎯 Features

- **Document Analysis**: Upload PDF/DOCX legal documents
- **AI Q&A**: Ask questions about your documents or general legal queries
- **Smart Summarization**: Generate custom summaries with specific instructions
- **Translation**: Translate legal text to Hindi or Marathi
- **Chat Interface**: Beautiful, interactive chat UI

## 🛠️ Tech Stack

**Backend:**

- FastAPI (Python)
- Google Gemini API
- LangChain
- FAISS Vector Store
- PyMuPDF, python-docx

**Frontend:**

- HTML5, CSS3, JavaScript
- Modern responsive design
- Real-time chat interface

## 📁 Structure

```
clearclause-legal-assistant/
├── backend/
│   ├── main.py              # FastAPI server
│   ├── legal_processor.py   # Document processing logic
│   └── requirements.txt     # Python dependencies
├── frontend/
│   └── index.html          # Web interface
├── .env                     # API keys (create this)
└── README.md
```

## 🚀 Setup & Run

### 1. Install Backend Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Create .env file

Create a `.env` file in the root directory:

```
API_KEY=your_google_gemini_api_key_here
```

### 3. Start Backend Server

```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8001
```

### 4. Open Frontend

Open `frontend/index.html` in your browser or serve it:

```bash
# Using Python's built-in server
cd frontend
python -m http.server 8080
```

Then visit: `http://localhost:8080`

## 🔑 Get Gemini API Key

Get your free API key from [Google AI Studio](https://aistudio.google.com/)

## 📊 API Endpoints

- `POST /api/upload` - Upload and process documents
- `POST /api/ask` - Ask questions (document or general)
- `POST /api/summarize` - Generate custom summary
- `POST /api/translate` - Translate text
- `GET /api/health` - Health check

## 🎨 Features Comparison

| Feature           | Streamlit Version | Web Version |
| ----------------- | ----------------- | ----------- |
| Document Upload   | ✅                | ✅          |
| PDF/DOCX Support  | ✅                | ✅          |
| AI Q&A            | ✅                | ✅          |
| Summarization     | ✅                | ✅          |
| Translation       | ✅                | ✅          |
| Chat History      | ✅                | ✅          |
| Modern UI         | ⚠️ Basic          | ✅ Advanced |
| Mobile Responsive | ⚠️ Limited        | ✅ Full     |
| API Access        | ❌                | ✅          |

## 📝 Usage

1. **Upload Documents**: Click "Upload Document" and select PDF/DOCX files
2. **Ask Questions**: Type questions in the chat input
3. **Generate Summary**: Use the summary panel with custom instructions
4. **Translate**: Switch to translate tab for multilingual support

## 🔒 Security Note

Never commit your `.env` file with API keys to Git!
