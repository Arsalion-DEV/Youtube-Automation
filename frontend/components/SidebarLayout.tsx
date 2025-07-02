'use client'

import { useState } from "react";

interface SidebarLayoutProps {
  children: React.ReactNode;
}

export default function SidebarLayout({ children }: SidebarLayoutProps) {
  const [sidebarOpen, setSidebarOpen] = useState(true);

  const navItems = [
    { name: 'Dashboard', href: '#', icon: '🏠', current: true },
    { name: 'Channels', href: '#', icon: '📺', current: false, badge: '✨' },
    { name: 'Videos', href: '#', icon: '🎬', current: false },
    { name: 'Multi-Platform', href: '#', icon: '🌐', current: false, badge: 'New' },
    { name: 'Scheduler', href: '#', icon: '📅', current: false },
    { name: 'Analytics', href: '#', icon: '📊', current: false },
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Sidebar */}
      <div className={`fixed inset-y-0 left-0 z-50 ${sidebarOpen ? 'w-72' : 'w-20'} bg-white shadow-lg border-r border-gray-200 transition-all duration-300`}>
        {/* Sidebar header */}
        <div className="flex h-16 items-center justify-between px-6 border-b border-gray-200">
          {sidebarOpen && (
            <div className="flex items-center">
              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-gradient-to-r from-blue-600 to-indigo-600">
                <span className="text-white font-bold text-lg">Y</span>
              </div>
              <div className="ml-3">
                <h1 className="text-lg font-bold text-gray-900">YouTube Pro</h1>
                <p className="text-xs text-gray-500">Automation Platform</p>
              </div>
            </div>
          )}
          <button 
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="p-2 rounded-md text-gray-400 hover:text-gray-600 hover:bg-gray-100"
          >
            {sidebarOpen ? '←' : '→'}
          </button>
        </div>

        {/* Navigation */}
        <nav className="flex-1 px-4 py-6 space-y-2">
          {navItems.map((item) => (
            <a
              key={item.name}
              href={item.href}
              className={`${
                item.current
                  ? 'bg-blue-100 text-blue-700 border-blue-300'
                  : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
              } group flex items-center px-3 py-2 text-sm font-medium rounded-md border border-transparent transition-colors`}
            >
              <span className="mr-3 text-lg">{item.icon}</span>
              {sidebarOpen && (
                <>
                  <span className="flex-1">{item.name}</span>
                  {item.badge && (
                    <span className="ml-2 px-2 py-1 text-xs bg-green-100 text-green-800 rounded">
                      {item.badge}
                    </span>
                  )}
                </>
              )}
            </a>
          ))}
        </nav>

        {/* Quick Actions */}
        {sidebarOpen && (
          <div className="border-t border-gray-200 p-4">
            <p className="text-xs font-medium text-gray-500 uppercase tracking-wider mb-3">
              Quick Actions
            </p>
            <div className="space-y-2">
              <button className="w-full flex items-center px-3 py-2 text-sm text-gray-600 hover:bg-gray-100 rounded-md">
                <span className="mr-2">➕</span>
                Add Channel
              </button>
              <button className="w-full flex items-center px-3 py-2 text-sm text-gray-600 hover:bg-gray-100 rounded-md">
                <span className="mr-2">🎥</span>
                Create Video
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Main content */}
      <div className={`${sidebarOpen ? 'ml-72' : 'ml-20'} transition-all duration-300`}>
        {/* Top bar */}
        <div className="bg-white shadow-sm border-b border-gray-200">
          <div className="flex h-16 items-center justify-between px-6">
            <div className="flex items-center space-x-4">
              <h2 className="text-xl font-semibold text-gray-900">Dashboard</h2>
            </div>
            
            <div className="flex items-center space-x-4">
              {/* System Status */}
              <div className="hidden md:flex items-center space-x-4 text-sm">
                <div className="flex items-center space-x-1">
                  <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                  <span className="text-gray-600">API</span>
                </div>
                <div className="flex items-center space-x-1">
                  <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                  <span className="text-gray-600">DB</span>
                </div>
                <div className="flex items-center space-x-1">
                  <span className="text-gray-600">Memory: 150MB</span>
                </div>
              </div>

              {/* Search */}
              <div className="relative">
                <input
                  type="text"
                  placeholder="Search..."
                  className="w-64 pl-10 pr-4 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center">
                  <span className="text-gray-400">🔍</span>
                </div>
              </div>

              {/* User menu */}
              <div className="flex items-center space-x-3">
                <button className="relative p-2 text-gray-400 hover:text-gray-600">
                  <span className="text-lg">🔔</span>
                </button>
                <div className="flex items-center space-x-2">
                  <button className="px-4 py-2 text-sm text-gray-600 hover:text-gray-900">
                    Sign In
                  </button>
                  <button className="px-4 py-2 text-sm text-white bg-blue-600 hover:bg-blue-700 rounded-md">
                    Get Started
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Page content */}
        <main className="p-6">
          {children}
        </main>
      </div>
    </div>
  );
}