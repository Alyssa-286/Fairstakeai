/**
 * RAGPanel - Contract Q&A using AWS Bedrock Knowledge Base
 * 
 * This component lets users:
 * 1. Ask questions about uploaded contract PDFs
 * 2. Get AI-powered answers with citations (source document, page, snippet)
 * 3. See reasoning behind answers
 * 
 * How it works:
 * - User types question like "What are the termination penalties?"
 * - Sends POST to /api/rag-query
 * - Backend queries AWS Bedrock Knowledge Base (searches PDFs + asks Claude)
 * - Displays answer + citations with page numbers and snippets
 */

import React, { useState } from 'react';
import { SectionCard } from '../components/SectionCard';

interface Citation {
  // AWS Bedrock format
  s3_object?: string | null;
  page?: number | null;
  snippet?: string;
  confidence?: number | null;
  raw_metadata?: Record<string, any>;
  // Local RAG format
  filename?: string;
  text?: string;
  relevance?: number;
  chunk_index?: number;
}

interface RAGResponse {
  answer: string;
  reasoning: string | null;
  citations: Citation[];
  raw_response?: any;
}

export default function RAGPanel() {
  const [query, setQuery] = useState('');
  const [response, setResponse] = useState<RAGResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [showRawResponse, setShowRawResponse] = useState(false);
  const [useLocalRAG, setUseLocalRAG] = useState(true); // 100% FREE local RAG (TF-IDF, no PyTorch!)

  // Sample questions to help users get started
  const sampleQuestions = [
    "What are the customer protection policies?",
    "What happens in case of cheque bounce?",
    "What is the bank social media policy?",
    "What are the liability rules for unauthorized transactions?",
    "How do I send a legal notice?"
  ];

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    setError('');
    setResponse(null);

    try {
      // Only AWS RAG available (local disabled due to PyTorch issues)
      const endpoint = '/api/rag-query';
      
      // Add timeout (60 seconds for first request, 30 seconds for subsequent)
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 60000); // 60 second timeout
      
      const res = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: query.trim() }),
        signal: controller.signal
      });

      clearTimeout(timeoutId);

      if (!res.ok) {
        const errorData = await res.json().catch(() => ({ detail: res.statusText }));
        throw new Error(errorData.detail || `HTTP ${res.status}: ${res.statusText}`);
      }

      const data: RAGResponse = await res.json();
      setResponse(data);
    } catch (err: any) {
      if (err.name === 'AbortError') {
        setError('Request timed out. The first query may take longer as models load. Please try again.');
      } else {
        setError(err.message || 'Failed to query knowledge base');
      }
    } finally {
      setLoading(false);
    }
  }

  function handleSampleClick(sample: string) {
    setQuery(sample);
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <SectionCard title="Contract Q&A (RAG)">
        <div className="space-y-4">
          <p className="text-gray-600">
            Ask questions about your uploaded contract PDFs using AI-powered search.
          </p>

          {/* Toggle Switch */}
          <div className="flex items-center justify-between p-4 bg-gradient-to-r from-indigo-50 to-purple-50 border border-indigo-200 rounded-lg">
            <div className="flex-1">
              <div className="flex items-center gap-2">
                <span className={`text-sm font-semibold ${useLocalRAG ? 'text-indigo-700' : 'text-gray-400'}`}>
                  🆓 Local RAG
                </span>
                <button
                  onClick={() => setUseLocalRAG(!useLocalRAG)}
                  className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                    useLocalRAG ? 'bg-indigo-600' : 'bg-gray-300'
                  }`}
                >
                  <span
                    className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                      useLocalRAG ? 'translate-x-6' : 'translate-x-1'
                    }`}
                  />
                </button>
                <span className={`text-sm font-semibold ${!useLocalRAG ? 'text-indigo-700' : 'text-gray-400'}`}>
                  ☁️ AWS Bedrock
                </span>
              </div>
              <p className="text-xs text-gray-600 mt-2">
                {useLocalRAG ? (
                  <>
                    <strong>FREE:</strong> Uses local ChromaDB + Gemini API. Run <code className="bg-white px-1 py-0.5 rounded text-xs">rag_ingest.py</code> first.
                  </>
                ) : (
                  <>
                    <strong>Cloud:</strong> AWS Bedrock Knowledge Base. Setup: <code className="bg-white px-1 py-0.5 rounded text-xs">docs/AWS_RAG_SETUP.md</code>
                  </>
                )}
              </p>
            </div>
          </div>

          {!useLocalRAG && (
            <div className="p-3 bg-blue-50 border border-blue-200 rounded-md text-sm">
              <strong>ℹ️ AWS Setup Required:</strong> Configure Bedrock Knowledge Base first.
              See <code className="bg-white px-1 py-0.5 rounded">docs/AWS_RAG_SETUP.md</code> for instructions.
            </div>
          )}

          {useLocalRAG && (
            <div className="p-3 bg-green-50 border border-green-200 rounded-md text-sm">
              <strong>✅ Local RAG Active:</strong> Using FREE ChromaDB + sentence-transformers.
              PDFs from <code className="bg-white px-1 py-0.5 rounded">data/contracts/</code>
            </div>
          )}
        </div>
      </SectionCard>

      {/* Query Input */}
      <SectionCard title="Ask a Question">
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label htmlFor="rag-query" className="block text-sm font-medium text-gray-700 mb-2">
              Your Question
            </label>
            <textarea
              id="rag-query"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="e.g., What are the termination notice requirements?"
              rows={3}
              className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              disabled={loading}
            />
          </div>

          <button
            type="submit"
            disabled={loading || !query.trim()}
            className={`w-full py-3 rounded-md font-medium transition-colors ${
              loading || !query.trim()
                ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                : 'bg-indigo-600 text-white hover:bg-indigo-700'
            }`}
          >
            {loading ? (
              <span className="flex items-center justify-center">
                <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Searching contracts...
              </span>
            ) : (
              'Search Knowledge Base'
            )}
          </button>
        </form>

        {/* Sample Questions */}
        <div className="mt-6">
          <h4 className="text-sm font-medium text-gray-700 mb-3">Try these examples:</h4>
          <div className="flex flex-wrap gap-2">
            {sampleQuestions.map((sample, idx) => (
              <button
                key={idx}
                onClick={() => handleSampleClick(sample)}
                className="px-3 py-1.5 text-sm bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-md transition-colors"
                disabled={loading}
              >
                {sample}
              </button>
            ))}
          </div>
        </div>
      </SectionCard>

      {/* Error Display */}
      {error && (
        <SectionCard title="Error">
          <div className="flex items-start space-x-3 bg-red-50 border border-red-200 rounded-md p-4">
            <svg className="w-5 h-5 text-red-500 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
            </svg>
            <div className="flex-1">
              <h4 className="font-medium text-red-800">Error</h4>
              <p className="text-sm text-red-700 mt-1">{error}</p>
              {error.includes('KNOWLEDGE_BASE_ID') && (
                <p className="text-xs text-red-600 mt-2">
                  💡 <strong>Tip:</strong> Set KNOWLEDGE_BASE_ID in backend/.env after creating Knowledge Base in AWS Console.
                </p>
              )}
              {error.includes('AWS') && (
                <p className="text-xs text-red-600 mt-2">
                  💡 <strong>Tip:</strong> Run <code className="bg-red-100 px-1 py-0.5 rounded">aws configure</code> to set up credentials.
                </p>
              )}
            </div>
          </div>
        </SectionCard>
      )}

      {/* Answer Display */}
      {response && (
        <>
          <SectionCard title="Answer">
            <div className="prose prose-sm max-w-none bg-green-50 border border-green-200 rounded-md p-4">
              <p className="text-gray-800 whitespace-pre-wrap">{response.answer}</p>
            </div>

            {response.reasoning && (
              <details className="mt-4">
                <summary className="cursor-pointer text-sm font-medium text-indigo-600 hover:text-indigo-700">
                  Show reasoning
                </summary>
                <p className="mt-2 text-sm text-gray-600 bg-gray-50 p-3 rounded-md whitespace-pre-wrap">
                  {response.reasoning}
                </p>
              </details>
            )}
          </SectionCard>

          {/* Citations */}
          <SectionCard title={`Citations (${response.citations.length})`}>
            {response.citations.length === 0 ? (
              <p className="text-gray-500 italic">No citations returned. The answer may be based on general knowledge or the documents don't contain relevant information.</p>
            ) : (
              <div className="space-y-4">
                {response.citations.map((citation, idx) => (
                  <div key={idx} className="border-l-4 border-indigo-400 pl-4 py-2 bg-gray-50 rounded-r-md">
                    <div className="flex items-start justify-between mb-2">
                      <div className="flex-1">
                        <span className="text-xs font-semibold text-indigo-700 uppercase tracking-wide">
                          Source {idx + 1}
                        </span>
                        <div className="flex items-center gap-2 mt-1 text-sm text-gray-600">
                          <span className="font-medium">
                            📄 {citation.filename || citation.s3_object?.split('/').pop() || 'Unknown document'}
                          </span>
                          {(citation.page !== null && citation.page !== undefined) && (
                            <span className="text-gray-500">• Page {citation.page}</span>
                          )}
                        </div>
                      </div>
                      {((citation.confidence !== null && citation.confidence !== undefined) || 
                        (citation.relevance !== null && citation.relevance !== undefined)) && (
                        <span className="text-xs bg-indigo-100 text-indigo-700 px-2 py-1 rounded-full">
                          {((citation.confidence || citation.relevance || 0) * 100).toFixed(0)}% match
                        </span>
                      )}
                    </div>
                    <p className="text-sm text-gray-700 italic mt-2 leading-relaxed">
                      "{citation.snippet || citation.text || 'No text available'}"
                    </p>
                  </div>
                ))}
              </div>
            )}
          </SectionCard>

          {/* Debug: Raw Response */}
          <SectionCard title="Debug Info">
            <button
              onClick={() => setShowRawResponse(!showRawResponse)}
              className="text-sm text-indigo-600 hover:text-indigo-700 font-medium"
            >
              {showRawResponse ? '▼ Hide' : '▶ Show'} raw AWS response
            </button>
            {showRawResponse && response.raw_response && (
              <pre className="mt-3 text-xs bg-gray-900 text-green-400 p-4 rounded-md overflow-auto max-h-96">
                {JSON.stringify(response.raw_response, null, 2)}
              </pre>
            )}
          </SectionCard>
        </>
      )}
    </div>
  );
}
