import React, { useEffect, useState, useCallback, useRef } from 'react';
import { Loader2, ZoomIn, ZoomOut, Maximize2 } from 'lucide-react';
import { getGraph, GraphNode, GraphEdge } from '../api/client';

const NODE_COLORS: Record<string, string> = {
  Department: '#3b82f6',
  Employee: '#10b981',
  Product: '#f59e0b',
  Customer: '#8b5cf6',
  Region: '#ef4444',
  Industry: '#ec4899',
  Quarter: '#06b6d4',
  Category: '#f97316',
};

interface GraphData {
  nodes: GraphNode[];
  edges: GraphEdge[];
  statistics: Record<string, any>;
}

export default function GraphView() {
  const [data, setData] = useState<GraphData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null);
  const [filter, setFilter] = useState<string>('all');
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [graphModule, setGraphModule] = useState<any>(null);

  useEffect(() => {
    loadGraph();
  }, []);

  const loadGraph = async () => {
    try {
      setLoading(true);
      const result = await getGraph();
      setData(result);
    } catch (err: any) {
      setError(err.message || 'Failed to load graph');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-[calc(100vh-10rem)]">
        <div className="flex items-center gap-3 text-gray-400">
          <Loader2 className="w-5 h-5 animate-spin" />
          Loading knowledge graph...
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-[calc(100vh-10rem)]">
        <div className="bg-red-900/20 border border-red-800 rounded-xl p-6 text-center max-w-md">
          <p className="text-red-400 mb-2 font-medium">Failed to load graph</p>
          <p className="text-gray-400 text-sm">{error}</p>
          <button onClick={loadGraph} className="mt-4 px-4 py-2 bg-red-600 text-white rounded-lg text-sm hover:bg-red-500">
            Retry
          </button>
        </div>
      </div>
    );
  }

  if (!data) return null;

  const nodeTypes = Object.keys(data.statistics.node_types || {});
  const filteredNodes = filter === 'all' ? data.nodes : data.nodes.filter(n => n.node_type === filter);
  const filteredNodeIds = new Set(filteredNodes.map(n => n.id));
  const filteredEdges = data.edges.filter(e => filteredNodeIds.has(e.source) && filteredNodeIds.has(e.target));

  return (
    <div className="space-y-4">
      {/* Controls bar */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="text-sm text-gray-400">Filter by type:</span>
          <button
            onClick={() => setFilter('all')}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
              filter === 'all' ? 'bg-blue-600 text-white' : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
            }`}
          >
            All ({data.nodes.length})
          </button>
          {nodeTypes.map((type) => (
            <button
              key={type}
              onClick={() => setFilter(filter === type ? 'all' : type)}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors flex items-center gap-1.5 ${
                filter === type ? 'bg-blue-600 text-white' : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
              }`}
            >
              <span className="w-2 h-2 rounded-full" style={{ backgroundColor: NODE_COLORS[type] || '#666' }} />
              {type} ({data.statistics.node_types[type]})
            </button>
          ))}
        </div>
        <div className="text-sm text-gray-500">
          {filteredNodes.length} nodes · {filteredEdges.length} edges
        </div>
      </div>

      {/* Graph + Details panel */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-4">
        {/* Canvas graph visualization */}
        <div className="lg:col-span-3 bg-gray-900 border border-gray-800 rounded-xl overflow-hidden" style={{ height: 'calc(100vh - 16rem)' }}>
          <SimpleGraphCanvas
            nodes={filteredNodes}
            edges={filteredEdges}
            onNodeClick={setSelectedNode}
            selectedNode={selectedNode}
          />
        </div>

        {/* Details panel */}
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-4 overflow-y-auto" style={{ maxHeight: 'calc(100vh - 16rem)' }}>
          {selectedNode ? (
            <div>
              <div className="flex items-center gap-2 mb-3">
                <span className="w-3 h-3 rounded-full" style={{ backgroundColor: NODE_COLORS[selectedNode.node_type || ''] || '#666' }} />
                <span className="text-xs font-medium text-gray-400 uppercase">{selectedNode.node_type}</span>
              </div>
              <h3 className="text-lg font-semibold text-white mb-4">{selectedNode.name || selectedNode.id}</h3>
              <div className="space-y-2">
                {Object.entries(selectedNode)
                  .filter(([k]) => !['id', 'name', 'node_type'].includes(k))
                  .map(([key, value]) => (
                    <div key={key} className="flex justify-between text-sm">
                      <span className="text-gray-400">{key}</span>
                      <span className="text-gray-200 font-medium">{String(value)}</span>
                    </div>
                  ))}
              </div>
              {/* Connected edges */}
              <div className="mt-4 pt-4 border-t border-gray-800">
                <h4 className="text-sm font-medium text-gray-300 mb-2">Connections</h4>
                <div className="space-y-1">
                  {data.edges
                    .filter(e => e.source === selectedNode.id || e.target === selectedNode.id)
                    .slice(0, 20)
                    .map((edge, i) => {
                      const otherId = edge.source === selectedNode.id ? edge.target : edge.source;
                      const otherNode = data.nodes.find(n => n.id === otherId);
                      return (
                        <button
                          key={i}
                          onClick={() => otherNode && setSelectedNode(otherNode)}
                          className="w-full text-left text-xs px-2 py-1.5 rounded bg-gray-800/50 hover:bg-gray-800 transition-colors"
                        >
                          <span className="text-blue-400">{edge.relation}</span>
                          <span className="text-gray-500"> → </span>
                          <span className="text-gray-300">{otherNode?.name || otherId}</span>
                        </button>
                      );
                    })}
                </div>
              </div>
            </div>
          ) : (
            <div className="text-center text-gray-500 mt-8">
              <p className="text-sm">Click a node to see details</p>
            </div>
          )}

          {/* Statistics */}
          <div className="mt-6 pt-4 border-t border-gray-800">
            <h4 className="text-sm font-medium text-gray-300 mb-3">Graph Statistics</h4>
            <div className="space-y-2 text-xs">
              <div className="flex justify-between">
                <span className="text-gray-400">Total Nodes</span>
                <span className="text-white font-medium">{data.statistics.total_nodes}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Total Edges</span>
                <span className="text-white font-medium">{data.statistics.total_edges}</span>
              </div>
              {Object.entries(data.statistics.edge_types || {}).map(([type, count]) => (
                <div key={type} className="flex justify-between">
                  <span className="text-gray-500">{type}</span>
                  <span className="text-gray-400">{String(count)}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

/* ---------- Lightweight Canvas-based Force Graph ---------- */

interface SimpleGraphCanvasProps {
  nodes: GraphNode[];
  edges: GraphEdge[];
  onNodeClick: (node: GraphNode) => void;
  selectedNode: GraphNode | null;
}

interface SimNode extends GraphNode {
  x: number;
  y: number;
  vx: number;
  vy: number;
}

function SimpleGraphCanvas({ nodes, edges, onNodeClick, selectedNode }: SimpleGraphCanvasProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const simNodesRef = useRef<SimNode[]>([]);
  const animFrameRef = useRef<number>(0);
  const [dimensions, setDimensions] = useState({ width: 800, height: 600 });

  // Initialize simulation nodes
  useEffect(() => {
    simNodesRef.current = nodes.map((n, i) => ({
      ...n,
      x: dimensions.width / 2 + (Math.random() - 0.5) * dimensions.width * 0.6,
      y: dimensions.height / 2 + (Math.random() - 0.5) * dimensions.height * 0.6,
      vx: 0,
      vy: 0,
    }));
  }, [nodes, dimensions]);

  // Observe container size
  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;
    const ro = new ResizeObserver((entries) => {
      for (const entry of entries) {
        setDimensions({ width: entry.contentRect.width, height: entry.contentRect.height });
      }
    });
    ro.observe(container);
    return () => ro.disconnect();
  }, []);

  // Simple force-directed simulation + draw loop
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const nodeMap = new Map<string, SimNode>();
    simNodesRef.current.forEach(n => nodeMap.set(n.id, n));

    let iteration = 0;
    const MAX_ITERATIONS = 300;

    function tick() {
      if (!ctx) return;
      const simNodes = simNodesRef.current;
      if (iteration < MAX_ITERATIONS) {
        const alpha = 1 - iteration / MAX_ITERATIONS;
        const k = Math.sqrt((dimensions.width * dimensions.height) / Math.max(simNodes.length, 1));

        // Repulsion between all nodes
        for (let i = 0; i < simNodes.length; i++) {
          for (let j = i + 1; j < simNodes.length; j++) {
            let dx = simNodes[j].x - simNodes[i].x;
            let dy = simNodes[j].y - simNodes[i].y;
            let dist = Math.sqrt(dx * dx + dy * dy) || 1;
            let force = (k * k) / dist * alpha * 0.05;
            let fx = (dx / dist) * force;
            let fy = (dy / dist) * force;
            simNodes[i].vx -= fx;
            simNodes[i].vy -= fy;
            simNodes[j].vx += fx;
            simNodes[j].vy += fy;
          }
        }

        // Attraction along edges
        edges.forEach(edge => {
          const src = nodeMap.get(edge.source);
          const tgt = nodeMap.get(edge.target);
          if (!src || !tgt) return;
          let dx = tgt.x - src.x;
          let dy = tgt.y - src.y;
          let dist = Math.sqrt(dx * dx + dy * dy) || 1;
          let force = (dist - k * 0.5) * alpha * 0.005;
          let fx = (dx / dist) * force;
          let fy = (dy / dist) * force;
          src.vx += fx;
          src.vy += fy;
          tgt.vx -= fx;
          tgt.vy -= fy;
        });

        // Center gravity
        simNodes.forEach(n => {
          n.vx += (dimensions.width / 2 - n.x) * 0.001 * alpha;
          n.vy += (dimensions.height / 2 - n.y) * 0.001 * alpha;
        });

        // Apply velocities with damping
        simNodes.forEach(n => {
          n.vx *= 0.85;
          n.vy *= 0.85;
          n.x += n.vx;
          n.y += n.vy;
          // Bounds
          n.x = Math.max(20, Math.min(dimensions.width - 20, n.x));
          n.y = Math.max(20, Math.min(dimensions.height - 20, n.y));
        });

        iteration++;
      }

      // Draw
      ctx.clearRect(0, 0, dimensions.width, dimensions.height);

      // Edges
      ctx.lineWidth = 0.5;
      ctx.strokeStyle = 'rgba(100, 116, 139, 0.3)';
      edges.forEach(edge => {
        const src = nodeMap.get(edge.source);
        const tgt = nodeMap.get(edge.target);
        if (!src || !tgt) return;
        ctx.beginPath();
        ctx.moveTo(src.x, src.y);
        ctx.lineTo(tgt.x, tgt.y);
        ctx.stroke();
      });

      // Nodes
      simNodes.forEach(n => {
        const color = NODE_COLORS[n.node_type || ''] || '#666';
        const isSelected = selectedNode?.id === n.id;
        const radius = isSelected ? 7 : 5;

        ctx.beginPath();
        ctx.arc(n.x, n.y, radius, 0, Math.PI * 2);
        ctx.fillStyle = color;
        ctx.fill();

        if (isSelected) {
          ctx.strokeStyle = '#fff';
          ctx.lineWidth = 2;
          ctx.stroke();
        }

        // Label for selected or hovered
        if (isSelected) {
          ctx.font = '11px Inter, sans-serif';
          ctx.fillStyle = '#e2e8f0';
          ctx.textAlign = 'center';
          ctx.fillText(n.name || n.id, n.x, n.y - 12);
        }
      });

      animFrameRef.current = requestAnimationFrame(tick);
    }

    animFrameRef.current = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(animFrameRef.current);
  }, [nodes, edges, dimensions, selectedNode]);

  // Handle click
  const handleClick = useCallback((e: React.MouseEvent<HTMLCanvasElement>) => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const rect = canvas.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;

    const clicked = simNodesRef.current.find(n => {
      const dx = n.x - x;
      const dy = n.y - y;
      return Math.sqrt(dx * dx + dy * dy) < 10;
    });

    if (clicked) {
      onNodeClick(clicked);
    }
  }, [onNodeClick]);

  return (
    <div ref={containerRef} className="w-full h-full relative">
      <canvas
        ref={canvasRef}
        width={dimensions.width}
        height={dimensions.height}
        onClick={handleClick}
        className="cursor-crosshair"
      />
      {/* Legend */}
      <div className="absolute bottom-3 left-3 bg-gray-900/90 backdrop-blur-sm border border-gray-700 rounded-lg p-2 flex flex-wrap gap-x-3 gap-y-1">
        {Object.entries(NODE_COLORS).map(([type, color]) => (
          <div key={type} className="flex items-center gap-1.5 text-xs text-gray-400">
            <span className="w-2 h-2 rounded-full" style={{ backgroundColor: color }} />
            {type}
          </div>
        ))}
      </div>
    </div>
  );
}
