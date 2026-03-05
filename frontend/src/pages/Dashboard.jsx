import React from 'react';
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
  const severityData = {
    labels: ['Critical', 'High', 'Medium', 'Low'],
    datasets: [
      {
        data: [4, 9, 14, 22],
        backgroundColor: ['#EF4444', '#F97316', '#EAB308', '#22C55E'],
        borderWidth: 0,
      },
    ],
  };

  const scoreData = {
    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
    datasets: [
      {
        label: 'Security Score',
        data: [68, 73, 76, 82, 84, 87],
        borderColor: '#22D3EE',
        backgroundColor: 'rgba(34,211,238,0.15)',
        tension: 0.35,
        fill: true,
      },
    ],
  };

  const typeData = {
    labels: ['Secrets', 'SAST', 'Dependencies', 'Config'],
    datasets: [
      {
        data: [18, 26, 12, 8],
        backgroundColor: ['#22D3EE', '#2563EB', '#EAB308', '#EF4444'],
        borderRadius: 8,
      },
    ],
  };

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
        <StatCard title="Total Scans" value="184" subtext="Last 30 days" icon={BoltIcon} color="bg-cyber/80" />
        <StatCard title="Total Vulnerabilities" value="47" subtext="-12% vs last month" icon={ExclamationTriangleIcon} color="bg-critical/80" />
        <StatCard title="Average Security Score" value="87" subtext="Across active projects" icon={ShieldCheckIcon} color="bg-accent/70" />
        <StatCard title="Recent Activity" value="12 scans" subtext="Past 24 hours" icon={ChartBarSquareIcon} color="bg-white/10" />
      </div>

      <div className="grid lg:grid-cols-3 gap-4">
        <ChartCard title="Severity Distribution">
          <Pie data={severityData} options={{ plugins: { legend: { position: 'bottom', labels: { color: '#cbd5e1' } } } }} />
        </ChartCard>
        <ChartCard title="Security Score Trend">
          <Line data={scoreData} options={{ plugins: { legend: { display: false } }, scales: { x: { ticks: { color: '#cbd5e1' } }, y: { ticks: { color: '#cbd5e1' }, min: 50, max: 100 } } }} />
        </ChartCard>
        <ChartCard title="Vulnerability Types">
          <Bar data={typeData} options={{ plugins: { legend: { display: false } }, scales: { x: { ticks: { color: '#cbd5e1' } }, y: { ticks: { color: '#cbd5e1' } } } }} />
        </ChartCard>
      </div>
    </div>
  );
};

export default Dashboard;
