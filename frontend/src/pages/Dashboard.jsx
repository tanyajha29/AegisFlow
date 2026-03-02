import React, { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { DocumentTextIcon, DocumentArrowUpIcon, BeakerIcon } from '@heroicons/react/24/outline';

const Dashboard = () => {
    const [tab, setTab] = useState('paste'); // 'paste' or 'upload'
    const [scanTitle, setScanTitle] = useState('');
    const [codeContent, setCodeContent] = useState('');
    const [file, setFile] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const fileInputRef = useRef(null);
    const navigate = useNavigate();

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

        const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

        try {
            const response = await axios.post(`${API_BASE}/scans/upload`, formData, {
                headers: {
                    'Content-Type': 'multipart/form-data'
                }
            });
            // Navigate to the report page
            navigate(`/report/${response.data.id}`);
        } catch (err) {
            console.error(err);
            setError(err.response?.data?.detail || "An error occurred during scanning");
            setLoading(false);
        }
    };

    return (
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-10">

            <div className="flex flex-col md:flex-row md:items-center justify-between mb-8">
                <div>
                    <h1 className="text-3xl font-bold text-white tracking-tight">New Security Scan</h1>
                    <p className="mt-2 text-slate-400">Analyze your source code for vulnerabilities and secrets.</p>
                </div>
            </div>

            <div className="bg-dark/50 border border-white/10 rounded-2xl p-6 shadow-xl backdrop-blur-sm">
                {error && (
                    <div className="mb-6 bg-red-500/10 border border-red-500/50 text-red-400 px-4 py-3 rounded-lg text-sm">
                        {error}
                    </div>
                )}

                <div className="mb-6">
                    <label className="block text-sm font-medium text-slate-300 mb-2">Scan Title or Reference</label>
                    <input
                        type="text"
                        className="w-full bg-darker border border-white/10 rounded-lg px-4 py-3 text-white focus:ring-2 focus:ring-primary focus:border-transparent outline-none transition-all placeholder-slate-600"
                        placeholder="e.g. Authentication Service Fixes"
                        value={scanTitle}
                        onChange={(e) => setScanTitle(e.target.value)}
                    />
                </div>

                <div className="mb-8 border-b border-white/10 flex">
                    <button
                        className={`pb-4 px-6 text-sm font-medium transition-colors flex items-center ${tab === 'paste' ? 'text-primary border-b-2 border-primary' : 'text-slate-400 hover:text-slate-200'}`}
                        onClick={() => setTab('paste')}
                    >
                        <DocumentTextIcon className="w-5 h-5 mr-2" />
                        Paste Code
                    </button>
                    <button
                        className={`pb-4 px-6 text-sm font-medium transition-colors flex items-center ${tab === 'upload' ? 'text-primary border-b-2 border-primary' : 'text-slate-400 hover:text-slate-200'}`}
                        onClick={() => setTab('upload')}
                    >
                        <DocumentArrowUpIcon className="w-5 h-5 mr-2" />
                        Upload File
                    </button>
                </div>

                {tab === 'paste' ? (
                    <div className="mb-6">
                        <textarea
                            className="w-full h-64 bg-darker border border-white/10 rounded-lg p-4 text-slate-300 font-mono text-sm focus:ring-2 focus:ring-primary focus:border-transparent outline-none transition-all resize-y placeholder-slate-600"
                            placeholder="# Paste your Python, JS, JSON or Text file content here..."
                            value={codeContent}
                            onChange={(e) => setCodeContent(e.target.value)}
                        ></textarea>
                    </div>
                ) : (
                    <div className="mb-6">
                        <div
                            className="border-2 border-dashed border-slate-600 hover:border-primary/50 bg-darker/50 rounded-xl p-12 text-center transition-colors cursor-pointer"
                            onClick={() => fileInputRef.current?.click()}
                        >
                            <input
                                type="file"
                                ref={fileInputRef}
                                onChange={handleFileChange}
                                className="hidden"
                            />
                            <DocumentArrowUpIcon className="w-12 h-12 mx-auto text-slate-400 mb-4" />
                            {file ? (
                                <div>
                                    <p className="text-white font-medium">{file.name}</p>
                                    <p className="text-sm text-slate-500 mt-1">{(file.size / 1024).toFixed(2)} KB</p>
                                </div>
                            ) : (
                                <div>
                                    <p className="text-slate-300">Click to upload a file</p>
                                    <p className="text-sm text-slate-500 mt-1">Supports .py, .js, package.json, requirements.txt, etc.</p>
                                </div>
                            )}
                        </div>
                    </div>
                )}

                <div className="flex justify-end">
                    <button
                        onClick={handleScan}
                        disabled={loading}
                        className="flex items-center px-6 py-3 bg-gradient-to-r from-primary to-blue-600 hover:from-blue-600 hover:to-primary text-white font-medium rounded-lg shadow-lg shadow-primary/20 transition-all disabled:opacity-50"
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
    );
};

export default Dashboard;
