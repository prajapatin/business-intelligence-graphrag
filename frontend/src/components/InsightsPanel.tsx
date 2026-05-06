import React, { useEffect, useState } from 'react';
import { Loader2, TrendingUp, Users, ShoppingCart, Building2, Globe, Tag } from 'lucide-react';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  LineChart, Line, PieChart, Pie, Cell, Legend,
} from 'recharts';
import { getInsights, InsightsResponse } from '../api/client';

const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#8b5cf6', '#ef4444', '#ec4899', '#06b6d4', '#f97316'];

function formatCurrency(value: number) {
  if (value >= 1_000_000) return `$${(value / 1_000_000).toFixed(1)}M`;
  if (value >= 1_000) return `$${(value / 1_000).toFixed(0)}K`;
  return `$${value.toFixed(0)}`;
}

export default function InsightsPanel() {
  const [data, setData] = useState<InsightsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadInsights();
  }, []);

  const loadInsights = async () => {
    try {
      setLoading(true);
      const result = await getInsights();
      setData(result);
    } catch (err: any) {
      setError(err.message || 'Failed to load insights');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-[calc(100vh-10rem)]">
        <div className="flex items-center gap-3 text-gray-400">
          <Loader2 className="w-5 h-5 animate-spin" />
          Analyzing trends...
        </div>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="flex items-center justify-center h-[calc(100vh-10rem)]">
        <div className="bg-red-900/20 border border-red-800 rounded-xl p-6 text-center max-w-md">
          <p className="text-red-400 mb-2 font-medium">Failed to load insights</p>
          <p className="text-gray-400 text-sm">{error}</p>
          <button onClick={loadInsights} className="mt-4 px-4 py-2 bg-red-600 text-white rounded-lg text-sm hover:bg-red-500">
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Summary cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <SummaryCard
          icon={<ShoppingCart className="w-4 h-4" />}
          label="Total Revenue"
          value={formatCurrency(data.quarterly_revenue.reduce((sum, q) => sum + q.revenue, 0))}
          color="text-blue-400"
        />
        <SummaryCard
          icon={<Tag className="w-4 h-4" />}
          label="Products"
          value={String(data.top_products.length)}
          color="text-yellow-400"
        />
        <SummaryCard
          icon={<Users className="w-4 h-4" />}
          label="Active Customers"
          value={String(data.top_customers.length)}
          color="text-purple-400"
        />
        <SummaryCard
          icon={<Globe className="w-4 h-4" />}
          label="Regions"
          value={String(data.regional_distribution.length)}
          color="text-red-400"
        />
      </div>

      {/* Quarterly Revenue Trend */}
      <div className="bg-gray-900 border border-gray-800 rounded-xl p-5">
        <div className="flex items-center gap-2 mb-4">
          <TrendingUp className="w-4 h-4 text-blue-400" />
          <h3 className="text-sm font-semibold text-white">Quarterly Revenue Trend</h3>
        </div>
        <ResponsiveContainer width="100%" height={280}>
          <LineChart data={data.quarterly_revenue}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
            <XAxis dataKey="quarter" stroke="#64748b" fontSize={11} />
            <YAxis stroke="#64748b" fontSize={11} tickFormatter={(v) => formatCurrency(v)} />
            <Tooltip
              contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px' }}
              labelStyle={{ color: '#e2e8f0' }}
              formatter={(value: number) => [formatCurrency(value), 'Revenue']}
            />
            <Line type="monotone" dataKey="revenue" stroke="#3b82f6" strokeWidth={2} dot={{ fill: '#3b82f6', r: 4 }} />
          </LineChart>
        </ResponsiveContainer>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Top Products */}
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-5">
          <div className="flex items-center gap-2 mb-4">
            <ShoppingCart className="w-4 h-4 text-yellow-400" />
            <h3 className="text-sm font-semibold text-white">Top Products by Revenue</h3>
          </div>
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={data.top_products} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
              <XAxis type="number" stroke="#64748b" fontSize={11} tickFormatter={(v) => formatCurrency(v)} />
              <YAxis dataKey="product_name" type="category" stroke="#64748b" fontSize={10} width={120} />
              <Tooltip
                contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px' }}
                formatter={(value: number) => [formatCurrency(value), 'Revenue']}
              />
              <Bar dataKey="total_revenue" fill="#f59e0b" radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Regional Distribution */}
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-5">
          <div className="flex items-center gap-2 mb-4">
            <Globe className="w-4 h-4 text-red-400" />
            <h3 className="text-sm font-semibold text-white">Revenue by Region</h3>
          </div>
          <ResponsiveContainer width="100%" height={280}>
            <PieChart>
              <Pie
                data={data.regional_distribution}
                dataKey="total_revenue"
                nameKey="region_name"
                cx="50%"
                cy="50%"
                outerRadius={100}
                label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                labelLine={false}
                fontSize={11}
              >
                {data.regional_distribution.map((_, index) => (
                  <Cell key={index} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip
                contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px' }}
                formatter={(value: number) => [formatCurrency(value), 'Revenue']}
              />
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* Department Performance */}
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-5">
          <div className="flex items-center gap-2 mb-4">
            <Building2 className="w-4 h-4 text-green-400" />
            <h3 className="text-sm font-semibold text-white">Department Performance</h3>
          </div>
          <div className="space-y-3">
            {data.department_performance.map((dept, i) => (
              <div key={i} className="flex items-center justify-between text-sm">
                <div>
                  <span className="text-gray-200 font-medium">{dept.department_name}</span>
                  <span className="text-gray-500 text-xs ml-2">{dept.active_sellers} sellers · {dept.sales_count} sales</span>
                </div>
                <span className="text-green-400 font-semibold">{formatCurrency(dept.total_revenue)}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Category Breakdown */}
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-5">
          <div className="flex items-center gap-2 mb-4">
            <Tag className="w-4 h-4 text-orange-400" />
            <h3 className="text-sm font-semibold text-white">Category Breakdown</h3>
          </div>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={data.category_breakdown}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
              <XAxis dataKey="category_name" stroke="#64748b" fontSize={11} />
              <YAxis stroke="#64748b" fontSize={11} tickFormatter={(v) => formatCurrency(v)} />
              <Tooltip
                contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px' }}
                formatter={(value: number) => [formatCurrency(value), 'Revenue']}
              />
              <Bar dataKey="total_revenue" radius={[4, 4, 0, 0]}>
                {data.category_breakdown.map((_, index) => (
                  <Cell key={index} fill={COLORS[index % COLORS.length]} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Top Customers Table */}
      <div className="bg-gray-900 border border-gray-800 rounded-xl p-5">
        <div className="flex items-center gap-2 mb-4">
          <Users className="w-4 h-4 text-purple-400" />
          <h3 className="text-sm font-semibold text-white">Top Customers by Spend</h3>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-gray-400 border-b border-gray-800">
                <th className="pb-2 font-medium">#</th>
                <th className="pb-2 font-medium">Customer</th>
                <th className="pb-2 font-medium text-right">Total Spend</th>
                <th className="pb-2 font-medium text-right">Purchases</th>
              </tr>
            </thead>
            <tbody>
              {data.top_customers.map((cust, i) => (
                <tr key={i} className="border-b border-gray-800/50">
                  <td className="py-2 text-gray-500">{i + 1}</td>
                  <td className="py-2 text-gray-200">{cust.customer_name}</td>
                  <td className="py-2 text-right text-green-400 font-medium">{formatCurrency(cust.total_spend)}</td>
                  <td className="py-2 text-right text-gray-400">{cust.purchase_count}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

function SummaryCard({ icon, label, value, color }: { icon: React.ReactNode; label: string; value: string; color: string }) {
  return (
    <div className="bg-gray-900 border border-gray-800 rounded-xl p-4">
      <div className={`flex items-center gap-2 mb-1 ${color}`}>
        {icon}
        <span className="text-xs text-gray-400">{label}</span>
      </div>
      <p className="text-2xl font-bold text-white">{value}</p>
    </div>
  );
}
