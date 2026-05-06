import React, { useState, useRef, useEffect } from 'react';
import { Send, Loader2, Sparkles, ChevronRight, Network, FileText } from 'lucide-react';
import { queryGraph, QueryResponse } from '../api/client';

interface Message {
  id: string;
  type: 'user' | 'assistant';
  content: string;
  metadata?: {
    node_count: number;
    edge_count: number;
    matched_terms: string[];
    vector_chunks_used: number;
    retrieval_mode: string;
  };
}

const EXAMPLE_QUERIES = [
  "What are the top-selling products and what do quarterly reports say about them?",
  "Summarize the Engineering department's performance from memos and graph data",
  "Which region has the strongest revenue and what growth trends are reported?",
  "What do customer case studies reveal about our highest-spending clients?",
  "Show me quarterly revenue trends for 2024 vs 2025",
  "What strategic recommendations appear in our annual reviews?",
  "Who are the top-performing sales representatives?",
  "What product insights can you find across briefs and sales data?",
];

export default function ChatPanel() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSubmit = async (query: string) => {
    if (!query.trim() || loading) return;

    const userMsg: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: query,
    };
    setMessages((prev) => [...prev, userMsg]);
    setInput('');
    setLoading(true);

    try {
      const result = await queryGraph({ query, max_depth: 2 });
      const assistantMsg: Message = {
        id: (Date.now() + 1).toString(),
        type: 'assistant',
        content: result.answer,
        metadata: {
          node_count: result.subgraph.node_count,
          edge_count: result.subgraph.edge_count,
          matched_terms: result.subgraph.matched_terms,
          vector_chunks_used: result.vector_chunks_used || 0,
          retrieval_mode: result.retrieval_mode || 'graph_only',
        },
      };
      setMessages((prev) => [...prev, assistantMsg]);
    } catch (err: any) {
      const errMsg: Message = {
        id: (Date.now() + 1).toString(),
        type: 'assistant',
        content: `Error: ${err.message || 'Failed to get response'}. Make sure the API server is running.`,
      };
      setMessages((prev) => [...prev, errMsg]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-[calc(100vh-10rem)]">
      {/* Messages area */}
      <div className="flex-1 overflow-y-auto space-y-4 pb-4">
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center">
            <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-blue-500/20 to-purple-600/20 flex items-center justify-center mb-4">
              <Sparkles className="w-8 h-8 text-blue-400" />
            </div>
            <h2 className="text-xl font-semibold text-gray-200 mb-2">Ask Business Intelligence Questions</h2>
            <p className="text-gray-400 mb-6 max-w-md">
              Ask questions using natural language. The system combines knowledge graph context with business report insights for richer, data-driven answers.
            </p>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 max-w-2xl w-full">
              {EXAMPLE_QUERIES.map((q, i) => (
                <button
                  key={i}
                  onClick={() => handleSubmit(q)}
                  className="flex items-center gap-2 text-left px-4 py-3 rounded-lg bg-gray-800/50 border border-gray-700/50 text-sm text-gray-300 hover:bg-gray-800 hover:border-gray-600 transition-colors"
                >
                  <ChevronRight className="w-3.5 h-3.5 text-blue-400 flex-shrink-0" />
                  <span className="line-clamp-1">{q}</span>
                </button>
              ))}
            </div>
          </div>
        ) : (
          messages.map((msg) => (
            <div
              key={msg.id}
              className={`flex ${msg.type === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-[80%] rounded-2xl px-4 py-3 ${
                  msg.type === 'user'
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-800 border border-gray-700 text-gray-200'
                }`}
              >
                <div className="whitespace-pre-wrap text-sm leading-relaxed">{msg.content}</div>
                {msg.metadata && (
                  <div className="mt-2 pt-2 border-t border-gray-600/50">
                    <div className="flex items-center gap-2 mb-1">
                      {(msg.metadata.retrieval_mode === 'hybrid' || msg.metadata.retrieval_mode === 'graph_only') && (
                        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-blue-500/20 text-blue-300 text-xs">
                          <Network className="w-3 h-3" /> Graph
                        </span>
                      )}
                      {(msg.metadata.retrieval_mode === 'hybrid' || msg.metadata.retrieval_mode === 'vector_only') && msg.metadata.vector_chunks_used > 0 && (
                        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-purple-500/20 text-purple-300 text-xs">
                          <FileText className="w-3 h-3" /> Vector
                        </span>
                      )}
                    </div>
                    <div className="flex items-center gap-3 text-xs text-gray-400">
                      <span>{msg.metadata.node_count} nodes</span>
                      <span>{msg.metadata.edge_count} edges</span>
                      {msg.metadata.vector_chunks_used > 0 && (
                        <span>{msg.metadata.vector_chunks_used} doc chunks</span>
                      )}
                      <span className="truncate">Terms: {msg.metadata.matched_terms.join(', ')}</span>
                    </div>
                  </div>
                )}
              </div>
            </div>
          ))
        )}
        {loading && (
          <div className="flex justify-start">
            <div className="bg-gray-800 border border-gray-700 rounded-2xl px-4 py-3 flex items-center gap-2 text-sm text-gray-400">
              <Loader2 className="w-4 h-4 animate-spin" />
              Analyzing knowledge graph & knowledge base...
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input area */}
      <div className="border-t border-gray-800 pt-4">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSubmit(input);
          }}
          className="flex gap-2"
        >
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask a business intelligence question..."
            className="flex-1 bg-gray-800 border border-gray-700 rounded-xl px-4 py-3 text-sm text-gray-200 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500"
            disabled={loading}
          />
          <button
            type="submit"
            disabled={loading || !input.trim()}
            className="px-4 py-3 rounded-xl bg-blue-600 text-white hover:bg-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            <Send className="w-4 h-4" />
          </button>
        </form>
      </div>
    </div>
  );
}
