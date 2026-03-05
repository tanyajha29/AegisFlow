import React, { useState, useRef, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import axios from 'axios';
import { DocumentTextIcon, DocumentArrowUpIcon, BeakerIcon, ClockIcon, ShieldExclamationIcon } from '@heroicons/react/24/outline';
import { Line } from 'react-chartjs-2';
import {
    Chart as ChartJS,
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    Title,
    Tooltip,
    Legend
} from 'chart.js';

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend);

const Dashboard = () => {
    const [tab, setTab] = useState('paste'); // 'paste' or 'upload'
    const [scanTitle, setScanTitle] = useState('');
    const [codeContent, setCodeContent] = useState('');
    const [file, setFile] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [history, setHistory] = useState([]);
    const [historyLoading, setHistoryLoading] = useState(true);
    const fileInputRef = useRef(null);
    const navigate = useNavigate();

    const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

    useEffect(() => {
        const fetchHistory = async () => {
            try {
                const response = await axios.get(`${API_BASE}/scans/`);
                setHistory(response.data);
            } catch (err) {
                console.error("Failed to load history", err);
            } finally {
                setHistoryLoading(false);
            }
        };
        fetchHistory();
    }, [API_BASE]);

    const handleFileChange = (e) => {
        if (e.target.files && e.target.files[0]) {
            setFile(e.target.files[0]);
        }
    };

    const handleScan = async () => {
        if (!scanTitle) {
            setError("Please provide a scan title");
            return;
        }

        if (tab === 'paste' && !codeContent) {
            setError("Please paste some code to scan");
            return;
        }

        if (tab === 'upload' && !file) {
            setError("Please select a file to upload");
            return;
        }

        setLoading(true);
        setError('');

        const formData = new FormData();
        formData.append('title', scanTitle);

        if (tab === 'paste') {
            formData.append('code_content', codeContent);
        } else {
            formData.append('file', file);
        }

        try {
            const response = await axios.post(`${API_BASE}/scans/upload`, formData, {
                headers: {
                    'Content-Type': 'multipart/form-data'
                }
            });
            navigate(`/report/${response.data.id}`);
        } catch (err) {
            console.error(err);
            setError(err.response?.data?.detail || "An error occurred during scanning");
            setLoading(false);
        }
    };

    // Calculate aggregated stats
    const totalScans = history.length;
    const avgRiskScore = totalScans > 0
        ? Math.round(history.reduce((acc, curr) => acc + curr.risk_score, 0) / totalScans)
        : 0;

    // Prepare chart data (Chronological order)
    const chartData = {
        labels: history.slice().reverse().map(scan => new Date(scan.created_at).toLocaleDateString()),
        datasets: [
            {
                label: 'Risk Score Trend',
                data: history.slice().reverse().map(scan => scan.risk_score),
                borderColor: 'rgba(59, 130, 246, 1)',
                backgroundColor: 'rgba(59, 130, 246, 0.2)',
                tension: 0.4,
                pointBackgroundColor: 'rgba(59, 130, 246, 1)',
            }
        ]
    };

    const chartOptions = {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
            y: {
                beginAtZero: true,
                max: 100,
                grid: { color: 'rgba(255, 255, 255, 0.1)' },
                ticks: { color: 'rgba(200, 200, 200, 0.8)' }
            },
            x: {
                grid: { display: false },
                ticks: { color: 'rgba(200, 200, 200, 0.8)' }
            }
        },
        plugins: {
            legend: { display: false }
        }
    };

    return (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">

            <div className="mb-8">
                <h1 className="text-3xl font-bold text-white tracking-tight">Dashboard Overview</h1>
                <p className="mt-2 text-slate-400">Monitor your security posture and analyze new code.</p>
            </div>

            {/* Top Stats & Chart Row */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
                {/* Stats */}
                <div className="flex flex-col gap-6">
                    <div className="bg-dark/50 border border-white/10 rounded-2xl p-6 shadow-xl backdrop-blur-sm flex items-center justify-between">
                        <div>
                            <p className="text-sm font-medium text-slate-400">Total Scans</p>
                            <h2 className="text-4xl font-bold text-white mt-2">{totalScans}</h2>
                        </div>
                        <div className="w-12 h-12 rounded-full bg-blue-500/20 flex items-center justify-center">
                            <ClockIcon className="w-6 h-6 text-blue-400" />
                        </div>
                    </div>

                    <div className="bg-dark/50 border border-white/10 rounded-2xl p-6 shadow-xl backdrop-blur-sm flex items-center justify-between">
                        <div>
                            <p className="text-sm font-medium text-slate-400">Average Risk Score</p>
                            <h2 className="text-4xl font-bold text-white mt-2">{avgRiskScore}</h2>
                        </div>
                        <div className="w-12 h-12 rounded-full bg-orange-500/20 flex items-center justify-center">
                            <ShieldExclamationIcon className="w-6 h-6 text-orange-400" />
                        </div>
                    </div>
                </div>

                {/* Chart */}
                <div className="lg:col-span-2 bg-dark/50 border border-white/10 rounded-2xl p-6 shadow-xl backdrop-blur-sm">
                    <h3 className="text-sm font-medium text-slate-400 mb-4">Risk Score Trend</h3>
                    <div className="h-48 w-full">
                        {totalScans > 0 ? (
                            <Line data={chartData} options={chartOptions} />
                        ) : (
                            <div className="h-full flex items-center justify-center text-slate-500 text-sm">
                                Not enough data to display trend
                            </div>
                        )}
                    </div>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                {/* Left Column: Scan history */}
                <div className="bg-dark/50 border border-white/10 rounded-2xl shadow-xl backdrop-blur-sm overflow-hidden flex flex-col h-[600px]">
                    <div className="p-6 border-b border-white/10 bg-dark/80">
                        <h2 className="text-xl font-bold text-white">Recent Scans</h2>
                    </div>
                    <div className="overflow-y-auto flex-1 p-2">
                        {historyLoading ? (
                            <div className="p-8 text-center text-slate-400">Loading history...</div>
                        ) : history.length === 0 ? (
                            <div className="p-8 text-center text-slate-500">No scans found. Start your first scan!</div>
                        ) : (
                            <div className="space-y-2">
                                {history.map(scan => (
                                    <Link key={scan.id} to={`/report/${scan.id}`} className="block bg-white/[0.02] hover:bg-white/[0.05] border border-white/5 rounded-xl p-4 transition-colors">
                                        <div className="flex justify-between items-start mb-2">
                                            <h3 className="text-white font-medium truncate pr-4">{scan.title}</h3>
                                            <span className={`px-2 py-1 text-xs font-semibold rounded-full border ${scan.risk_score > 70 ? 'bg-red-500/10 text-red-400 border-red-500/20' : scan.risk_score > 40 ? 'bg-orange-500/10 text-orange-400 border-orange-500/20' : 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'}`}>
                                                Risk: {scan.risk_score}
                                            </span>
                                        </div>
                                        <div className="flex justify-between text-xs text-slate-500">
                                            <span>{new Date(scan.created_at).toLocaleString()}</span>
                                            <span className="capitalize">{scan.status}</span>
                                        </div>
                                    </Link>
                                ))}
                            </div>
                        )}
                    </div>
                </div>

                {/* Right Column: New Scan Form */}
                <div className="bg-dark/50 border border-white/10 rounded-2xl p-6 shadow-xl backdrop-blur-sm h-[600px] flex flex-col">
                    <h2 className="text-xl font-bold text-white mb-6">Run New Scan</h2>

                    {error && (
                        <div className="mb-4 bg-red-500/10 border border-red-500/50 text-red-400 px-4 py-3 rounded-lg text-sm">
                            {error}
                        </div>
                    )}

                    <div className="mb-4">
                        <label className="block text-sm font-medium text-slate-300 mb-2">Scan Title or Reference</label>
                        <input
                            type="text"
                            className="w-full bg-darker border border-white/10 rounded-lg px-4 py-3 text-white focus:ring-2 focus:ring-primary focus:border-transparent outline-none transition-all placeholder-slate-600"
                            placeholder="e.g. Authentication Service Fixes"
                            value={scanTitle}
                            onChange={(e) => setScanTitle(e.target.value)}
                        />
                    </div>

                    <div className="mb-4 border-b border-white/10 flex shrink-0">
                        <button
                            className={`pb-3 px-4 text-sm font-medium transition-colors flex items-center ${tab === 'paste' ? 'text-primary border-b-2 border-primary' : 'text-slate-400 hover:text-slate-200'}`}
                            onClick={() => setTab('paste')}
                        >
                            <DocumentTextIcon className="w-5 h-5 mr-2" />
                            Paste Code
                        </button>
                        <button
                            className={`pb-3 px-4 text-sm font-medium transition-colors flex items-center ${tab === 'upload' ? 'text-primary border-b-2 border-primary' : 'text-slate-400 hover:text-slate-200'}`}
                            onClick={() => setTab('upload')}
                        >
                            <DocumentArrowUpIcon className="w-5 h-5 mr-2" />
                            Upload File
                        </button>
                    </div>

                    <div className="flex-1 overflow-y-auto mb-4">
                        {tab === 'paste' ? (
                            <textarea
                                className="w-full h-full min-h-[150px] bg-darker border border-white/10 rounded-lg p-4 text-slate-300 font-mono text-sm focus:ring-2 focus:ring-primary focus:border-transparent outline-none transition-all resize-none placeholder-slate-600"
                                placeholder="# Paste your Python, JS, JSON or Text file content here..."
                                value={codeContent}
                                onChange={(e) => setCodeContent(e.target.value)}
                            ></textarea>
                        ) : (
                            <div
                                className="h-full min-h-[150px] border-2 border-dashed border-slate-600 hover:border-primary/50 bg-darker/50 rounded-xl flex flex-col items-center justify-center transition-colors cursor-pointer"
                                onClick={() => fileInputRef.current?.click()}
                            >
                                <input
                                    type="file"
                                    ref={fileInputRef}
                                    onChange={handleFileChange}
                                    className="hidden"
                                />
                                <DocumentArrowUpIcon className="w-10 h-10 text-slate-400 mb-3" />
                                {file ? (
                                    <div className="text-center">
                                        <p className="text-white font-medium">{file.name}</p>
                                        <p className="text-sm text-slate-500 mt-1">{(file.size / 1024).toFixed(2)} KB</p>
                                    </div>
                                ) : (
                                    <div className="text-center px-4">
                                        <p className="text-slate-300">Click to upload a file</p>
                                        <p className="text-sm text-slate-500 mt-1">Supports .py, .js, package.json, requirements.txt, etc.</p>
                                    </div>
                                )}
                            </div>
                        )}
                    </div>

                    <div className="flex justify-end shrink-0 pt-2 border-t border-white/10">
                        <button
                            onClick={handleScan}
                            disabled={loading}
                            className="w-full flex items-center justify-center px-6 py-3 bg-gradient-to-r from-primary to-blue-600 hover:from-blue-600 hover:to-primary text-white font-medium rounded-lg shadow-lg shadow-primary/20 transition-all disabled:opacity-50"
                        >
                            {loading ? (
                                <>
                                    <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin mr-2"></div>
                                    Analyzing Code...
                                </>
                            ) : (
                                <>
                                    <BeakerIcon className="w-5 h-5 mr-2" />
                                    Run Security Scan
                                </>
                            )}
                        </button>
                    </div>

                </div>
            </div>

        </div>
    );
};

export default Dashboard;
