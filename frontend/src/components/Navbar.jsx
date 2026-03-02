import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext.jsx';
import { ShieldCheckIcon, ArrowRightOnRectangleIcon } from '@heroicons/react/24/outline';

const Navbar = () => {
    const { logout, user } = useAuth();
    const navigate = useNavigate();

    const handleLogout = () => {
        logout();
        navigate('/login');
    };

    return (
        <nav className="fixed top-0 w-full z-50 bg-dark/80 backdrop-blur-md border-b border-white/10 shadow-lg">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="flex items-center justify-between h-16">
                    <div className="flex items-center flex-shrink-0 cursor-pointer" onClick={() => navigate('/')}>
                        <ShieldCheckIcon className="h-8 w-8 text-primary" />
                        <span className="ml-2 text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-primary to-secondary">
                            Drishti-Scan
                        </span>
                    </div>

                    <div className="flex items-center space-x-4">
                        <button
                            onClick={handleLogout}
                            className="flex items-center text-sm font-medium text-slate-300 hover:text-white transition-colors"
                        >
                            <ArrowRightOnRectangleIcon className="h-5 w-5 mr-1" />
                            Logout
                        </button>
                    </div>
                </div>
            </div>
        </nav>
    );
};

export default Navbar;
