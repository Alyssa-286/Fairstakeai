"""
Local RAG Query Module - Search ChromaDB and Generate Answers

What this does:
1. Takes user question (e.g., "What is the notice period for cheque bounce?")
2. Converts question to embedding (using same FREE model as ingestion)
3. Searches ChromaDB for top 5 most similar chunks
4. Sends chunks + question to Gemini (FREE API you already have)
5. Returns answer with citations (filename, page number, snippet)

Why Gemini:
- You already have the API key
- Free tier: 60 requests/minute
- Good quality for legal text
- No new setup needed

Why top 5 chunks:
- Balance between context and response time
- More chunks = better context but slower
- Fewer chunks = faster but may miss info
- 5 is sweet spot
"""

import os
# Disable TensorFlow imports (we use PyTorch)
os.environ['TRANSFORMERS_NO_TF'] = '1'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

from pathlib import Path
from typing import List, Dict
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Paths
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
CHROMA_DB_DIR = PROJECT_ROOT / "data" / "chroma_db"
COLLECTION_NAME = "legal_contracts"

# Config
TOP_K = 5  # Number of chunks to retrieve (can adjust: 3-10)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Lazy initialization (only load when needed, not on import)
_embedding_model = None
_gemini_model = None

def get_embedding_model():
    """Lazy load embedding model (only when first needed)"""
    global _embedding_model
    if _embedding_model is None:
        import logging
        logger = logging.getLogger(__name__)
        logger.info("Loading embedding model (first time - may take 30-60 seconds)...")
        _embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        logger.info("Embedding model loaded successfully")
    return _embedding_model

def get_gemini_model():
    """Lazy load Gemini model (only when first needed)"""
    global _gemini_model
    if _gemini_model is None:
        if GEMINI_API_KEY:
            import logging
            logger = logging.getLogger(__name__)
            logger.info("Initializing Gemini model...")
            genai.configure(api_key=GEMINI_API_KEY)
            # Try gemini-2.0-flash-exp first, fallback to gemini-pro if not available
            try:
                _gemini_model = genai.GenerativeModel('gemini-2.0-flash-exp')
            except Exception:
                _gemini_model = genai.GenerativeModel('gemini-pro')
            logger.info("Gemini model initialized")
        else:
            _gemini_model = None
    return _gemini_model


def query_chromadb(question: str, top_k: int = TOP_K) -> List[Dict]:
    """
    Search ChromaDB for relevant chunks.
    
    Returns list of dicts:
    [
        {
            "text": "chunk content...",
            "filename": "contract.pdf",
            "page": 2,
            "distance": 0.45  # Lower = more similar
        },
        ...
    ]
    """
    # Connect to ChromaDB
    client = chromadb.PersistentClient(
        path=str(CHROMA_DB_DIR),
        settings=Settings(anonymized_telemetry=False)
    )
    
    try:
        collection = client.get_collection(COLLECTION_NAME)
    except Exception as e:
        raise Exception(f"Collection '{COLLECTION_NAME}' not found. Run rag_ingest.py first!")
    
    # Convert question to embedding
    embedding_model = get_embedding_model()
    question_embedding = embedding_model.encode(question).tolist()
    
    # Search ChromaDB
    results = collection.query(
        query_embeddings=[question_embedding],
        n_results=top_k,
        include=["documents", "metadatas", "distances"]
    )
    
    # Format results
    formatted_results = []
    for i in range(len(results['documents'][0])):
        formatted_results.append({
            "text": results['documents'][0][i],
            "filename": results['metadatas'][0][i]['filename'],
            "page": results['metadatas'][0][i]['page'],
            "chunk_index": results['metadatas'][0][i]['chunk_index'],
            "distance": results['distances'][0][i]
        })
    
    return formatted_results


