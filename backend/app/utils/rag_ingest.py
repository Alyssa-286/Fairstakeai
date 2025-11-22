"""
Local RAG Ingestion Script - Load PDFs into ChromaDB

What this does:
1. Scans data/contracts/ folder for PDF files
2. Extracts text from each PDF (page by page)
3. Splits text into chunks (1000 chars with 200 overlap for context)
4. Creates embeddings using FREE sentence-transformers model (all-MiniLM-L6-v2)
5. Stores in ChromaDB (local vector database at data/chroma_db/)

Why 1000 chars chunk size:
- Legal documents need context (clauses often span multiple paragraphs)
- Too small (500) = loses context
- Too large (2000) = embedding quality drops
- 1000 = sweet spot for legal text

Why 200 char overlap:
- Ensures clauses don't get split awkwardly at chunk boundaries
- Example: If clause ends at char 995 of chunk 1, it will also appear in start of chunk 2

Free model used: all-MiniLM-L6-v2
- Size: 80MB (downloads once, cached locally)
- Speed: ~100 pages/minute on laptop
- Quality: Good for retrieval (not as good as OpenAI but FREE)
- No API calls, no cost
"""

import os
# Disable TensorFlow imports (we use PyTorch)
os.environ['TRANSFORMERS_NO_TF'] = '1'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

from pathlib import Path
from typing import List, Dict, Any
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from pypdf import PdfReader

# Paths
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
CONTRACTS_DIR = PROJECT_ROOT / "data" / "contracts"
CHROMA_DB_DIR = PROJECT_ROOT / "data" / "chroma_db"

# Config
CHUNK_SIZE = 1000  # Characters per chunk (chosen for best legal doc context)
CHUNK_OVERLAP = 200  # Characters overlap between chunks
COLLECTION_NAME = "legal_contracts"  # ChromaDB collection name

# Initialize embedding model (FREE, local)
print("Loading embedding model (all-MiniLM-L6-v2)...")
print("   First time: will download ~80MB model")
print("   Subsequent runs: uses cached model")
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
print("Model loaded!")


def extract_text_from_pdf(pdf_path: Path) -> List[Dict[str, Any]]:
    """
    Extract text from PDF, page by page.
    
    Returns list of dicts: [{"page": 1, "text": "..."}, ...]
    
    Why page by page: We want citations to include page numbers
    """
    print(f"   Reading {pdf_path.name}...")
    reader = PdfReader(pdf_path)
    pages = []
    
    for page_num, page in enumerate(reader.pages, start=1):
        text = page.extract_text()
        if text.strip():  # Skip empty pages
            pages.append({
                "page": page_num,
                "text": text,
                "filename": pdf_path.name
            })
    
    print(f"      Extracted {len(pages)} pages")
    return pages


def chunk_text(text: str, chunk_size: int, overlap: int) -> List[str]:
    """
    Split text into overlapping chunks.
    
    Example with chunk_size=20, overlap=5:
    Text: "This is a sample legal document text"
    Chunks:
    1. "This is a sample le" (chars 0-19)
    2. "ple legal document " (chars 15-34, starts 5 chars before previous end)
    3. "ent text" (chars 30-end)
    """
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        
        if chunk.strip():  # Skip whitespace-only chunks
            chunks.append(chunk)
        
        start += (chunk_size - overlap)  # Move forward, but overlap
    
    return chunks


def ingest_pdfs():
    """
    Main ingestion function.
    
    Steps:
    1. Find all PDFs in data/contracts/
    2. Extract text page by page
    3. Chunk each page
    4. Create embeddings (using FREE model)
    5. Store in ChromaDB with metadata (filename, page, chunk index)
    """
    
    # Step 1: Find PDFs
    pdf_files = list(CONTRACTS_DIR.glob("*.pdf"))
    
    if not pdf_files:
        print(f"\nERROR: No PDF files found in {CONTRACTS_DIR}")
        print(f"   Please add PDF files to: {CONTRACTS_DIR.absolute()}")
        print(f"   Then run this script again.")
        return
    
    print(f"\nFound {len(pdf_files)} PDF file(s):")
    for pdf in pdf_files:
        print(f"   - {pdf.name}")
    
    # Step 2: Initialize ChromaDB
    print(f"\nInitializing ChromaDB at {CHROMA_DB_DIR}...")
    CHROMA_DB_DIR.mkdir(parents=True, exist_ok=True)
    
    client = chromadb.PersistentClient(
        path=str(CHROMA_DB_DIR),
        settings=Settings(anonymized_telemetry=False)  # Disable analytics
    )
    
    # Delete existing collection if it exists (fresh start each time)
    try:
        client.delete_collection(COLLECTION_NAME)
        print(f"   Deleted existing collection '{COLLECTION_NAME}'")
    except:
        pass
    
    # Create new collection
    collection = client.create_collection(
        name=COLLECTION_NAME,
        metadata={"description": "Legal contract embeddings"}
    )
    print(f"   Created collection '{COLLECTION_NAME}'")
    
    # Step 3: Process each PDF
    total_chunks = 0
    
    for pdf_path in pdf_files:
        print(f"\nProcessing {pdf_path.name}...")
        
        # Extract pages
        pages = extract_text_from_pdf(pdf_path)
        
        # Chunk and embed each page
        for page_data in pages:
            page_num = page_data["page"]
            page_text = page_data["text"]
            filename = page_data["filename"]
            
            # Split into chunks
            chunks = chunk_text(page_text, CHUNK_SIZE, CHUNK_OVERLAP)
            print(f"      Page {page_num}: {len(chunks)} chunk(s)")
            
            # Prepare data for ChromaDB
            for chunk_idx, chunk in enumerate(chunks):
                # Create unique ID
                chunk_id = f"{filename}_p{page_num}_c{chunk_idx}"
                
                # Create embedding (this is where the FREE model works!)
                embedding = embedding_model.encode(chunk).tolist()
                
                # Store in ChromaDB
                collection.add(
                    ids=[chunk_id],
                    embeddings=[embedding],
                    documents=[chunk],
                    metadatas=[{
                        "filename": filename,
                        "page": page_num,
                        "chunk_index": chunk_idx,
                        "source": str(pdf_path.absolute())
                    }]
                )
                
                total_chunks += 1
    
    # Step 4: Summary
    print(f"\n{'='*60}")
    print(f"Ingestion Complete!")
    print(f"{'='*60}")
    print(f"   Total chunks stored: {total_chunks}")
    print(f"   Collection name: {COLLECTION_NAME}")
    print(f"   Database location: {CHROMA_DB_DIR.absolute()}")
    print(f"\nNext step: Run queries using rag_query.py")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("🚀 Local RAG Ingestion - FREE Version")
    print("="*60)
    print("Using:")
    print("  - Embedding model: all-MiniLM-L6-v2 (FREE, local)")
    print("  - Vector DB: ChromaDB (FREE, local)")
    print("  - Chunk size: 1000 chars (optimal for legal docs)")
    print("  - Chunk overlap: 200 chars (context preservation)")
    print("="*60 + "\n")
    
    try:
        ingest_pdfs()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user. Partial ingestion may have occurred.")
    except Exception as e:
        print(f"\n\n❌ Error during ingestion: {e}")
        import traceback
        traceback.print_exc()
