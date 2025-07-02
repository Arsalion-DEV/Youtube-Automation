"use client";

import { useState } from "react";
import { 
  Home, 
  Video, 
  BarChart3, 
  Settings, 
  Menu,
  X,
  Activity
} from "lucide-react";

interface NavigationProps {
  activeTab: string;
  onTabChange: (tab: string) => void;
}

const navigationItems = [
  { id: "overview", label: "Overview", icon: Home },
  { id: "videos", label: "Videos", icon: Video },
  { id: "analytics", label: "Analytics", icon: BarChart3 },
  { id: "monitoring", label: "System", icon: Activity },
  { id: "settings", label: "Settings", icon: Settings },
];

export function Navigation({ activeTab, onTabChange }: NavigationProps) {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  return (
    <>
      {/* Desktop Navigation */}
      <nav className="hidden md:flex bg-white border-b border-gray-200 px-6 py-4">
        <div className="flex items-center justify-between w-full max-w-7xl mx-auto">
          <div className="flex items-center gap-8">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-blue-600 rounded-lg">
                <Video className="w-6 h-6 text-white" />
              </div>
              <h1 className="text-xl font-bold text-gray-900">YouTube Automation</h1>
            </div>
            
            <div className="flex items-center gap-1">
              {navigationItems.map((item) => {
                const Icon = item.icon;
                return (
                  <button
                    key={item.id}
                    onClick={() => onTabChange(item.id)}
                    className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                      activeTab === item.id
                        ? "bg-blue-100 text-blue-700"
                        : "text-gray-600 hover:text-gray-900 hover:bg-gray-100"
                    }`}
                  >
                    <Icon className="w-4 h-4" />
                    {item.label}
                  </button>
                );
              })}
            </div>
          </div>

          <div className="flex items-center gap-3">
            <div className="px-3 py-1 bg-green-100 text-green-800 text-sm rounded-full font-medium">
              Online
            </div>
          </div>
        </div>
      </nav>

      {/* Mobile Navigation */}
      <nav className="md:hidden bg-white border-b border-gray-200">
        <div className="flex items-center justify-between px-4 py-3">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-blue-600 rounded-lg">
              <Video className="w-5 h-5 text-white" />
            </div>
            <h1 className="text-lg font-bold text-gray-900">YouTube Automation</h1>
          </div>
          
          <button
            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
            className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg"
          >
            {isMobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </button>
        </div>

        {/* Mobile Menu */}
        {isMobileMenuOpen && (
          <div className="border-t border-gray-200 bg-white">
            <div className="px-4 py-2 space-y-1">
              {navigationItems.map((item) => {
                const Icon = item.icon;
                return (
                  <button
                    key={item.id}
                    onClick={() => {
                      onTabChange(item.id);
                      setIsMobileMenuOpen(false);
                    }}
                    className={`flex items-center gap-3 w-full px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                      activeTab === item.id
                        ? "bg-blue-100 text-blue-700"
                        : "text-gray-600 hover:text-gray-900 hover:bg-gray-100"
                    }`}
                  >
                    <Icon className="w-4 h-4" />
                    {item.label}
                  </button>
                );
              })}
            </div>
          </div>
        )}
      </nav>
    </>
  );
}
