"""
ClearClause Legal AI Routes
Legal document analysis, Q&A, summarization, and translation
"""
from fastapi import APIRouter, File, UploadFile, HTTPException
from pydantic import BaseModel
from typing import List
import os

from ..utils.legal_processor import (
    LegalDocumentProcessor,
    translate_text
)

router = APIRouter()

# Global processor instance
processor = LegalDocumentProcessor()

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
    return {
        "status": "healthy",
        "document_loaded": bool(getattr(processor, "vector_store", None) is not None or getattr(processor, "raw_text", "")),
        "api_key_configured": bool(os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY"))
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
        
        # Process documents
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
        if request.use_document:
            if not processor.vector_store:
                raise HTTPException(
                    status_code=400,
                    detail="No documents uploaded. Please upload documents first or disable 'use_document'."
                )
            answer = processor.handle_document_qna(request.question)
            source = "document"
        else:
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
async def clear_data():
    """
    Clear all uploaded documents and reset the processor
    """
    try:
        processor.clear()
        return {
            "status": "success",
            "message": "All data cleared successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
