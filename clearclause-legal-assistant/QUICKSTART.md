# 🚀 Quick Start Guide - ClearClause Legal AI

## ⚡ Get Started in 3 Steps

### Step 1: Install Backend Dependencies

```bash
cd E:\fairscorec\clearclause-legal-assistant\backend
pip install -r requirements.txt
```

### Step 2: Set Up API Key

1. Get your FREE Gemini API key from: https://aistudio.google.com/
2. Create a `.env` file in `clearclause-legal-assistant/` folder:

```
API_KEY=your_actual_api_key_here
```

### Step 3: Start the Application

**Terminal 1 - Backend:**

```bash
cd E:\fairscorec\clearclause-legal-assistant\backend
uvicorn main:app --reload --host 0.0.0.0 --port 8001
```

**Terminal 2 - Frontend:**
Just open `E:\fairscorec\clearclause-legal-assistant\frontend\index.html` in your browser!

Or use Python's simple server:

```bash
cd E:\fairscorec\clearclause-legal-assistant\frontend
python -m http.server 8080
```

Then visit: http://localhost:8080

---

## 🎯 How to Use

1. **Upload Documents**: Click the upload area and select PDF/DOCX files
2. **Process**: Click "Process Documents" button
3. **Ask Questions**: Type your legal questions in the chat
4. **Generate Summary**: Add custom instructions and generate summaries
5. **Translate**: Switch to "Translate" tab for Hindi/Marathi translation

---

## ✅ Features

✨ **Document Analysis** - Upload multiple PDF/DOCX files  
💬 **Intelligent Q&A** - Ask questions about documents or general legal queries  
📝 **Custom Summaries** - Generate summaries with specific instructions  
🌍 **Translation** - Translate to Hindi (हिन्दी) or Marathi (मराठी)  
🎨 **Beautiful UI** - Modern, responsive design  
🔒 **Privacy** - All processing happens locally (except Gemini API calls)

---

## 🐛 Troubleshooting

**Problem**: Backend won't start  
**Solution**: Make sure you've created the `.env` file with your API_KEY

**Problem**: "No module named 'fastapi'"  
**Solution**: Run `pip install -r requirements.txt` in the backend folder

**Problem**: CORS errors in browser  
**Solution**: Make sure backend is running on port 8001

**Problem**: Frontend can't connect  
**Solution**: Check if API_URL in index.html matches your backend URL (default: http://localhost:8001)

---

## 📺 Test it!

Try these example questions:

- "What are the key clauses in this contract?"
- "Explain the terms and conditions"
- "What are my rights according to this document?"
- "Summarize the payment terms"
- "Translate this clause to Hindi"

Enjoy using ClearClause! ⚖️
