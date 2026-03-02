import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { Link, useNavigate } from 'react-router-dom';
import { ShieldCheckIcon } from '@heroicons/react/24/outline';

const Register = () => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const { register } = useAuth();
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');

        if (password !== confirmPassword) {
            return setError('Passwords do not match');
        }

        setLoading(true);

        try {
            await register(email, password);
            navigate('/');
        } catch (err) {
            setError(err.response?.data?.detail || 'Failed to register. Email may be taken.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen flex items-center justify-center bg-darker py-12 px-4 sm:px-6 lg:px-8 relative overflow-hidden">
            {/* Background Decor */}
            <div className="absolute top-0 -right-1/4 w-1/2 h-1/2 bg-secondary/20 rounded-full blur-[120px] pointer-events-none"></div>
            <div className="absolute bottom-0 -left-1/4 w-1/2 h-1/2 bg-primary/20 rounded-full blur-[120px] pointer-events-none"></div>

            <div className="max-w-md w-full space-y-8 bg-dark/50 backdrop-blur-xl p-10 rounded-2xl border border-white/10 shadow-2xl relative z-10">
                <div>
                    <ShieldCheckIcon className="mx-auto h-16 w-16 text-secondary" />
                    <h2 className="mt-6 text-center text-3xl font-extrabold text-white">
                        Create an Account
                    </h2>
                </div>

                {error && (
                    <div className="bg-red-500/10 border border-red-500/50 text-red-400 px-4 py-3 rounded-lg text-sm text-center">
                        {error}
                    </div>
                )}

                <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
                    <div className="space-y-4">
                        <div>
                            <input
                                type="email"
                                required
                                className="appearance-none relative block w-full px-4 py-3 border border-white/10 bg-dark/50 placeholder-slate-400 text-white rounded-lg focus:outline-none focus:ring-2 focus:ring-secondary focus:border-transparent transition-all"
                                placeholder="Email address"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                            />
                        </div>
                        <div>
                            <input
                                type="password"
                                required
                                className="appearance-none relative block w-full px-4 py-3 border border-white/10 bg-dark/50 placeholder-slate-400 text-white rounded-lg focus:outline-none focus:ring-2 focus:ring-secondary focus:border-transparent transition-all"
                                placeholder="Password"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                            />
                        </div>
                        <div>
                            <input
                                type="password"
                                required
                                className="appearance-none relative block w-full px-4 py-3 border border-white/10 bg-dark/50 placeholder-slate-400 text-white rounded-lg focus:outline-none focus:ring-2 focus:ring-secondary focus:border-transparent transition-all"
                                placeholder="Confirm password"
                                value={confirmPassword}
                                onChange={(e) => setConfirmPassword(e.target.value)}
                            />
                        </div>
                    </div>

                    <div>
                        <button
                            type="submit"
                            disabled={loading}
                            className="group relative w-full flex justify-center py-3 px-4 border border-transparent text-sm font-medium rounded-lg text-white bg-gradient-to-r from-secondary to-emerald-600 hover:from-emerald-600 hover:to-secondary focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-secondary focus:ring-offset-darker transition-all disabled:opacity-50 shadow-lg shadow-secondary/30"
                        >
                            {loading ? 'Creating...' : 'Register'}
                        </button>
                    </div>
                </form>

                <div className="text-center text-sm text-slate-400">
                    Already have an account?{' '}
                    <Link to="/login" className="font-medium text-secondary hover:text-emerald-400 transition-colors">
                        Sign in here
                    </Link>
                </div>
            </div>
        </div>
    );
};

export default Register;
