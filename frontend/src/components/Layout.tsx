import React, { useState } from 'react';
import { Network, MessageSquare, BarChart3, Activity } from 'lucide-react';

interface LayoutProps {
  children: React.ReactNode;
  activeTab: string;
  onTabChange: (tab: string) => void;
  health: { status: string; node_count: number; edge_count: number; llm_provider: string } | null;
}

const tabs = [
  { id: 'chat', label: 'Ask BI Questions', icon: MessageSquare },
  { id: 'graph', label: 'Knowledge Graph', icon: Network },
  { id: 'insights', label: 'Insights Dashboard', icon: BarChart3 },
];

export default function Layout({ children, activeTab, onTabChange, health }: LayoutProps) {
  return (
    <div className="min-h-screen flex flex-col">
      {/* Header */}
      <header className="border-b border-gray-800 bg-gray-900/80 backdrop-blur-sm sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
                <Network className="w-5 h-5 text-white" />
              </div>
              <div>
                <h1 className="text-lg font-bold text-white">Business Intelligence - GraphRAG & Vector RAG</h1>
                <p className="text-xs text-gray-400">Trends & Relationships in Corporate Data</p>
              </div>
            </div>

            {/* Status badge */}
            {health && (
              <div className="flex items-center gap-2 text-xs">
                <Activity className={`w-3.5 h-3.5 ${health.status === 'healthy' ? 'text-green-400' : 'text-red-400'}`} />
                <span className="text-gray-400">
                  {health.node_count} nodes · {health.edge_count} edges · {health.llm_provider}
                </span>
              </div>
            )}
          </div>

          {/* Tab bar */}
          <nav className="flex gap-1 -mb-px">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              const active = activeTab === tab.id;
              return (
                <button
                  key={tab.id}
                  onClick={() => onTabChange(tab.id)}
                  className={`flex items-center gap-2 px-4 py-3 text-sm font-medium border-b-2 transition-colors
                    ${active
                      ? 'border-blue-500 text-blue-400'
                      : 'border-transparent text-gray-400 hover:text-gray-200 hover:border-gray-600'
                    }`}
                >
                  <Icon className="w-4 h-4" />
                  {tab.label}
                </button>
              );
            })}
          </nav>
        </div>
      </header>

      {/* Main content */}
      <main className="flex-1 max-w-7xl mx-auto w-full px-4 sm:px-6 lg:px-8 py-6">
        {children}
      </main>
    </div>
  );
}
