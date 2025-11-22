"""
RAG (Retrieval-Augmented Generation) endpoint for contract Q&A using AWS Bedrock Knowledge Base.

How this works:
1. User sends a question like "What are the termination penalties?"
2. This route calls AWS Bedrock Knowledge Base which:
   - Searches your uploaded PDFs for relevant passages
   - Sends those passages + question to Claude AI
   - Returns answer with citations (source document, page, snippet)
3. We return structured JSON with answer, reasoning, and citations

Requirements:
- AWS credentials configured (via IAM role or aws configure)
- Knowledge Base ID set in .env
- boto3 installed (AWS Python SDK)
"""

import os
import json
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
import boto3
from botocore.exceptions import BotoCoreError, ClientError
# Lazy loader to avoid MemoryError on startup for local TF-IDF RAG
_simple_rag_cached = None

def get_simple_rag():
    global _simple_rag_cached
    if _simple_rag_cached is not None:
        return _simple_rag_cached
    try:
        from ..utils.simple_free_rag import get_simple_rag as _factory  # 100% FREE local RAG!
        _simple_rag_cached = _factory()
        return _simple_rag_cached
    except MemoryError:
        print("Warning: simple_free_rag import failed due to MemoryError")
        return None
    except Exception as e:
        print(f"Warning: simple_free_rag unavailable: {e}")
        return None

# Create router (FastAPI's way of organizing endpoints)
router = APIRouter(prefix="/api", tags=["rag"])

# Load configuration from environment variables
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
KNOWLEDGE_BASE_ID = os.getenv("KNOWLEDGE_BASE_ID", "")
BEDROCK_MODEL_ID = os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-3-5-sonnet-20241022-v1:0")
MAX_RESULTS = int(os.getenv("RAG_MAX_RESULTS", "5"))
LOCAL_RAG_ENABLED = True  # FREE local RAG with TF-IDF (no PyTorch!)

# Initialize AWS Bedrock client (will use IAM role or ~/.aws/credentials)
try:
    bedrock_agent_runtime = boto3.client(
        "bedrock-agent-runtime",
        region_name=AWS_REGION
    )
except Exception as e:
    print(f"Warning: Failed to initialize Bedrock client: {e}")
    bedrock_agent_runtime = None


# Request/Response models (data validation)
class RAGQueryRequest(BaseModel):
    """What the frontend sends us"""
    query: str = Field(..., min_length=1, description="User's question about contracts")


class Citation(BaseModel):
    """Individual source reference"""
    s3_object: Optional[str] = Field(None, description="S3 path or filename")
    page: Optional[int] = Field(None, description="Page number in PDF")
    snippet: str = Field(..., description="Relevant text excerpt")
    confidence: Optional[float] = Field(None, description="Relevance score (0-1)")
    raw_metadata: Optional[Dict[str, Any]] = Field(None, description="Full AWS metadata")


class RAGQueryResponse(BaseModel):
    """What we return to frontend"""
    answer: str = Field(..., description="AI-generated answer")
    reasoning: Optional[str] = Field(None, description="Chain-of-thought explanation")
    citations: List[Citation] = Field(default_factory=list, description="Source references")
    raw_response: Optional[Dict[str, Any]] = Field(None, description="Full AWS response for debugging")


