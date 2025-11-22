# Local RAG Quick Start Guide (FREE - No AWS Needed!)

## 🎉 What We Built

A **fully local RAG system** that works **completely offline** (except for Gemini API calls, which are free tier):

✅ **Ingestion**: `rag_ingest.py` - Loads PDFs from `data/contracts/` into ChromaDB  
✅ **Query**: `rag_query.py` - Searches ChromaDB and generates answers with Gemini  
✅ **Backend API**: `/api/clearclause/local-rag-query` - FastAPI endpoint  
✅ **Frontend**: RAGPanel with toggle for Local vs AWS RAG  
✅ **Dependencies**: All added to `requirements.txt`

---

## 🚀 Quick Start (3 Steps)

### Step 1: Install Dependencies

```powershell
cd E:\fairscorec
pip install -r backend/requirements.txt
```

**New packages installed:**
- `chromadb` - Local vector database
- `sentence-transformers` - FREE embedding model (all-MiniLM-L6-v2)
- `pypdf` - PDF text extraction

**Note**: First run will download ~80MB embedding model (cached after that).

---

### Step 2: Ingest Your PDFs

Place your contract PDFs in `data/contracts/` folder, then run:

```powershell
python backend/app/utils/rag_ingest.py
```

**What it does:**
1. Scans `data/contracts/` for PDF files
2. Extracts text page by page
3. Splits into chunks (1000 chars, 200 overlap)
4. Creates embeddings using FREE local model
5. Stores in ChromaDB at `data/chroma_db/`

**Expected output:**
```
🚀 Local RAG Ingestion - FREE Version
============================================================
📂 Found 4 PDF file(s):
   - contract1.pdf
   - contract2.pdf
   ...

🗄️  Initializing ChromaDB...
   ✅ Created collection 'legal_contracts'

📖 Processing contract1.pdf...
   📄 Reading contract1.pdf...
      Extracted 5 pages
      Page 1: 3 chunk(s)
      ...

✅ Ingestion Complete!
   Total chunks stored: 45
```

**Troubleshooting:**
- No PDFs found? → Add PDFs to `data/contracts/` folder
- Import errors? → Run `pip install -r backend/requirements.txt` again

---

### Step 3: Test It!

#### Option A: Via Frontend (Recommended)

```powershell
# Terminal 1: Start backend
.\start_backend.ps1

# Terminal 2: Start frontend
.\start_frontend.ps1

# Open browser: http://localhost:5173
# Click "Contract Q&A" tab
# Make sure "🆓 Local RAG" toggle is ON (left side)
# Ask: "What is the notice period for cheque bounce?"
```

#### Option B: Via API (curl)

```powershell
curl -X POST http://localhost:8000/api/clearclause/local-rag-query `
  -H "Content-Type: application/json" `
  -d '{\"query\": \"What is the notice period for cheque bounce?\"}'
```

#### Option C: Via CLI (Interactive)

```powershell
python backend/app/utils/rag_query.py
```

Then type questions interactively!

---

## 📋 Prerequisites Checklist

Before starting, make sure you have:

- [ ] Python 3.8+ installed
- [ ] `GEMINI_API_KEY` set in `backend/.env` (or environment variable)
- [ ] At least one PDF file in `data/contracts/` folder
- [ ] Dependencies installed: `pip install -r backend/requirements.txt`

**Get Gemini API Key:**
1. Go to https://makersuite.google.com/app/apikey
2. Create new API key (FREE)
3. Add to `backend/.env`: `GEMINI_API_KEY=your_key_here`

---

## 🎯 How It Works

```
User Question
    ↓
Frontend (RAGPanel.tsx)
    ↓ POST /api/clearclause/local-rag-query
Backend (routes/clearclause.py)
    ↓ query_rag()
rag_query.py
    ↓ 1. Convert question to embedding (sentence-transformers)
ChromaDB (data/chroma_db/)
    ↓ 2. Vector similarity search (top 5 chunks)
Retrieved Chunks
    ↓ 3. Build prompt with context
Gemini API (FREE tier)
    ↓ 4. Generate answer
Response JSON
    ↓
Frontend displays answer + citations
```

---

## 📁 File Structure

```
fairscorec/
├── backend/
│   ├── app/
│   │   ├── routes/
│   │   │   └── clearclause.py          ← Local RAG endpoint
│   │   └── utils/
│   │       ├── rag_ingest.py            ← PDF ingestion script
│   │       └── rag_query.py             ← Query function
│   └── requirements.txt                 ← Dependencies
├── data/
│   ├── contracts/                       ← Put PDFs here
│   │   ├── contract1.pdf
│   │   └── contract2.pdf
│   └── chroma_db/                       ← Auto-created (vector DB)
│       └── legal_contracts/             ← Collection storage
└── frontend/
    └── src/
        └── modules/
            └── RAGPanel.tsx             ← UI component
```

---

## 🔧 Configuration

### Chunk Size (in `rag_ingest.py`)

```python
CHUNK_SIZE = 1000      # Characters per chunk
CHUNK_OVERLAP = 200    # Overlap between chunks
```

**Why these values?**
- Legal documents need context (clauses span paragraphs)
- 1000 chars = sweet spot for legal text
- 200 overlap = prevents clause splitting at boundaries

