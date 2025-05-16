import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Menu, X, MoreVertical, UserCircle } from 'lucide-react';

const Navbar = ({ sidebarOpen, setSidebarOpen }) => {
    const location = useLocation();

    const navItems = [
        { name: 'Dashboard', path: '/' },
        { name: 'Upload', path: '/upload' },
        { name: 'EDA', path: '/eda' }
    ];

    return (
        <div>
            {/* Top Navbar */}
            <nav className="fixed w-full bg-gray-900 text-white shadow-md py-4 px-6 flex justify-between items-center z-50">
                <div className="flex items-center space-x-4">
                    <button onClick={() => setSidebarOpen(!sidebarOpen)} className="p-2 rounded-lg bg-gray-700 hover:bg-gray-600">
                        {sidebarOpen ? <X size={20} /> : <Menu size={20} />}
                    </button>
                    <h1 className="text-2xl font-bold">AutoML</h1>
                </div>
                <div className="flex items-center space-x-4">
                    <button className="p-2 rounded-lg bg-gray-700 hover:bg-gray-600">
                        <MoreVertical size={20} />
                    </button>
                    <UserCircle size={30} className="text-gray-400" />
                </div>
            </nav>

            {/* Sidebar */}
            <aside className={`fixed top-0 left-0 h-full bg-gray-800 text-white shadow-md z-40 w-64 p-6 transform transition-transform duration-300 ease-in-out ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'}`}>
                <ul className="space-y-4">
                    {navItems.map((item) => (
                        <li key={item.path}>
                            <Link
                                to={item.path}
                                className={`block py-2 px-4 rounded-lg ${location.pathname === item.path ? 'bg-blue-500 text-white' : 'text-gray-300 hover:bg-gray-700'}`}
                            >
                                {item.name}
                            </Link>
                        </li>
                    ))}
                </ul>
            </aside>

            {/* Overlay for closing sidebar on mobile */}
            {sidebarOpen && (
                <div onClick={() => setSidebarOpen(false)} className="fixed inset-0 bg-black bg-opacity-50 z-30 md:hidden"></div>
            )}
        </div>
    );
};

export default Navbar;