@router.post("/rag-query", response_model=RAGQueryResponse)
async def rag_query(request: RAGQueryRequest) -> RAGQueryResponse:
    """
    Main endpoint: Ask a question about uploaded contracts and get AI answer with citations.
    
    Example request:
    POST /api/rag-query
    {"query": "What are the early termination penalties?"}
    
    Example response:
    {
      "answer": "The contract specifies 30 days notice required...",
      "reasoning": "I examined sections 5.2 and 8.1...",
      "citations": [
        {
          "s3_object": "s3://bucket/contract.pdf",
          "page": 5,
          "snippet": "Either party may terminate with thirty (30) days written notice...",
          "confidence": 0.87
        }
      ]
    }
    """
    
    # Decide backend: AWS if fully configured, else FREE local TF-IDF RAG
    use_aws = bool(KNOWLEDGE_BASE_ID.strip()) and bedrock_agent_runtime is not None

    if not use_aws:
        # Local FREE RAG path
        try:
            rag_instance = get_simple_rag()
            if rag_instance is None:
                raise HTTPException(status_code=503, detail="Local RAG unavailable (memory or import error). Please retry or configure AWS RAG.")
            result = rag_instance.query(request.query)

            # Map local citations to unified Citation model
            citations: List[Citation] = []
            for c in result.get("citations", [])[:MAX_RESULTS]:
                citations.append(Citation(
                    s3_object=c.get("s3_object") or c.get("raw_metadata", {}).get("filename") or c.get("raw_metadata", {}).get("path"),
                    page=c.get("page"),
                    snippet=c.get("snippet", "")[:500],
                    confidence=c.get("confidence"),
                    raw_metadata=c.get("raw_metadata")
                ))

            return RAGQueryResponse(
                answer=result.get("answer", "No answer produced."),
                reasoning=result.get("reasoning", "Local TF-IDF retrieval"),
                citations=citations,
                raw_response={"source": "local_free", "chunks_considered": len(result.get("citations", []))}
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Local RAG error: {e}")

    # AWS path
    try:
        # Call AWS Bedrock Knowledge Base
        # retrieve_and_generate does 3 things in one call:
        # 1. Searches vector database for relevant chunks
        # 2. Sends chunks + query to Claude
        # 3. Returns answer + citations
        response = bedrock_agent_runtime.retrieve_and_generate(
            input={"text": request.query},
            retrieveAndGenerateConfiguration={
                "type": "KNOWLEDGE_BASE",
                "knowledgeBaseConfiguration": {
                    "knowledgeBaseId": KNOWLEDGE_BASE_ID,
                    "modelArn": f"arn:aws:bedrock:{AWS_REGION}::foundation-model/{BEDROCK_MODEL_ID}",
                    "generationConfiguration": {
                        "inferenceConfig": {
                            "textInferenceConfig": {
                                "maxTokens": 1000,  # Max response length
                                "temperature": 0.2,  # Low = more focused answers
                                "topP": 0.9
                            }
                        },
                        # Custom prompt to guide Claude's responses
                        "promptTemplate": {
                            "textPromptTemplate": """You are a legal contract analysis assistant. Answer questions clearly and cite sources.

Instructions:
1. Provide a clear, direct answer first
2. If the information is in the retrieved passages, cite them
3. If uncertain, say "The provided documents do not contain sufficient information"
4. Be specific about page numbers and sections when available

User Question: $query$

Retrieved Context:
$search_results$

Provide your answer:"""
                        }
                    }
                }
            }
        )
        
    except ClientError as e:
        error_code = e.response.get("Error", {}).get("Code", "Unknown")
        error_msg = e.response.get("Error", {}).get("Message", str(e))
        
        # User-friendly error messages
        if error_code == "AccessDeniedException":
            raise HTTPException(
                status_code=403,
                detail=f"AWS access denied. Check IAM permissions for Bedrock and S3. Details: {error_msg}"
            )
        elif error_code == "ResourceNotFoundException":
            raise HTTPException(
                status_code=404,
                detail=f"Knowledge Base not found. Verify KNOWLEDGE_BASE_ID is correct. Details: {error_msg}"
            )
        elif error_code == "ThrottlingException":
            raise HTTPException(
                status_code=429,
                detail="AWS rate limit exceeded. Please retry in a few seconds."
            )
        else:
            raise HTTPException(
                status_code=502,
                detail=f"AWS Bedrock error ({error_code}): {error_msg}"
            )
    
    except BotoCoreError as e:
        raise HTTPException(
            status_code=500,
            detail=f"AWS connection error: {str(e)}. Check network and region configuration."
        )
    
    # Parse AWS response
    raw_output = response.get("output", {})
    model_text = raw_output.get("text", "").strip()
    retrievals = response.get("citations", [])  # Claude 3.5 returns citations here
    
    # Build citation list
    citations = []
    for citation in retrievals[:MAX_RESULTS]:
        # Each citation has retrievedReferences
        for ref in citation.get("retrievedReferences", []):
            content = ref.get("content", {})
            location = ref.get("location", {})
            
            # Extract metadata
            s3_location = location.get("s3Location", {})
            s3_uri = s3_location.get("uri", "")
            
            # Try to extract page number from metadata
            metadata = ref.get("metadata", {})
            page_num = None
            if "x-amz-bedrock-kb-chunk-id" in metadata:
                # Parse page from chunk metadata if available
                try:
                    page_num = int(metadata.get("pageNumber", 0))
                except (ValueError, TypeError):
                    page_num = None
            
            citations.append(Citation(
                s3_object=s3_uri if s3_uri else "unknown",
                page=page_num,
                snippet=content.get("text", "")[:500],  # Limit snippet length
                confidence=None,  # Confidence not directly provided in this response format
                raw_metadata=metadata
            ))
    
    # If no structured citations, try to extract from retrievalResults (fallback)
    if not citations:
        retrievals_fallback = response.get("retrievalResults", [])
        for r in retrievals_fallback[:MAX_RESULTS]:
            content = r.get("content", {})
            text = content.get("text", "")
            metadata = content.get("metadata", {})
            
            citations.append(Citation(
                s3_object=metadata.get("source", metadata.get("x-amz-bedrock-kb-source-uri", "unknown")),
                page=metadata.get("pageNumber"),
                snippet=text[:500],
                confidence=r.get("score"),
                raw_metadata=metadata
            ))
    
    # Return structured response
    return RAGQueryResponse(
        answer=model_text,
        reasoning="Retrieved from knowledge base and analyzed by Claude",
        citations=citations,
        raw_response=response  # Include full response for debugging
    )


@router.get("/rag-health")
async def rag_health():
    """
    Health check endpoint - verifies AWS configuration without making expensive calls.
    
    Returns:
    - configured: Whether KB ID is set
    - region: AWS region
    - client_ready: Whether boto3 client initialized
    """
    return {
        "status": "healthy",
        "mode": "aws" if (KNOWLEDGE_BASE_ID.strip() and bedrock_agent_runtime) else "local_free",
        "configured": bool(KNOWLEDGE_BASE_ID.strip()),
        "knowledge_base_id": KNOWLEDGE_BASE_ID[:10] + "..." if KNOWLEDGE_BASE_ID else None,
        "region": AWS_REGION,
        "model": BEDROCK_MODEL_ID,
        "client_ready": bedrock_agent_runtime is not None,
        "local_rag_enabled": LOCAL_RAG_ENABLED
    }


@router.post("/rag-ingest-local")
async def rag_ingest_local():
    """
    Trigger local ingestion of PDFs from data/contracts into ChromaDB.
    DISABLED: PyTorch DLL issues on Windows.
    """
    try:
        print("[RAG] Building FREE local index...")
        rag_instance = get_simple_rag()
        if rag_instance is None:
            raise HTTPException(status_code=503, detail="Local RAG unavailable (memory or import error). Cannot ingest.")
        rag_instance.load_documents()
        if rag_instance.chunks:
            rag_instance.build_index()
            rag_instance.save_index()
            return {
                "status": "success",
                "message": f"Indexed {len(rag_instance.chunks)} chunks from contracts directory",
                "chunks_count": len(rag_instance.chunks)
            }
        else:
            return {
                "status": "warning",
                "message": "No PDF or DOCX files found in data/contracts directory"
            }
    except Exception as e:
        print(f"[RAG] Ingestion error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