### Top-K Results (in `rag_query.py`)

```python
TOP_K = 5  # Number of chunks to retrieve
```

**Adjust if needed:**
- More chunks (7-10) = better context, slower
- Fewer chunks (3) = faster, may miss info
- 5 = balanced

### Embedding Model

Currently using: `all-MiniLM-L6-v2` (FREE, 80MB)

**Alternatives** (if you want better quality):
- `all-mpnet-base-v2` (better quality, 420MB)
- `paraphrase-multilingual-MiniLM-L12-v2` (multilingual)

Change in `rag_ingest.py` and `rag_query.py`:
```python
embedding_model = SentenceTransformer('all-mpnet-base-v2')
```

---

## 🐛 Troubleshooting

### "Collection 'legal_contracts' not found"

**Solution**: Run ingestion first:
```powershell
python backend/app/utils/rag_ingest.py
```

### "Gemini API not configured"

**Solution**: Add to `backend/.env`:
```
GEMINI_API_KEY=your_key_here
```

Or set environment variable:
```powershell
$env:GEMINI_API_KEY="your_key_here"
```

### "No PDF files found"

**Solution**: 
1. Check `data/contracts/` folder exists
2. Add at least one `.pdf` file
3. Run ingestion again

### Slow embedding generation

**First time**: Downloads ~80MB model (one-time, ~2-3 min)  
**Subsequent**: Uses cached model (fast)

If still slow:
- Check internet connection (first-time download)
- Try smaller chunk size (500 instead of 1000)

### Empty or poor answers

**Possible causes:**
1. PDFs not ingested → Run `rag_ingest.py`
2. Question too vague → Be specific: "What is the notice period?" not "Tell me about the contract"
3. No relevant content → Check if PDFs actually contain answer
4. Gemini quota exceeded → Wait 1 minute, try again

---

## 📊 Performance

**Ingestion** (first time):
- 1 PDF (5 pages) = ~30 seconds
- 10 PDFs (50 pages) = ~5 minutes
- Includes model download time

**Query** (after ingestion):
- Embedding generation = ~0.1 seconds
- ChromaDB search = ~0.05 seconds
- Gemini API call = ~2-5 seconds
- **Total**: ~3-6 seconds per query

**Storage**:
- ChromaDB size ≈ 10% of original PDF size
- Example: 10 PDFs (10MB) → ~1MB ChromaDB

---

## 🆚 Local RAG vs AWS RAG

| Feature | Local RAG (FREE) | AWS RAG (Paid) |
|---------|------------------|----------------|
| **Cost** | FREE (except Gemini API) | ~$10-15/month |
| **Setup** | 5 minutes | 30-45 minutes |
| **Scalability** | Limited (local machine) | Unlimited (cloud) |
| **Speed** | Fast (local) | Fast (cloud) |
| **Quality** | Good (sentence-transformers) | Excellent (Titan + Claude) |
| **Offline** | Yes (except Gemini) | No (requires AWS) |
| **Best for** | Development, testing | Production, scale |

**Use Local RAG when:**
- ✅ Developing/testing
- ✅ Small number of documents (< 50)
- ✅ Want to avoid AWS costs
- ✅ Need offline capability

**Use AWS RAG when:**
- ✅ Production deployment
- ✅ Large document corpus (> 100 PDFs)
- ✅ Need enterprise-grade quality
- ✅ Multiple users

---

## 🎓 Next Steps

### 1. Add More PDFs

```powershell
# Add PDFs to data/contracts/
# Then re-run ingestion
python backend/app/utils/rag_ingest.py
```

**Note**: Ingestion deletes old collection and creates fresh one. To append, modify `rag_ingest.py` (remove `delete_collection` call).

### 2. Customize Prompts

Edit `rag_query.py` → `generate_answer()` function:

```python
prompt = f"""You are a legal document analysis assistant...
[Your custom instructions here]
"""
```

### 3. Improve Chunking

For better results, try:
- **Recursive chunking** (by paragraphs, then sentences)
- **Semantic chunking** (using embeddings to find natural breaks)
- **Metadata enrichment** (add section headers, clause numbers)

### 4. Add Filters

Filter by document type, date, etc.:

```python
# In query_chromadb()
results = collection.query(
    query_embeddings=[question_embedding],
    n_results=top_k,
    where={"document_type": "contract"}  # Filter
)
```

---

## ✅ Success Checklist

After following this guide, you should have:

- [x] Dependencies installed
- [x] PDFs ingested into ChromaDB
- [x] Backend running (`http://localhost:8000`)
- [x] Frontend running (`http://localhost:5173`)
- [x] Can ask questions and get answers
- [x] Citations showing (filename, page, snippet)

---

## 🎉 You're Done!

Your local RAG system is now working! 

**Try these sample questions:**
- "What is the notice period for cheque bounce?"
- "Summarize the consumer protection notice"
- "What are the legal remedies mentioned?"
- "Who are the parties in the legal notice?"

**Need help?**
- Check `docs/RAG_IMPLEMENTATION.md` for architecture details
- Check `docs/AWS_RAG_SETUP.md` if you want to upgrade to AWS later

---

**Happy querying! 🚀**

