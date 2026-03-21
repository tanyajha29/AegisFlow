import React, { useEffect, useState } from 'react';
import {
  ShieldCheckIcon,
  BoltIcon,
  ChartBarSquareIcon,
  ExclamationTriangleIcon,
} from '@heroicons/react/24/outline';
import { Line, Pie, Bar } from 'react-chartjs-2';
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, ArcElement, BarElement, Tooltip, Legend } from 'chart.js';
import StatCard from '../components/StatCard.jsx';
import ChartCard from '../components/ChartCard.jsx';

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, ArcElement, BarElement, Tooltip, Legend);

const Dashboard = () => {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);

  const computeScore = (report) => {
    if (typeof report?.security_score === 'number') return report.security_score;
    if (typeof report?.risk_score === 'number') return Math.max(0, 100 - report.risk_score);
    const sevWeights = { Critical: 25, High: 15, Medium: 8, Low: 2 };
    const risk = (report?.vulnerabilities || []).reduce((acc, v) => acc + (sevWeights[v.severity] || 0), 0);
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
        data: [severityCounts.Critical, severityCounts.High, severityCounts.Medium, severityCounts.Low],
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
        backgroundColor: 'rgba(34,211,238,0.15)',
        tension: 0.35,
        fill: true,
      },
    ],
  };

  const typeData = severityData; // placeholder since API doesn't classify types yet

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-xs uppercase tracking-[0.2em] text-slate-500">Security Overview</p>
          <h1 className="text-3xl font-semibold text-white">Welcome back, engineer.</h1>
          <p className="text-slate-500 text-sm">Monitor scans, risks, and remediation velocity.</p>
        </div>
        <div className="hidden md:flex items-center gap-3">
          <button className="px-4 py-2 rounded-xl bg-white/5 border border-border text-slate-200">Create API Key</button>
          <button className="px-4 py-2 rounded-xl bg-gradient-to-r from-cyber to-accent text-white shadow-glow">New Scan</button>
        </div>
      </div>

      <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard title="Total Scans" value={totalScans} subtext="All time" icon={BoltIcon} color="bg-cyber/80" />
        <StatCard title="Total Vulnerabilities" value={totalIssues} subtext="Across scans" icon={ExclamationTriangleIcon} color="bg-critical/80" />
        <StatCard title="Average Security Score" value={avgScore} subtext="Across scans" icon={ShieldCheckIcon} color="bg-accent/70" />
        <StatCard title="Recent Activity" value={`${Math.min(totalScans, 5)} scans`} subtext="Latest runs" icon={ChartBarSquareIcon} color="bg-white/10" />
      </div>

      <div className="grid lg:grid-cols-3 gap-4">
        <ChartCard title="Severity Distribution">
          <Pie data={severityData} options={{ plugins: { legend: { position: 'bottom', labels: { color: '#cbd5e1' } } } }} />
        </ChartCard>
        <ChartCard title="Security Score Trend">
          <Line
            data={scoreData}
            options={{
              plugins: { legend: { display: false } },
              scales: {
                x: { ticks: { color: '#cbd5e1' } },
                y: { ticks: { color: '#cbd5e1' }, suggestedMin: 0, suggestedMax: 100 },
              },
            }}
          />
        </ChartCard>
        <ChartCard title="Vulnerability Types">
          <Bar data={typeData} options={{ plugins: { legend: { display: false } }, scales: { x: { ticks: { color: '#cbd5e1' } }, y: { ticks: { color: '#cbd5e1' } } } }} />
        </ChartCard>
      </div>
    </div>
  );
};

export default Dashboard;
