# Contract Q&A (RAG) - Quick Start

## What We Built

✅ **Backend**: FastAPI route `/api/rag-query` that calls AWS Bedrock Knowledge Base  
✅ **Frontend**: New "Contract Q&A" tab with question input, answer display, and citations  
✅ **Documentation**: Complete AWS setup guide in `docs/AWS_RAG_SETUP.md`  
✅ **Dependencies**: boto3 installed for AWS SDK

---

## Current Status

🟡 **Waiting for AWS setup** - Backend is ready, but needs Knowledge Base configuration.

**Health check result**:

```json
{
  "status": "healthy",
  "configured": false, // ← Will be true after AWS setup
  "knowledge_base_id": null,
  "region": "us-east-1",
  "model": "anthropic.claude-3-5-sonnet-20241022-v1:0",
  "client_ready": true
}
```

---

## Next Steps (You Need To Do)

### 1. **Create AWS Resources** (30-45 minutes)

Follow the detailed guide: **`docs/AWS_RAG_SETUP.md`**

Quick checklist:

- [ ] Create S3 bucket `fairstake-rag-data`
- [ ] Upload 2-5 contract PDFs to `contracts/` folder
- [ ] Request Bedrock model access (Claude 3.5 + Titan Embeddings)
- [ ] Create IAM role with S3 read permissions
- [ ] Create Bedrock Knowledge Base (select Titan embeddings + Quick Create vector store)
- [ ] Sync data source (wait for PDFs to be indexed)
- [ ] Copy Knowledge Base ID (looks like `kb-abc123...`)
- [ ] Paste KB ID into `backend/.env` → `KNOWLEDGE_BASE_ID=`
- [ ] Run `aws configure` to set up credentials (or use IAM role if on AWS)
- [ ] Restart backend

### 2. **Test Locally**

```powershell
# Terminal 1: Start backend
.\start_backend.ps1

# Terminal 2: Start frontend
.\start_frontend.ps1

# Open browser: http://localhost:5173
# Click "Contract Q&A" tab
# Try: "What are the termination penalties?"
```

### 3. **Verify It Works**

✅ Answer appears (3-10 seconds)  
✅ Citations show document name, page, snippet  
✅ No red error messages

---

## Architecture

```
User Question
    ↓
Frontend (RAGPanel.tsx)
    ↓ POST /api/rag-query
Backend (routes/rag.py)
    ↓ boto3 client
AWS Bedrock Knowledge Base
    ↓ Vector search
S3 Bucket (fairstake-rag-data)
    ↓ PDF chunks
OpenSearch Serverless (embeddings)
    ↓ Relevant passages
Claude 3.5 Sonnet
    ↓ Generated answer + citations
Response JSON
    ↓
Frontend displays
```

---

## Files Created/Modified

### Backend

- ✅ `backend/app/routes/rag.py` - New FastAPI route (300+ lines with docs)
- ✅ `backend/app/main.py` - Registered RAG router
- ✅ `backend/requirements.txt` - Added boto3
- ✅ `backend/.env` - Added AWS config vars

### Frontend

- ✅ `frontend/src/modules/RAGPanel.tsx` - New React component (250+ lines)
- ✅ `frontend/src/App.tsx` - Added 6th tab "Contract Q&A"

### Documentation

- ✅ `docs/AWS_RAG_SETUP.md` - Complete step-by-step AWS guide (400+ lines)
- ✅ `docs/RAG_QUICKSTART.md` - This file (quick reference)

---

## API Examples

### Health Check

```bash
curl http://localhost:8000/api/rag-health
```

### Query

```bash
curl -X POST http://localhost:8000/api/rag-query \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the notice period for termination?"}'
```

Expected response:

```json
{
  "answer": "The contract requires 30 days written notice for termination.",
  "reasoning": "Retrieved from knowledge base...",
  "citations": [
    {
      "s3_object": "s3://fairstake-rag-data/contracts/MSA.pdf",
      "page": 5,
      "snippet": "Either party may terminate with thirty (30) days...",
      "confidence": 0.87
    }
  ]
}
```

---

## Troubleshooting

| Issue                              | Solution                                   |
| ---------------------------------- | ------------------------------------------ |
| "KNOWLEDGE_BASE_ID not configured" | Set in `backend/.env`, restart backend     |
| "AWS access denied"                | Run `aws configure` with valid credentials |
| Empty citations                    | Re-sync Knowledge Base data source         |
| Frontend shows old code            | Hard refresh (Ctrl+Shift+R)                |

Full troubleshooting: See `docs/AWS_RAG_SETUP.md` Step 9.

---

## Cost Estimate

- **Development**: ~$10-15/month
- **Production (100 queries/day)**: ~$30-50/month
- **Breakdown**: S3 ($0.10), Embeddings ($0.50), Claude ($5-10), OpenSearch ($10-15)

**Tip**: Delete Knowledge Base when not testing to save OpenSearch costs.

---

## Security Notes

- ✅ AWS credentials NOT committed to Git
- ✅ S3 bucket has Block Public Access enabled
- ✅ IAM policies follow least privilege
- ✅ `.env` file gitignored
- ⚠️ For production: Use IAM roles (not access keys)

---

## After AWS Setup

Once Knowledge Base ID is set:

1. **Test queries**: Try the 5 sample questions in frontend
2. **Add more PDFs**: Upload to S3 → Sync KB
3. **Customize prompts**: Edit `promptTemplate` in `rag.py`
4. **Deploy**: Use AWS App Runner with IAM role

---

## Questions?

1. **AWS setup unclear?** → Read `docs/AWS_RAG_SETUP.md` (step-by-step with screenshots descriptions)
2. **Backend errors?** → Check `http://localhost:8000/api/rag-health`
3. **Cost concerns?** → Start with 2-3 PDFs, monitor AWS billing dashboard

---

**Ready to start?** → Open `docs/AWS_RAG_SETUP.md` and follow Step 1!
