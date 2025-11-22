"""
100% FREE Local RAG - No PyTorch, No AWS, No Credits Needed!

Uses:
- TF-IDF vectorization (scikit-learn - already installed)
- Simple cosine similarity for search
- Google Gemini API (you already have free key) for generation
- Works completely offline for search, online only for LLM answer
"""

import os
from pathlib import Path
from typing import List, Dict, Any
import pickle

# Only use libraries we already have
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from pypdf import PdfReader
from docx import Document
import google.generativeai as genai

# Paths
CONTRACTS_DIR = Path(__file__).parent.parent.parent.parent / "data" / "contracts"
INDEX_PATH = Path(__file__).parent.parent.parent.parent / "data" / "tfidf_index.pkl"

# Initialize Gemini (free API)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

class SimpleFreeRAG:
    """100% free local RAG using TF-IDF + Gemini"""
    
    def __init__(self):
        self.chunks = []
        self.metadata = []
        self.vectorizer = None
        self.tfidf_matrix = None
        
    def load_documents(self) -> None:
        """Load and chunk documents (PDF and DOCX) from contracts directory"""
        print(f"Loading documents from {CONTRACTS_DIR}")

        if not CONTRACTS_DIR.exists():
            print(f"Creating contracts directory: {CONTRACTS_DIR}")
            CONTRACTS_DIR.mkdir(parents=True, exist_ok=True)
            return

        # Get both PDF and DOCX files
        pdf_files = list(CONTRACTS_DIR.glob("*.pdf"))
        docx_files = list(CONTRACTS_DIR.glob("*.docx"))

        all_files = pdf_files + docx_files
        if not all_files:
            print("No PDF or DOCX files found in contracts directory")
            return

        for file_path in all_files:
            try:
                if file_path.suffix.lower() == '.pdf':
                    self._load_pdf(file_path)
                elif file_path.suffix.lower() == '.docx':
                    self._load_docx(file_path)
            except Exception as e:
                print(f"[ERROR] Error loading {file_path.name}: {e}")

        print(f"\nTotal chunks created: {len(self.chunks)}")

    def _load_pdf(self, pdf_path: Path) -> None:
        """Load a PDF file"""
        reader = PdfReader(str(pdf_path))
        for page_num, page in enumerate(reader.pages):
            text = page.extract_text()
            if text.strip():
                # Split into chunks of ~1000 chars
                words = text.split()
                chunk_size = 200  # words per chunk
                for i in range(0, len(words), chunk_size):
                    chunk = " ".join(words[i:i+chunk_size])
                    if len(chunk.strip()) > 50:  # Skip tiny chunks
                        self.chunks.append(chunk)
                        self.metadata.append({
                            "filename": pdf_path.name,
                            "page": page_num + 1,
                            "path": str(pdf_path)
                        })
        print(f"[OK] Loaded PDF {pdf_path.name}: {len(reader.pages)} pages")

    def _load_docx(self, docx_path: Path) -> None:
        """Load a DOCX file"""
        document = Document(str(docx_path))
        text = ""
        for para in document.paragraphs:
            text += para.text + "\n"

        if text.strip():
            # Split into chunks of ~1000 chars
            words = text.split()
            chunk_size = 200  # words per chunk
            page_num = 1  # DOCX doesn't have pages, so use 1
            for i in range(0, len(words), chunk_size):
                chunk = " ".join(words[i:i+chunk_size])
                if len(chunk.strip()) > 50:  # Skip tiny chunks
                    self.chunks.append(chunk)
                    self.metadata.append({
                        "filename": docx_path.name,
                        "page": page_num,
                        "path": str(docx_path)
                    })
            print(f"[OK] Loaded DOCX {docx_path.name}: {len(self.chunks)} chunks")
    
    def build_index(self) -> None:
        """Build TF-IDF index"""
        if not self.chunks:
            print("No chunks to index!")
            return
        
        print("Building TF-IDF index...")
        self.vectorizer = TfidfVectorizer(
            max_features=5000,
            stop_words='english',
            ngram_range=(1, 2)
        )
        self.tfidf_matrix = self.vectorizer.fit_transform(self.chunks)
        print(f"[OK] Index built: {self.tfidf_matrix.shape}")

    def save_index(self) -> None:
        """Save index to disk"""
        INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(INDEX_PATH, 'wb') as f:
            pickle.dump({
                'chunks': self.chunks,
                'metadata': self.metadata,
                'vectorizer': self.vectorizer,
                'tfidf_matrix': self.tfidf_matrix
            }, f)
        print(f"[OK] Index saved to {INDEX_PATH}")

    def load_index(self) -> bool:
        """Load index from disk"""
        if not INDEX_PATH.exists():
            return False

        try:
            with open(INDEX_PATH, 'rb') as f:
                data = pickle.load(f)
            self.chunks = data['chunks']
            self.metadata = data['metadata']
            self.vectorizer = data['vectorizer']
            self.tfidf_matrix = data['tfidf_matrix']
            print(f"[OK] Loaded index: {len(self.chunks)} chunks")
            return True
        except Exception as e:
            print(f"[ERROR] Error loading index: {e}")
            return False
    
    def search(self, query: str, top_k: int = 8) -> List[Dict[str, Any]]:
        """Search for relevant chunks"""
        if self.vectorizer is None:
            return []
        
        # Vectorize query
        query_vec = self.vectorizer.transform([query])
        
        # Calculate cosine similarity
        similarities = cosine_similarity(query_vec, self.tfidf_matrix)[0]
        
        # Get top K results
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        
        results = []
        for idx in top_indices:
            if similarities[idx] > 0.003:  # Lower threshold for more results
                results.append({
                    'text': self.chunks[idx],
                    'score': float(similarities[idx]),
                    'metadata': self.metadata[idx]
                })
        
        return results
    
    def generate_answer(self, query: str, results: List[Dict]) -> str:
        """Generate answer using Gemini"""
        if not GEMINI_API_KEY:
            # Fallback: just return the most relevant chunk
            if results:
                return f"[Based on {results[0]['metadata']['filename']} p.{results[0]['metadata']['page']}]\n\n{results[0]['text'][:500]}..."
            return "No relevant information found."
        
        try:
            # Build context from search results
            context = "\n\n".join([
                f"[From {r['metadata']['filename']}, Page {r['metadata']['page']}]\n{r['text']}"
                for r in results[:3]
            ])
            
            # Build prompt
            prompt = f"""You are a legal contract analyst. Answer the question based ONLY on the provided context.

Context from contracts:
{context}

Question: {query}

Instructions:
1. Provide a clear, direct answer
2. Cite the source document and page number
3. If the context doesn't contain the answer, say "The provided contracts do not contain this information"
4. Be concise but complete

Answer:"""
            
            # Call Gemini
            model = genai.GenerativeModel('gemini-2.0-flash-exp')
            response = model.generate_content(
                prompt,
                generation_config={
                    'temperature': 0.2,
                    'max_output_tokens': 500
                }
            )
            return response.text
            
        except Exception as e:
            # Fallback to extractive answer
            if results:
                return f"[Extractive answer from {results[0]['metadata']['filename']} p.{results[0]['metadata']['page']}]\n\n{results[0]['text'][:500]}..."
            return f"Error generating answer: {e}"
    
    def query(self, question: str) -> Dict[str, Any]:
        """Main query function"""
        # Search for relevant chunks
        results = self.search(question, top_k=5)
        
        if not results:
            return {
                'answer': "No relevant information found in the uploaded contracts.",
                'citations': [],
                'reasoning': "No matching documents"
            }
        
        # Generate answer
        answer = self.generate_answer(question, results)
        
        # Format citations
        citations = []
        for r in results:
            citations.append({
                's3_object': r['metadata']['filename'],
                'page': r['metadata']['page'],
                'snippet': r['text'][:400],
                'confidence': r['score'],
                'raw_metadata': r['metadata']
            })
        
        return {
            'answer': answer,
            'citations': citations,
            'reasoning': f"Found {len(results)} relevant passages using TF-IDF similarity"
        }


