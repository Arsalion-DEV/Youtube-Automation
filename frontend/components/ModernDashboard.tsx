import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { useTheme } from '@/components/ThemeProvider';
import { 
  Sun,
  Moon,
  Menu,
  X,
  Bell,
  Settings,
  Plus,
  Youtube,
  BarChart3,
  Video,
  Search,
  TrendingUp,
  Users,
  Clock,
  CheckCircle,
  AlertCircle,
  Activity,
  Zap,
  Target,
  Globe
} from 'lucide-react';

import ChannelManager from './ChannelManager';
import IntegrationsDashboard from './IntegrationsDashboard';
import VideoGenerationDashboard from './VideoGenerationDashboard';

interface SystemStatus {
  total_channels: number;
  active_channels: number;
  system_healthy: boolean;
  api_usage: Record<string, number>;
  last_updated: string;
}

interface DashboardStats {
  total_videos: number;
  total_views: number;
  total_subscribers: number;
  monthly_growth: number;
}

const ModernDashboard: React.FC = () => {
  const { theme, setTheme, isDarkMode, toggleTheme } = useTheme();
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');
  const [systemStatus, setSystemStatus] = useState<SystemStatus | null>(null);
  const [dashboardStats, setDashboardStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Load initial data
    loadDashboardData();
    
    // Set up polling for real-time updates
    const interval = setInterval(loadDashboardData, 30000);
    return () => clearInterval(interval);
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      
      // Load system status
      try {
        const statusResponse = await fetch('/api/v2/channels/system/status');
        if (statusResponse.ok) {
          const statusData = await statusResponse.json();
          setSystemStatus(statusData.data);
        }
      } catch (error) {
        console.error('Failed to load system status:', error);
      }

      // Load dashboard stats (mock data for demo)
      setDashboardStats({
        total_videos: 142,
        total_views: 1284567,
        total_subscribers: 45678,
        monthly_growth: 12.5
      });

    } catch (error) {
      console.error('Failed to load dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const navigationItems = [
    { id: 'overview', label: 'Overview', icon: BarChart3 },
    { id: 'channels', label: 'Channels', icon: Youtube },
    { id: 'videos', label: 'Videos', icon: Video },
    { id: 'analytics', label: 'Analytics', icon: TrendingUp },
    { id: 'integrations', label: 'Integrations', icon: Zap },
    { id: 'settings', label: 'Settings', icon: Settings }
  ];

  const Sidebar = () => (
    <div className={`fixed inset-y-0 left-0 z-50 w-64 bg-white dark:bg-gray-900 border-r border-gray-200 dark:border-gray-700 transform transition-transform duration-200 ease-in-out ${
      sidebarOpen ? 'translate-x-0' : '-translate-x-full'
    } lg:translate-x-0`}>
      <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-xl">
            <Youtube className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="text-lg font-bold text-gray-900 dark:text-white">
              YouTube Pro
            </h1>
            <p className="text-xs text-gray-500 dark:text-gray-400">
              Automation Platform
            </p>
          </div>
        </div>
        <Button
          variant="ghost"
          size="sm"
          onClick={() => setSidebarOpen(false)}
          className="lg:hidden"
        >
          <X className="w-4 h-4" />
        </Button>
      </div>

      <nav className="p-4 space-y-2">
        {navigationItems.map((item) => {
          const Icon = item.icon;
          return (
            <button
              key={item.id}
              onClick={() => setActiveTab(item.id)}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg text-left transition-colors ${
                activeTab === item.id
                  ? 'bg-blue-50 dark:bg-blue-900/50 text-blue-700 dark:text-blue-300 border border-blue-200 dark:border-blue-700'
                  : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800'
              }`}
            >
              <Icon className="w-5 h-5" />
              <span className="font-medium">{item.label}</span>
            </button>
          );
        })}
      </nav>

      <div className="absolute bottom-4 left-4 right-4">
        <div className="p-4 bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 rounded-lg border border-blue-200 dark:border-blue-700">
          <div className="flex items-center gap-3 mb-2">
            <Activity className="w-5 h-5 text-blue-600 dark:text-blue-400" />
            <span className="font-medium text-blue-900 dark:text-blue-100">System Status</span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-sm text-blue-700 dark:text-blue-300">
              {systemStatus?.system_healthy ? 'All Systems Operational' : 'Issues Detected'}
            </span>
            <div className={`w-2 h-2 rounded-full ${
              systemStatus?.system_healthy ? 'bg-green-500' : 'bg-red-500'
            }`} />
          </div>
        </div>
      </div>
    </div>
  );

  const TopBar = () => (
    <div className="bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-700 px-6 py-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="lg:hidden"
          >
            <Menu className="w-5 h-5" />
          </Button>
          
          <div>
            <h2 className="text-xl font-bold text-gray-900 dark:text-white capitalize">
              {activeTab === 'overview' ? 'Dashboard Overview' : navigationItems.find(item => item.id === activeTab)?.label}
            </h2>
            <p className="text-sm text-gray-500 dark:text-gray-400">
              {new Date().toLocaleDateString('en-US', { 
                weekday: 'long', 
                year: 'numeric', 
                month: 'long', 
                day: 'numeric' 
              })}
            </p>
          </div>
        </div>

        <div className="flex items-center gap-4">
          <Button variant="ghost" size="sm" className="relative">
            <Bell className="w-5 h-5" />
            <div className="absolute -top-1 -right-1 w-3 h-3 bg-red-500 rounded-full border-2 border-white dark:border-gray-900" />
          </Button>
          
          <Button
            variant="ghost"
            size="sm"
            onClick={toggleTheme}
            className="flex items-center gap-2"
          >
            {isDarkMode ? (
              <>
                <Sun className="w-4 h-4" />
                <span className="hidden sm:inline">Light</span>
              </>
            ) : (
              <>
                <Moon className="w-4 h-4" />
                <span className="hidden sm:inline">Dark</span>
              </>
            )}
          </Button>

          <div className="flex items-center gap-3 pl-4 border-l border-gray-200 dark:border-gray-700">
            <Avatar className="w-8 h-8">
              <AvatarFallback className="bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300">
                YA
              </AvatarFallback>
            </Avatar>
            <div className="hidden sm:block">
              <p className="text-sm font-medium text-gray-900 dark:text-white">YouTube Admin</p>
              <p className="text-xs text-gray-500 dark:text-gray-400">Pro Account</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  const OverviewContent = () => (
    <div className="space-y-6">
      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card className="bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-900/20 dark:to-blue-800/20 border-blue-200 dark:border-blue-700">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-blue-600 dark:text-blue-400 text-sm font-medium">Total Channels</p>
                <p className="text-2xl font-bold text-blue-900 dark:text-blue-100">
                  {systemStatus?.total_channels || 0}
                </p>
                <p className="text-xs text-blue-600 dark:text-blue-400 mt-1">
                  {systemStatus?.active_channels || 0} active
                </p>
              </div>
              <div className="p-3 bg-blue-200 dark:bg-blue-800 rounded-full">
                <Youtube className="w-6 h-6 text-blue-700 dark:text-blue-300" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-green-50 to-green-100 dark:from-green-900/20 dark:to-green-800/20 border-green-200 dark:border-green-700">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-green-600 dark:text-green-400 text-sm font-medium">Total Videos</p>
                <p className="text-2xl font-bold text-green-900 dark:text-green-100">
                  {dashboardStats?.total_videos.toLocaleString() || 0}
                </p>
                <p className="text-xs text-green-600 dark:text-green-400 mt-1">
                  +12 this week
                </p>
              </div>
              <div className="p-3 bg-green-200 dark:bg-green-800 rounded-full">
                <Video className="w-6 h-6 text-green-700 dark:text-green-300" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-purple-50 to-purple-100 dark:from-purple-900/20 dark:to-purple-800/20 border-purple-200 dark:border-purple-700">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-purple-600 dark:text-purple-400 text-sm font-medium">Total Views</p>
                <p className="text-2xl font-bold text-purple-900 dark:text-purple-100">
                  {dashboardStats?.total_views.toLocaleString() || 0}
                </p>
                <p className="text-xs text-purple-600 dark:text-purple-400 mt-1">
                  +{dashboardStats?.monthly_growth || 0}% this month
                </p>
              </div>
              <div className="p-3 bg-purple-200 dark:bg-purple-800 rounded-full">
                <BarChart3 className="w-6 h-6 text-purple-700 dark:text-purple-300" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-orange-50 to-orange-100 dark:from-orange-900/20 dark:to-orange-800/20 border-orange-200 dark:border-orange-700">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-orange-600 dark:text-orange-400 text-sm font-medium">Subscribers</p>
                <p className="text-2xl font-bold text-orange-900 dark:text-orange-100">
                  {dashboardStats?.total_subscribers.toLocaleString() || 0}
                </p>
                <p className="text-xs text-orange-600 dark:text-orange-400 mt-1">
                  +2.3K this month
                </p>
              </div>
              <div className="p-3 bg-orange-200 dark:bg-orange-800 rounded-full">
                <Users className="w-6 h-6 text-orange-700 dark:text-orange-300" />
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Quick Actions */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Zap className="w-5 h-5 text-blue-500" />
            Quick Actions
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <Button 
              className="h-20 flex-col gap-2 bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700"
              onClick={() => setActiveTab('videos')}
            >
              <Video className="w-5 h-5" />
              <span>Create Video</span>
            </Button>
            
            <Button 
              variant="outline" 
              className="h-20 flex-col gap-2 border-dashed border-2 hover:bg-gray-50 dark:hover:bg-gray-800"
              onClick={() => setActiveTab('channels')}
            >
              <Plus className="w-5 h-5" />
              <span>Add Channel</span>
            </Button>
            
            <Button 
              variant="outline" 
              className="h-20 flex-col gap-2 border-dashed border-2 hover:bg-gray-50 dark:hover:bg-gray-800"
              onClick={() => setActiveTab('analytics')}
            >
              <BarChart3 className="w-5 h-5" />
              <span>View Analytics</span>
            </Button>
            
            <Button 
              variant="outline" 
              className="h-20 flex-col gap-2 border-dashed border-2 hover:bg-gray-50 dark:hover:bg-gray-800"
              onClick={() => setActiveTab('integrations')}
            >
              <Zap className="w-5 h-5" />
              <span>Integrations</span>
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Recent Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Activity className="w-5 h-5 text-green-500" />
              Recent Activity
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {[
              { action: 'Video published', channel: 'Tech Reviews', time: '2 minutes ago', status: 'success' },
              { action: 'Script generated', channel: 'Cooking Tips', time: '15 minutes ago', status: 'info' },
              { action: 'Channel added', channel: 'Gaming Hub', time: '1 hour ago', status: 'success' },
              { action: 'Video failed', channel: 'Music Channel', time: '2 hours ago', status: 'error' }
            ].map((activity, index) => (
              <div key={index} className="flex items-center gap-3 p-3 rounded-lg bg-gray-50 dark:bg-gray-800">
                <div className={`w-2 h-2 rounded-full ${
                  activity.status === 'success' ? 'bg-green-500' :
                  activity.status === 'error' ? 'bg-red-500' : 'bg-blue-500'
                }`} />
                <div className="flex-1">
                  <p className="text-sm font-medium text-gray-900 dark:text-white">
                    {activity.action}
                  </p>
                  <p className="text-xs text-gray-500 dark:text-gray-400">
                    {activity.channel} • {activity.time}
                  </p>
                </div>
              </div>
            ))}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Target className="w-5 h-5 text-purple-500" />
              Performance Overview
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600 dark:text-gray-400">Video Generation Success Rate</span>
                <span className="text-sm font-medium text-gray-900 dark:text-white">94%</span>
              </div>
              <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                <div className="bg-green-500 h-2 rounded-full" style={{ width: '94%' }} />
              </div>
            </div>
            
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600 dark:text-gray-400">API Usage</span>
                <span className="text-sm font-medium text-gray-900 dark:text-white">67%</span>
              </div>
              <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                <div className="bg-blue-500 h-2 rounded-full" style={{ width: '67%' }} />
              </div>
            </div>
            
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600 dark:text-gray-400">System Performance</span>
                <span className="text-sm font-medium text-gray-900 dark:text-white">98%</span>
              </div>
              <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                <div className="bg-purple-500 h-2 rounded-full" style={{ width: '98%' }} />
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-950 transition-colors duration-200">
      <Sidebar />
      
      <div className={`transition-all duration-200 ${sidebarOpen ? 'lg:ml-64' : ''}`}>
        <TopBar />
        
        <main className="p-6">
          {activeTab === 'overview' && <OverviewContent />}
          {activeTab === 'channels' && <ChannelManager />}
          {activeTab === 'videos' && <VideoGenerationDashboard />}
          {activeTab === 'integrations' && <IntegrationsDashboard />}
          {activeTab === 'analytics' && (
            <div className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <BarChart3 className="w-5 h-5" />
                    Analytics Dashboard
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-center py-12">
                    <BarChart3 className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                    <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                      Advanced Analytics
                    </h3>
                    <p className="text-gray-500 dark:text-gray-400 mb-4">
                      Comprehensive analytics dashboard with real-time insights.
                    </p>
                    <Button>Coming Soon</Button>
                  </div>
                </CardContent>
              </Card>
            </div>
          )}
          {activeTab === 'settings' && (
            <div className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Settings className="w-5 h-5" />
                    Settings
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-center py-12">
                    <Settings className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                    <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                      System Settings
                    </h3>
                    <p className="text-gray-500 dark:text-gray-400 mb-4">
                      Configure your YouTube automation platform settings.
                    </p>
                    <Button>Manage Settings</Button>
                  </div>
                </CardContent>
              </Card>
            </div>
          )}
        </main>
      </div>

      {/* Mobile overlay */}
      {sidebarOpen && (
        <div 
          className="fixed inset-0 bg-black bg-opacity-50 z-40 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}
    </div>
  );
};

export default ModernDashboard;