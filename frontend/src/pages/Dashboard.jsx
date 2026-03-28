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
import GlassCard from '../components/GlassCard.jsx';
import SectionHeader from '../components/SectionHeader.jsx';
import { Button } from '../components/ui/button';

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

  const recentSummaries = [...sortedHistory].reverse().slice(0, 4);

  return (
    <div className="space-y-8">
      <SectionHeader
        eyebrow="Security Overview"
        title="Command Center"
        description="Monitor scans, risk posture, and remediation momentum in a single, glassy dashboard."
        actions={
          <>
            <Button variant="outline" size="sm" className="border-white/15 text-slate-100">
              Create API Key
            </Button>
            <Button size="sm" className="shadow-[0_0_24px_rgba(34,211,238,0.35)]">
              New Scan
            </Button>
          </>
        }
      />

      {/* Stat cards */}
      <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Total Scans"
          value={loading ? '—' : totalScans}
          subtext="All time"
          icon={BoltIcon}
          tone="cyan"
        />
        <StatCard
          title="Total Vulnerabilities"
          value={loading ? '—' : totalIssues}
          subtext="Across all scans"
          icon={ExclamationTriangleIcon}
          tone="amber"
        />
        <StatCard
          title="Avg Security Score"
          value={loading ? '—' : avgScore}
          subtext="Out of 100"
          icon={ShieldCheckIcon}
          tone="blue"
        />
        <StatCard
          title="Recent Activity"
          value={loading ? '—' : `${Math.min(totalScans, 5)} scans`}
          subtext="Latest runs"
          icon={ChartBarSquareIcon}
          tone="green"
        />
      </div>

      {/* Highlight banner */}
      <GlassCard tone="accent" className="p-5">
        <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
          <div className="space-y-1">
            <p className="text-xs uppercase tracking-[0.24em] text-slate-400">Live posture</p>
            <p className="text-lg font-semibold text-white">Security score trending at {loading ? '—' : `${avgScore}/100`}</p>
            <p className="text-sm text-slate-400">
              Keep momentum by scheduling your next scan and sharing reports with stakeholders.
            </p>
          </div>
          <div className="flex gap-3">
            <Button variant="outline" size="sm" className="border-white/15 text-slate-100">
              View Reports
            </Button>
            <Button size="sm" className="shadow-[0_0_24px_rgba(34,211,238,0.35)]">
              Schedule Scan
            </Button>
          </div>
        </div>
      </GlassCard>

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

      {/* Recent scans list */}
      <GlassCard className="p-5">
        <div className="flex items-center justify-between mb-3">
          <div>
            <p className="text-xs uppercase tracking-[0.24em] text-slate-500">Recent scans</p>
            <p className="text-sm text-slate-300">Latest activity across your workspace</p>
          </div>
          <span className="px-3 py-1 rounded-full text-xs bg-white/5 border border-white/10 text-slate-200">
            {recentSummaries.length} shown
          </span>
        </div>
        <div className="grid md:grid-cols-2 gap-3">
          {recentSummaries.map((item) => (
            <div
              key={item.scan_id}
              className="flex items-center justify-between rounded-xl border border-white/10 bg-white/5 px-4 py-3 hover:border-accent/30 transition"
            >
              <div className="min-w-0">
                <p className="text-sm text-white font-semibold truncate">
                  {item.display_file_name || item.file_name}
                </p>
                <p className="text-xs text-slate-500">Scan #{item.scan_id}</p>
              </div>
              <div className="text-right">
                <p className="text-sm font-semibold text-accent">{computeScore(item)}</p>
                <p className="text-xs text-slate-500">{new Date(item.scan_date || 0).toLocaleDateString()}</p>
              </div>
            </div>
          ))}
        </div>
      </GlassCard>
    </div>
  );
};

export default Dashboard;
