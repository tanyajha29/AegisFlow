import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import axios from 'axios';
import { Pie, Bar } from 'react-chartjs-2';
import { ArrowDownTrayIcon, ArrowLeftIcon, ExclamationTriangleIcon, ShieldExclamationIcon, CheckCircleIcon } from '@heroicons/react/24/outline';

const ScanReport = () => {
    const { id } = useParams();
    const [report, setReport] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

    useEffect(() => {
        const fetchReport = async () => {
            try {
                const response = await axios.get(`${API_BASE}/reports/${id}`);
                setReport(response.data);
            } catch (err) {
                setError("Failed to load report. It may not exist or you don't have permission.");
            } finally {
                setLoading(false);
            }
        };
        fetchReport();
    }, [id, API_BASE]);

    const downloadPdf = async () => {
        try {
            const response = await axios.get(`${API_BASE}/reports/${id}/pdf`, {
                responseType: 'blob',
            });
            const url = window.URL.createObjectURL(new Blob([response.data]));
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', `drishti_scan_${id}.pdf`);
            document.body.appendChild(link);
            link.click();
        } catch (err) {
            console.error("Failed to download PDF", err);
            alert("Failed to download PDF report");
        }
    };

    if (loading) return (
        <div className="flex h-[80vh] items-center justify-center">
            <div className="w-16 h-16 border-4 border-primary/20 border-t-primary rounded-full animate-spin"></div>
        </div>
    );

    if (error || !report) return (
        <div className="max-w-4xl mx-auto mt-20 p-8 bg-dark/50 border border-white/10 rounded-2xl text-center">
            <ExclamationTriangleIcon className="w-16 h-16 text-red-400 mx-auto mb-4" />
            <h2 className="text-xl font-bold text-white mb-2">Error Loading Report</h2>
            <p className="text-slate-400 mb-6">{error}</p>
            <Link to="/" className="text-primary hover:text-white transition-colors">← Back to Dashboard</Link>
        </div>
    );

    // Group vulnerabilities by severity
    const severityCounts = {
        Critical: report.vulnerabilities.filter(v => v.severity === 'Critical').length,
        High: report.vulnerabilities.filter(v => v.severity === 'High').length,
        Medium: report.vulnerabilities.filter(v => v.severity === 'Medium').length,
        Low: report.vulnerabilities.filter(v => v.severity === 'Low').length,
    };

    const pieData = {
        labels: ['Critical', 'High', 'Medium', 'Low'],
        datasets: [
            {
                data: [severityCounts.Critical, severityCounts.High, severityCounts.Medium, severityCounts.Low],
                backgroundColor: [
                    'rgba(239, 68, 68, 0.8)', // red-500
                    'rgba(249, 115, 22, 0.8)', // orange-500
                    'rgba(234, 179, 8, 0.8)', // yellow-500
                    'rgba(59, 130, 246, 0.8)', // blue-500
                ],
                borderColor: [
                    'rgb(239, 68, 68)',
                    'rgb(249, 115, 22)',
                    'rgb(234, 179, 8)',
                    'rgb(59, 130, 246)',
                ],
                borderWidth: 1,
            },
        ],
    };

    // Safe gauge setup
    const gaugeColor = report.risk_score > 70 ? 'text-red-500' : report.risk_score > 40 ? 'text-orange-500' : 'text-emerald-500';

    return (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-8">

            {/* Header */}
            <div className="flex flex-col md:flex-row md:items-center justify-between bg-dark/50 backdrop-blur-sm border border-white/10 rounded-2xl p-6">
                <div>
                    <Link to="/" className="inline-flex items-center text-sm text-slate-400 hover:text-white transition-colors mb-4">
                        <ArrowLeftIcon className="w-4 h-4 mr-1" /> Back to Scanner
                    </Link>
                    <h1 className="text-3xl font-bold text-white">Report: {report.title}</h1>
                    <p className="text-slate-400 mt-1">Generated on {new Date(report.created_at).toLocaleString()}</p>
                </div>
                <div className="mt-4 md:mt-0">
                    <button
                        onClick={downloadPdf}
                        className="flex items-center px-4 py-2 bg-white/10 hover:bg-white/20 text-white font-medium rounded-lg transition-colors border border-white/5"
                    >
                        <ArrowDownTrayIcon className="w-5 h-5 mr-2" />
                        Download PDF
                    </button>
                </div>
            </div>

            {/* Overview Cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="bg-dark/50 border border-white/10 rounded-2xl p-6 flex flex-col items-center justify-center">
                    <h3 className="text-slate-400 font-medium mb-2">Risk Score</h3>
                    <div className={`text-6xl font-bold ${gaugeColor}`}>
                        {report.risk_score}<span className="text-2xl text-slate-500">/100</span>
                    </div>
                    <p className="text-sm mt-4 text-center text-slate-400">
                        {report.risk_score > 70 ? 'Action required immediately' : 'Keep monitoring'}
                    </p>
                </div>

                <div className="bg-dark/50 border border-white/10 rounded-2xl p-6 flex flex-col items-center justify-center col-span-1 md:col-span-2">
                    <h3 className="text-slate-400 font-medium mb-4 w-full text-left">Vulnerability Distribution</h3>
                    <div className="h-48 w-full flex justify-center items-center">
                        {report.vulnerabilities.length > 0 ? (
                            <Pie data={pieData} options={{ maintainAspectRatio: false }} />
                        ) : (
                            <div className="text-center">
                                <CheckCircleIcon className="w-16 h-16 text-emerald-500 mx-auto mb-2" />
                                <p className="text-slate-300">No vulnerabilities found!</p>
                            </div>
                        )}
                    </div>
                </div>
            </div>

            {/* Details List */}
            <div className="bg-dark/50 border border-white/10 rounded-2xl overflow-hidden">
                <div className="px-6 py-4 border-b border-white/10 bg-dark/80">
                    <h3 className="text-lg font-medium text-white">Findings Breakdown ({report.vulnerabilities.length})</h3>
                </div>

                <div className="divide-y divide-white/10">
                    {report.vulnerabilities.length === 0 ? (
                        <div className="p-8 text-center text-slate-400">Code is clean. Outstanding job!</div>
                    ) : (
                        report.vulnerabilities.map((vuln, idx) => (
                            <div key={idx} className="p-6 hover:bg-white/[0.02] transition-colors">
                                <div className="flex items-start justify-between">
                                    <div className="flex items-start">
                                        <ShieldExclamationIcon className={`w-6 h-6 mr-3 mt-1 ${vuln.severity === 'Critical' ? 'text-red-500' :
                                                vuln.severity === 'High' ? 'text-orange-500' :
                                                    vuln.severity === 'Medium' ? 'text-yellow-500' : 'text-blue-500'
                                            }`} />
                                        <div>
                                            <h4 className="text-lg font-medium text-white">{vuln.vulnerability_name}</h4>
                                            <p className="text-sm text-slate-400 mt-1 font-mono">
                                                {vuln.file_name} : {vuln.line_number}
                                            </p>
                                        </div>
                                    </div>
                                    <span className={`px-3 py-1 text-xs font-semibold rounded-full border ${vuln.severity === 'Critical' ? 'bg-red-500/10 text-red-400 border-red-500/20' :
                                            vuln.severity === 'High' ? 'bg-orange-500/10 text-orange-400 border-orange-500/20' :
                                                vuln.severity === 'Medium' ? 'bg-yellow-500/10 text-yellow-400 border-yellow-500/20' :
                                                    'bg-blue-500/10 text-blue-400 border-blue-500/20'
                                        }`}>
                                        {vuln.severity}
                                    </span>
                                </div>

                                <div className="mt-4 pl-9 space-y-4">
                                    <div className="bg-darker p-4 rounded-lg border border-white/5 font-mono text-sm overflow-x-auto text-pink-400">
                                        {vuln.code_snippet}
                                    </div>

                                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                        <div>
                                            <h5 className="text-sm font-medium text-slate-300 mb-1">Explanation</h5>
                                            <p className="text-sm text-slate-400 leading-relaxed">{vuln.explanation}</p>
                                        </div>
                                        <div>
                                            <h5 className="text-sm font-medium text-slate-300 mb-1">Remediation ({vuln.cwe_mapping})</h5>
                                            <p className="text-sm text-emerald-400/80 leading-relaxed">{vuln.remediation_steps}</p>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        ))
                    )}
                </div>
            </div>

        </div>
    );
};

export default ScanReport;
