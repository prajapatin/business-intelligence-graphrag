import React, { useEffect, useState } from 'react';
import Layout from './components/Layout';
import ChatPanel from './components/ChatPanel';
import GraphView from './components/GraphView';
import InsightsPanel from './components/InsightsPanel';
import { getHealth, HealthResponse } from './api/client';

export default function App() {
  const [activeTab, setActiveTab] = useState('chat');
  const [health, setHealth] = useState<HealthResponse | null>(null);

  useEffect(() => {
    getHealth()
      .then(setHealth)
      .catch(() => setHealth(null));
  }, []);

  return (
    <Layout activeTab={activeTab} onTabChange={setActiveTab} health={health}>
      {activeTab === 'chat' && <ChatPanel />}
      {activeTab === 'graph' && <GraphView />}
      {activeTab === 'insights' && <InsightsPanel />}
    </Layout>
  );
}