def generate_answer(question: str, context_chunks: List[Dict]) -> Dict:
    """
    Use Gemini to generate answer from retrieved chunks.
    
    Prompt strategy:
    1. Give context (retrieved chunks with page refs)
    2. Ask question
    3. Request structured answer with citations
    """
    
    model = get_gemini_model()
    if not model:
        # Fallback if Gemini not configured
        return {
            "answer": "Gemini API not configured. Please set GEMINI_API_KEY in .env",
            "citations": context_chunks,
            "raw_response": None
        }
    
    # Build context string from chunks
    context_parts = []
    for idx, chunk in enumerate(context_chunks, 1):
        context_parts.append(
            f"[Source {idx}: {chunk['filename']}, Page {chunk['page']}]\n{chunk['text']}\n"
        )
    context_text = "\n".join(context_parts)
    
    # Build prompt
    prompt = f"""You are a legal document analysis assistant. Answer the question based ONLY on the provided context.

Context from legal documents:
{context_text}

User Question: {question}

Instructions:
1. Provide a clear, direct answer
2. Cite specific sources (mention document name and page number)
3. If the context doesn't contain the answer, say "The provided documents do not contain information about this"
4. Be specific and use legal terminology when appropriate

Answer:"""
    
    try:
        # Call Gemini
        response = model.generate_content(
            prompt,
            generation_config={
                "temperature": 0.2,  # Low = more focused, less creative
                "max_output_tokens": 1000,
            }
        )
        
        answer_text = response.text
        
    except Exception as e:
        error_msg = str(e)
        # Handle quota exceeded gracefully
        if "429" in error_msg or "quota" in error_msg.lower():
            # Build fallback answer from top chunks
            fallback_parts = []
            fallback_parts.append("⚠️ Gemini API quota exceeded. Here are the most relevant passages I found:\n")
            for idx, chunk in enumerate(context_chunks[:3], 1):
                fallback_parts.append(f"\n{idx}. From {chunk['filename']}, Page {chunk['page']}:")
                fallback_parts.append(f"   {chunk['text'][:300]}...")
            answer_text = "\n".join(fallback_parts)
            answer_text += "\n\n💡 Tip: Wait 1 minute and try again, or switch to AWS RAG in settings."
        else:
            answer_text = f"Error calling Gemini API: {error_msg}"
    
    return {
        "answer": answer_text,
        "citations": context_chunks,
        "raw_response": response.to_dict() if 'response' in locals() else None
    }


def query_rag(question: str, verbose: bool = False) -> Dict:
    """
    Main query function - combines retrieval + generation.
    
    Usage:
    >>> result = query_rag("What is the legal notice period?")
    >>> print(result['answer'])
    >>> for citation in result['citations']:
    >>>     print(f"Source: {citation['filename']}, Page {citation['page']}")
    
    Args:
        question: User's question
        verbose: If True, print progress messages (for CLI use)
    """
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        if verbose:
            print(f"\n🔍 Searching for: '{question}'")
        logger.info(f"Starting RAG query: {question[:50]}...")
        
        # Step 1: Retrieve relevant chunks
        if verbose:
            print(f"   Searching ChromaDB...")
        logger.info("Querying ChromaDB...")
        context_chunks = query_chromadb(question, top_k=TOP_K)
        if verbose:
            print(f"   Found {len(context_chunks)} relevant chunk(s)")
        logger.info(f"Found {len(context_chunks)} relevant chunks")
        
        # Step 2: Generate answer
        if verbose:
            print(f"   Generating answer with Gemini...")
        logger.info("Generating answer with Gemini...")
        result = generate_answer(question, context_chunks)
        if verbose:
            print(f"   ✅ Answer generated")
        logger.info("Answer generated successfully")
        
        return result
    except Exception as e:
        logger.error(f"Error in query_rag: {str(e)}", exc_info=True)
        raise


# CLI interface for testing
if __name__ == "__main__":
    print("\n" + "="*60)
    print("🤖 Local RAG Query - FREE Version")
    print("="*60)
    print("Using:")
    print("  - Embedding: all-MiniLM-L6-v2 (FREE, local)")
    print("  - LLM: Google Gemini (FREE API)")
    print("  - Vector DB: ChromaDB (FREE, local)")
    print("="*60 + "\n")
    
    # Sample questions you can try
    sample_questions = [
        "What is the notice period for cheque bounce?",
        "Summarize the consumer protection notice",
        "What are the legal remedies mentioned?",
        "Who are the parties in the legal notice?",
    ]
    
    print("📝 Sample questions you can ask:")
    for i, q in enumerate(sample_questions, 1):
        print(f"   {i}. {q}")
    
    print("\n" + "-"*60)
    
    # Interactive mode
    while True:
        user_question = input("\n❓ Your question (or 'quit' to exit): ").strip()
        
        if user_question.lower() in ['quit', 'exit', 'q']:
            print("\n👋 Goodbye!")
            break
        
        if not user_question:
            continue
        
        try:
            result = query_rag(user_question, verbose=True)
            
            print("\n" + "="*60)
            print("💡 ANSWER:")
            print("="*60)
            print(result['answer'])
            
            print("\n" + "="*60)
            print(f"📚 CITATIONS ({len(result['citations'])} sources):")
            print("="*60)
            for i, citation in enumerate(result['citations'], 1):
                print(f"\n{i}. 📄 {citation['filename']}")
                print(f"   Page: {citation['page']}")
                print(f"   Relevance: {(1 - citation['distance']) * 100:.1f}%")
                print(f"   Snippet: {citation['text'][:150]}...")
            
            print("\n" + "="*60)
            
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
