import React, { useEffect, useState } from 'react';
import {
  ShieldCheckIcon,
  BoltIcon,
  ChartBarSquareIcon,
  ExclamationTriangleIcon,
} from '@heroicons/react/24/outline';
import { Line, Pie, Bar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  ArcElement,
  BarElement,
  Tooltip,
  Legend,
} from 'chart.js';
import StatCard from '../components/StatCard.jsx';
import ChartCard from '../components/ChartCard.jsx';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  ArcElement,
  BarElement,
  Tooltip,
  Legend
);

const Dashboard = () => {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);

  const computeScore = (report) => {
    if (typeof report?.security_score === 'number') return report.security_score;
    if (typeof report?.risk_score === 'number') return Math.max(0, 100 - report.risk_score);
    const sevWeights = { Critical: 25, High: 15, Medium: 8, Low: 2 };
    const risk = (report?.vulnerabilities || []).reduce(
      (acc, v) => acc + (sevWeights[v.severity] || 0),
      0
    );
    return Math.max(0, 100 - risk);
  };

  useEffect(() => {
    import('../lib/api.js').then(({ default: api }) => {
      api
        .get('/api/reports/history')
        .then((res) => setHistory(res.data.reports || []))
        .finally(() => setLoading(false));
    });
  }, []);

  const sortedHistory = [...history].sort(
    (a, b) => new Date(a.scan_date || 0) - new Date(b.scan_date || 0)
  );
  const totalScans = sortedHistory.length;
  const totalIssues = sortedHistory.reduce((sum, r) => sum + (r.total_vulnerabilities || 0), 0);
  const avgScore = totalScans
    ? Math.round(sortedHistory.reduce((s, r) => s + computeScore(r), 0) / totalScans)
    : 0;

  const severityCounts = history.reduce(
    (acc, r) => {
      (r.vulnerabilities || []).forEach((v) => {
        acc[v.severity] = (acc[v.severity] || 0) + 1;
      });
      return acc;
    },
    { Critical: 0, High: 0, Medium: 0, Low: 0 }
  );

  const severityData = {
    labels: ['Critical', 'High', 'Medium', 'Low'],
    datasets: [
      {
        data: [
          severityCounts.Critical,
          severityCounts.High,
          severityCounts.Medium,
          severityCounts.Low,
        ],
        backgroundColor: ['#EF4444', '#F97316', '#EAB308', '#22C55E'],
        borderWidth: 0,
      },
    ],
  };

  const recent = sortedHistory.slice(-6);
  const scoreData = {
    labels: recent.map((r) => `#${r.scan_id}`),
    datasets: [
      {
        label: 'Security Score',
        data: recent.map((r) => computeScore(r)),
        borderColor: '#22D3EE',
        backgroundColor: 'rgba(34,211,238,0.12)',
        tension: 0.35,
        fill: true,
        pointBackgroundColor: '#22D3EE',
        pointRadius: 4,
      },
    ],
  };

  const typeData = severityData;

  const chartOptions = {
    plugins: { legend: { display: false } },
    scales: {
      x: { ticks: { color: '#64748b' }, grid: { color: 'rgba(255,255,255,0.04)' } },
      y: { ticks: { color: '#64748b' }, grid: { color: 'rgba(255,255,255,0.04)' }, suggestedMin: 0, suggestedMax: 100 },
    },
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-end sm:justify-between gap-4">
        <div className="space-y-1">
          <p className="text-xs uppercase tracking-widest text-slate-500">Security Overview</p>
          <h1 className="text-2xl font-bold text-white">Welcome back, engineer.</h1>
          <p className="text-sm text-slate-500">Monitor scans, risks, and remediation velocity.</p>
        </div>
        <div className="flex items-center gap-2">
          <button className="px-4 py-2 rounded-xl bg-white/[0.04] border border-white/[0.08] text-slate-300 text-sm hover:bg-white/[0.08] transition">
            Create API Key
          </button>
          <button className="px-4 py-2 rounded-xl bg-gradient-to-r from-cyan-400 to-blue-600 text-white text-sm font-semibold shadow-[0_0_16px_rgba(34,211,238,0.3)] hover:shadow-[0_0_24px_rgba(34,211,238,0.45)] transition">
            New Scan
          </button>
        </div>
      </div>

      {/* Stat cards */}
      <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Total Scans"
          value={loading ? '—' : totalScans}
          subtext="All time"
          icon={BoltIcon}
          color="bg-cyan-500/20"
        />
        <StatCard
          title="Total Vulnerabilities"
          value={loading ? '—' : totalIssues}
          subtext="Across all scans"
          icon={ExclamationTriangleIcon}
          color="bg-red-500/20"
        />
        <StatCard
          title="Avg Security Score"
          value={loading ? '—' : avgScore}
          subtext="Out of 100"
          icon={ShieldCheckIcon}
          color="bg-accent/20"
        />
        <StatCard
          title="Recent Activity"
          value={loading ? '—' : `${Math.min(totalScans, 5)} scans`}
          subtext="Latest runs"
          icon={ChartBarSquareIcon}
          color="bg-white/10"
        />
      </div>

      {/* Charts */}
      <div className="grid lg:grid-cols-3 gap-4">
        <ChartCard title="Severity Distribution">
          <Pie
            data={severityData}
            options={{
              plugins: {
                legend: {
                  position: 'bottom',
                  labels: { color: '#94a3b8', boxWidth: 12, padding: 16 },
                },
              },
            }}
          />
        </ChartCard>
        <ChartCard title="Security Score Trend">
          <Line data={scoreData} options={chartOptions} />
        </ChartCard>
        <ChartCard title="Vulnerability Types">
          <Bar
            data={typeData}
            options={{
              ...chartOptions,
              plugins: { legend: { display: false } },
            }}
          />
        </ChartCard>
      </div>
    </div>
  );
};

export default Dashboard;