# Singleton instance
_rag_instance = None

def get_simple_rag() -> SimpleFreeRAG:
    """Get or create RAG instance"""
    global _rag_instance
    if _rag_instance is None:
        _rag_instance = SimpleFreeRAG()
        
        # Try to load existing index
        if not _rag_instance.load_index():
            # Build new index
            print("No existing index found, building new one...")
            _rag_instance.load_documents()
            if _rag_instance.chunks:
                _rag_instance.build_index()
                _rag_instance.save_index()
    
    return _rag_instance


# Script to build index
if __name__ == "__main__":
    print("Building FREE Local RAG Index...")
    print("=" * 60)

    rag = SimpleFreeRAG()
    rag.load_documents()

    if rag.chunks:
        rag.build_index()
        rag.save_index()

        # Test query
        print("\n" + "=" * 60)
        print("Testing with sample query...")
        result = rag.query("What are the main obligations?")
        print(f"\nAnswer: {result['answer']}")
        print(f"\nCitations: {len(result['citations'])} found")
        for i, c in enumerate(result['citations'][:3], 1):
            print(f"  {i}. {c['s3_object']} p.{c['page']} (score: {c['confidence']:.3f})")
    else:
        print("\n[WARNING] No PDF or DOCX files found! Add document files to data/contracts/ folder")
