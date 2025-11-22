"""
ClearClause Legal AI Routes
Legal document analysis, Q&A, summarization, and translation
"""
from fastapi import APIRouter, File, UploadFile, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os

# Lazy import to avoid PyTorch DLL errors on startup
# from ..utils.local_rag import get_local_rag

router = APIRouter()

# Lazy-initialized processor to avoid heavy imports at startup
processor = None

# --- Request/Response Models ---
class QuestionRequest(BaseModel):
    question: str
    use_document: bool = False

class SummaryRequest(BaseModel):
    instruction: str = "Provide a comprehensive summary"

class TranslateRequest(BaseModel):
    text: str
    target_language: str  # "Hindi" or "Kannada"

class ChatResponse(BaseModel):
    answer: str
    source: str  # "document" or "general"

# --- API Endpoints ---

@router.get("/health")
async def health_check():
    """Health check endpoint for ClearClause module"""
    # Initialize minimal flags without importing heavy modules
    api_key_configured = bool(os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY"))
    has_doc = False
    try:
        global processor
        if processor is None:
            # don't import heavy module unless needed
            pass
        else:
            has_doc = bool(getattr(processor, "vector_store", None) is not None or getattr(processor, "raw_text", ""))
    except Exception:
        has_doc = False

    return {
        "status": "healthy",
        "document_loaded": has_doc,
        "api_key_configured": api_key_configured
    }

@router.post("/upload")
async def upload_documents(files: List[UploadFile] = File(...)):
    """
    Upload and process legal documents (PDF or DOCX)
    """
    try:
        if not files:
            raise HTTPException(status_code=400, detail="No files uploaded")
        
        # Save uploaded files temporarily
        file_paths = []
        for file in files:
            file_path = f"temp_{file.filename}"
            with open(file_path, "wb") as f:
                content = await file.read()
                f.write(content)
            file_paths.append(file_path)
        
        # Lazy import and initialize processor
        global processor
        if processor is None:
            from ..utils.legal_processor import LegalDocumentProcessor  # defer heavy import
            processor = LegalDocumentProcessor()

        success = processor.process_documents(file_paths)
        
        # Clean up temp files
        for path in file_paths:
            try:
                os.remove(path)
            except:
                pass
        
        if success:
            return {
                "status": "success",
                "message": f"Successfully processed {len(files)} document(s)",
                "files": [f.filename for f in files]
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to process documents")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/ask", response_model=ChatResponse)
async def ask_question(request: QuestionRequest):
    """
    Ask a question - either about uploaded documents or general legal query
    """
    try:
        global processor
        if request.use_document:
            if not processor.vector_store:
                raise HTTPException(
                    status_code=400,
                    detail="No documents uploaded. Please upload documents first or disable 'use_document'."
                )
            answer = processor.handle_document_qna(request.question)
            source = "document"
        else:
            if processor is None:
                from ..utils.legal_processor import LegalDocumentProcessor  # defer
                processor = LegalDocumentProcessor()
            answer = processor.handle_general_qna(request.question)
            source = "general"
        
        return ChatResponse(answer=answer, source=source)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/summarize")
async def generate_summary(request: SummaryRequest):
    """
    Generate a custom summary of uploaded documents
    """
    try:
        global processor
        if processor is None:
            from ..utils.legal_processor import LegalDocumentProcessor
            processor = LegalDocumentProcessor()
        if not processor.raw_text:
            raise HTTPException(
                status_code=400,
                detail="No documents uploaded. Please upload documents first."
            )
        
        summary = processor.generate_summary(request.instruction)
        
        return {
            "status": "success",
            "instruction": request.instruction,
            "summary": summary
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/translate")
async def translate(request: TranslateRequest):
    """
    Translate English text to Hindi or Kannada
    """
    try:
        if request.target_language not in ["Hindi", "Kannada"]:
            raise HTTPException(
                status_code=400,
                detail="Target language must be 'Hindi' or 'Kannada'"
            )
        
        # Lazy import translate function
        from ..utils.legal_processor import translate_text
        translated = translate_text(request.text, request.target_language)
        
        return {
            "status": "success",
            "original": request.text,
            "translated": translated,
            "target_language": request.target_language
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/clear")
async def clear_documents():
    """
    Clear all uploaded documents and reset the processor
    """
    try:
        global processor
        if processor is not None:
            processor.clear()
        return {
            "status": "success",
            "message": "All data cleared successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# --- Local RAG Endpoint ---

class LocalRAGRequest(BaseModel):
    query: str

class LocalRAGCitation(BaseModel):
    filename: str
    page: int
    snippet: str
    relevance: float  # 0-1 score

class LocalRAGResponse(BaseModel):
    answer: str
    reasoning: Optional[str] = None
    citations: List[Dict[str, Any]]
    raw_response: Optional[Dict[str, Any]] = None

@router.post("/local-rag-query")
async def local_rag_query(request: LocalRAGRequest):
    """
    Query local ChromaDB RAG system (FREE, no AWS needed).
    
    How it works:
    1. Searches data/chroma_db for relevant contract chunks
    2. Uses free sentence-transformers embeddings
    3. Generates answer with Gemini API (free tier)
    4. Returns answer + citations (filename, page, snippet)
    
    Difference from AWS RAG:
    - Local: FREE, runs on your computer, needs rag_ingest.py run first
    - AWS: Cloud-based, scalable, costs ~$10-15/month
    
    Example:
    POST /api/clearclause/local-rag-query
    {"query": "What is the notice period for cheque bounce?"}
    """
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        logger.info(f"Processing RAG query: {request.query[:50]}...")
        # TEMPORARY: Return error message for hackathon - PyTorch DLL issue
        return {
            "answer": "⚠️ Local RAG is temporarily disabled. Please toggle to 'AWS RAG' at the top of this page to use cloud-powered contract Q&A.",
            "reasoning": "Switch the toggle from 'Local RAG' to 'AWS RAG' for full functionality.",
            "citations": [],
            "raw_response": {"error": "local_rag_disabled", "hint": "use_aws_rag"}
        }
    
    except Exception as e:
        import traceback
        error_msg = str(e)
        error_trace = traceback.format_exc()
        logger.error(f"RAG query error: {error_msg}\n{error_trace}")
        
        if "not found" in error_msg.lower() and "collection" in error_msg.lower():
            raise HTTPException(
                status_code=404,
                detail="ChromaDB collection not found. Please run: python backend/app/utils/rag_ingest.py"
            )
        elif "GEMINI_API_KEY" in error_msg or "api key" in error_msg.lower():
            raise HTTPException(
                status_code=500,
                detail="Gemini API key not configured. Please set GEMINI_API_KEY in backend/.env"
            )
        else:
            raise HTTPException(
                status_code=500, 
                detail=f"Local RAG error: {error_msg}. Check backend logs for details."
            )
