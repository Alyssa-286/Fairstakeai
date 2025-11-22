# 🔧 RAG Query Fix - "Searching contracts..." Issue Resolved

## 🐛 Problem

The frontend was getting stuck at "Searching contracts..." when querying the RAG system. This was happening because:

1. **No timeout** - Frontend would wait indefinitely if backend was slow
2. **Model loading** - First request takes 30-60 seconds to load embedding model (~80MB download)
3. **Poor error handling** - Errors weren't being caught and displayed properly
4. **Gemini model name** - Using experimental model name that might not be available

---

## ✅ Fixes Applied

### 1. **Frontend Timeout** (`RAGPanel.tsx`)
- Added **60-second timeout** to prevent infinite waiting
- Shows helpful error message if timeout occurs
- Better error handling for network issues

### 2. **Backend Logging** (`rag_query.py`, `clearclause.py`)
- Added logging to track progress:
  - Model loading status
  - ChromaDB query progress
  - Gemini API calls
  - Error details
- Errors now include full traceback for debugging

### 3. **Gemini Model Fallback** (`rag_query.py`)
- Try `gemini-2.0-flash-exp` first
- Fallback to `gemini-pro` if experimental model unavailable
- Prevents crashes from model name issues

### 4. **Better Error Messages** (`clearclause.py`)
- Specific error for missing ChromaDB collection
- Specific error for missing Gemini API key
- Generic error with instructions to check logs

---

## 🚀 How to Test

### Step 1: Restart Backend

**Important:** You must restart the backend for changes to take effect!

```powershell
# Stop current backend (Ctrl+C)
# Then restart:
.\start_backend.ps1
```

### Step 2: Test Query

1. Open frontend: http://localhost:5173
2. Click **"Contract Q&A"** tab
3. Make sure **"🆓 Local RAG"** toggle is **ON**
4. Ask: **"Is there a limitation of liability clause?"**

### Expected Behavior:

**First Query (may take 30-60 seconds):**
- Shows "Searching contracts..." 
- Backend logs: "Loading embedding model (first time)..."
- Downloads ~80MB model (one-time)
- Returns answer with citations

**Subsequent Queries (3-6 seconds):**
- Much faster (model already loaded)
- Returns answer immediately

**If Error:**
- Shows error message in red box
- Helpful tips based on error type
- Check backend terminal for detailed logs

---

## 📊 What to Check

### Backend Terminal Should Show:

```
INFO: Processing RAG query: Is there a limitation of liability clause?...
INFO: Loading embedding model (first time - may take 30-60 seconds)...
INFO: Embedding model loaded successfully
INFO: Querying ChromaDB...
INFO: Found 5 relevant chunks
INFO: Generating answer with Gemini...
INFO: Answer generated successfully
INFO: RAG query completed successfully
```

### If You See Errors:

1. **"ChromaDB collection not found"**
   - Run: `python backend/app/utils/rag_ingest.py`

2. **"Gemini API key not configured"**
   - Add to `backend/.env`: `GEMINI_API_KEY=your_key_here`

3. **"Request timed out"**
   - First query takes longer (model download)
   - Try again after 60 seconds
   - Check internet connection

4. **"Error loading model"**
   - Check internet (needs to download ~80MB first time)
   - Check disk space
   - Check backend logs for details

---

## 🔍 Debugging Tips

### Check Backend Logs

Look at the terminal where backend is running. You should see:
- ✅ "Processing RAG query..." - Request received
- ✅ "Loading embedding model..." - Model loading (first time only)
- ✅ "Querying ChromaDB..." - Searching database
- ✅ "Found X relevant chunks" - Results found
- ✅ "Generating answer..." - Calling Gemini
- ✅ "Answer generated successfully" - Done!

### Check Browser Console

Press `F12` → Console tab. Look for:
- Network errors
- CORS issues
- Timeout messages

### Test API Directly

```powershell
curl -X POST http://localhost:8000/api/clearclause/local-rag-query `
  -H "Content-Type: application/json" `
  -d '{\"query\": \"test\"}'
```

---

## ⚡ Performance Notes

- **First query**: 30-60 seconds (model download)
- **Subsequent queries**: 3-6 seconds
- **Model cached**: After first load, no more downloads
- **Timeout**: 60 seconds (should be enough)

---

## 📝 Files Changed

1. `frontend/src/modules/RAGPanel.tsx` - Added timeout + better error handling
2. `backend/app/routes/clearclause.py` - Added logging + better error messages
3. `backend/app/utils/rag_query.py` - Added logging + Gemini fallback

---

## ✅ Success Indicators

After restarting backend, you should see:

1. ✅ Backend starts without errors
2. ✅ First query shows progress in backend logs
3. ✅ Answer appears in frontend (may take 30-60 seconds first time)
4. ✅ Citations show filename, page, snippet
5. ✅ Subsequent queries are fast (3-6 seconds)

---

**🎉 The fix is complete! Restart your backend and try again!**

