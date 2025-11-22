import { useState } from 'react'
import { SectionCard } from '../components/SectionCard'

interface Message {
  role: 'user' | 'assistant'
  content: string
  source?: string
}

interface DocumentStatus {
  loaded: boolean
  files: string[]
}

export const ClearClausePanel = () => {
  const [messages, setMessages] = useState<Message[]>([])
  const [question, setQuestion] = useState('')
  const [useDocument, setUseDocument] = useState(false)
  const [documentStatus, setDocumentStatus] = useState<DocumentStatus>({ loaded: false, files: [] })
  const [status, setStatus] = useState<{ loading: boolean; error?: string }>({ loading: false })
  
  // Translation state
  const [textToTranslate, setTextToTranslate] = useState('')
  const [translatedText, setTranslatedText] = useState('')
  const [targetLanguage, setTargetLanguage] = useState<'Hindi' | 'Kannada'>('Hindi')
  
  // Summarization state
  const [summaryInstruction, setSummaryInstruction] = useState('Provide a comprehensive summary')
  const [summary, setSummary] = useState('')

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files
    if (!files || files.length === 0) return

    setStatus({ loading: true })
    const formData = new FormData()
    Array.from(files).forEach(file => formData.append('files', file))

    try {
      const response = await fetch('http://localhost:8000/api/clearclause/upload', {
        method: 'POST',
        body: formData,
      })
      
      if (!response.ok) throw new Error('Upload failed')
      
      const data = await response.json()
      setDocumentStatus({ loaded: true, files: data.files })
      setStatus({ loading: false })
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: `✅ Successfully uploaded ${data.files.length} document(s): ${data.files.join(', ')}`
      }])
    } catch (error) {
      setStatus({ loading: false, error: error instanceof Error ? error.message : 'Upload failed' })
    }
  }

  const handleAskQuestion = async () => {
    if (!question.trim()) return

    const userMessage: Message = { role: 'user', content: question }
    setMessages(prev => [...prev, userMessage])
    setStatus({ loading: true })

    try {
      const response = await fetch('http://localhost:8000/api/clearclause/ask', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question, use_document: useDocument }),
      })
      
      if (!response.ok) throw new Error('Question failed')
      
      const data = await response.json()
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: data.answer,
        source: data.source
      }])
      setQuestion('')
      setStatus({ loading: false })
    } catch (error) {
      setStatus({ loading: false, error: error instanceof Error ? error.message : 'Question failed' })
    }
  }

  const handleSummarize = async () => {
    if (!documentStatus.loaded) {
      setStatus({ loading: false, error: 'Please upload documents first' })
      return
    }

    setStatus({ loading: true })
    try {
      const response = await fetch('http://localhost:8000/api/clearclause/summarize', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ instruction: summaryInstruction }),
      })
      
      if (!response.ok) throw new Error('Summarization failed')
      
      const data = await response.json()
      setSummary(data.summary)
      setStatus({ loading: false })
    } catch (error) {
      setStatus({ loading: false, error: error instanceof Error ? error.message : 'Summarization failed' })
    }
  }

  const handleTranslate = async () => {
    if (!textToTranslate.trim()) return

    setStatus({ loading: true })
    try {
      const response = await fetch('http://localhost:8000/api/clearclause/translate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: textToTranslate, target_language: targetLanguage }),
      })
      
      if (!response.ok) throw new Error('Translation failed')
      
      const data = await response.json()
      setTranslatedText(data.translated)
      setStatus({ loading: false })
    } catch (error) {
      setStatus({ loading: false, error: error instanceof Error ? error.message : 'Translation failed' })
    }
  }

  return (
    <div className="space-y-6">
      {/* Document Upload Section */}
      <SectionCard
        title="📄 Document Upload"
        description="Upload PDF or DOCX legal documents for analysis"
      >
        <div className="space-y-4">
          <div className="rounded-xl border-2 border-dashed border-brand-300 bg-brand-50 p-8 text-center">
            <input
              type="file"
              id="file-upload"
              className="hidden"
              accept=".pdf,.docx"
              multiple
              onChange={handleFileUpload}
            />
            <label htmlFor="file-upload" className="cursor-pointer">
              <div className="text-4xl mb-2">📁</div>
              <p className="text-sm font-semibold text-brand-600">
                Click to upload documents
              </p>
              <p className="text-xs text-slate-500 mt-1">PDF or DOCX files</p>
            </label>
          </div>
          
          {documentStatus.loaded && (
            <div className="rounded-xl bg-emerald-50 border border-emerald-200 p-4">
              <p className="text-sm font-semibold text-emerald-700">✅ Documents loaded</p>
              <ul className="mt-2 text-xs text-emerald-600 list-disc list-inside">
                {documentStatus.files.map(file => <li key={file}>{file}</li>)}
              </ul>
            </div>
          )}
        </div>
      </SectionCard>

      {/* Q&A Section */}
      <SectionCard
        title="💬 Ask Questions"
        description="Ask questions about your uploaded documents or general legal queries"
      >
        <div className="space-y-4">
          {/* Chat Messages */}
          <div className="h-64 overflow-y-auto space-y-3 rounded-xl bg-slate-50 p-4">
            {messages.length === 0 ? (
              <p className="text-sm text-slate-400 text-center py-8">No messages yet. Ask a question!</p>
            ) : (
              messages.map((msg, idx) => (
                <div
                  key={idx}
                  className={`rounded-xl p-3 ${
                    msg.role === 'user'
                      ? 'bg-brand-500 text-white ml-8'
                      : 'bg-white border border-slate-200 mr-8'
                  }`}
                >
                  <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
                  {msg.source && (
                    <span className="text-xs opacity-70 mt-1 block">Source: {msg.source}</span>
                  )}
                </div>
              ))
            )}
          </div>

          {/* Question Input */}
          <div className="space-y-2">
            <textarea
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder="Type your question here..."
              className="w-full rounded-xl border border-slate-200 bg-white p-3 text-sm text-slate-800 resize-none"
              rows={3}
            />
            
            <div className="flex items-center gap-3">
              <label className="flex items-center gap-2 text-sm text-slate-600">
                <input
                  type="checkbox"
                  checked={useDocument}
                  onChange={(e) => setUseDocument(e.target.checked)}
                  className="rounded"
                />
                Use uploaded documents
              </label>
              
              <button
                onClick={handleAskQuestion}
                disabled={status.loading || !question.trim()}
                className="ml-auto rounded-full bg-brand-500 px-6 py-2 text-sm font-semibold text-white hover:bg-brand-600 disabled:opacity-50"
              >
                {status.loading ? 'Asking...' : 'Ask'}
              </button>
            </div>
          </div>
        </div>
      </SectionCard>

      {/* Summarization Section */}
      <SectionCard
        title="📝 Summarize Documents"
        description="Generate custom summaries of your uploaded documents"
      >
        <div className="space-y-4">
          <textarea
            value={summaryInstruction}
            onChange={(e) => setSummaryInstruction(e.target.value)}
            placeholder="Enter summarization instruction..."
            className="w-full rounded-xl border border-slate-200 bg-white p-3 text-sm text-slate-800 resize-none"
            rows={2}
          />
          
          <button
            onClick={handleSummarize}
            disabled={status.loading || !documentStatus.loaded}
            className="rounded-full bg-brand-500 px-6 py-2 text-sm font-semibold text-white hover:bg-brand-600 disabled:opacity-50"
          >
            {status.loading ? 'Summarizing...' : 'Generate Summary'}
          </button>

          {summary && (
            <div className="rounded-xl bg-blue-50 border border-blue-200 p-4">
              <h4 className="text-sm font-semibold text-blue-900 mb-2">Summary:</h4>
              <p className="text-sm text-blue-800 whitespace-pre-wrap">{summary}</p>
            </div>
          )}
        </div>
      </SectionCard>

      {/* Translation Section */}
      <SectionCard
        title="🌐 Translate Text"
        description="Translate English legal text to Hindi or Kannada"
      >
        <div className="space-y-4">
          <div className="flex gap-3">
            <label className="flex items-center gap-2 text-sm text-slate-700">
              <input
                type="radio"
                name="language"
                value="Hindi"
                checked={targetLanguage === 'Hindi'}
                onChange={() => setTargetLanguage('Hindi')}
              />
              Hindi
            </label>
            <label className="flex items-center gap-2 text-sm text-slate-700">
              <input
                type="radio"
                name="language"
                value="Kannada"
                checked={targetLanguage === 'Kannada'}
                onChange={() => setTargetLanguage('Kannada')}
              />
              Kannada
            </label>
          </div>

          <textarea
            value={textToTranslate}
            onChange={(e) => setTextToTranslate(e.target.value)}
            placeholder="Enter English text to translate..."
            className="w-full rounded-xl border border-slate-200 bg-white p-3 text-sm text-slate-800 resize-none"
            rows={3}
          />
          
          <button
            onClick={handleTranslate}
            disabled={status.loading || !textToTranslate.trim()}
            className="rounded-full bg-brand-500 px-6 py-2 text-sm font-semibold text-white hover:bg-brand-600 disabled:opacity-50"
          >
            {status.loading ? 'Translating...' : 'Translate'}
          </button>

          {translatedText && (
            <div className="rounded-xl bg-purple-50 border border-purple-200 p-4">
              <h4 className="text-sm font-semibold text-purple-900 mb-2">Translated ({targetLanguage}):</h4>
              <p className="text-sm text-purple-800 whitespace-pre-wrap">{translatedText}</p>
            </div>
          )}
        </div>
      </SectionCard>

      {/* Error Display */}
      {status.error && (
        <div className="rounded-xl bg-rose-50 border border-rose-200 p-4">
          <p className="text-sm text-rose-700">❌ {status.error}</p>
        </div>
      )}
    </div>
  )
}
