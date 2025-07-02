'use client'

import React, { useState, useEffect, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  TrendingUp, TrendingDown, Eye, Users, DollarSign, Play,
  BarChart3, PieChart, Activity, Calendar, Filter, Download,
  RefreshCw, Settings, Target, Zap, Globe, Clock, ArrowUpRight,
  ArrowDownRight, TestTube, Split, Trophy, Lightbulb, Star,
  Share2, Heart, MessageCircle, Repeat2, ExternalLink
} from 'lucide-react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  TimeScale
} from 'chart.js';
import { Line, Bar, Pie, Doughnut } from 'react-chartjs-2';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  TimeScale
);

// Mock data for advanced analytics
const mockAnalyticsData = {
  overview: {
    totalViews: 2450000,
    totalSubscribers: 45230,
    totalRevenue: 12847.50,
    totalVideos: 247,
    avgWatchTime: 8.4,
    engagementRate: 4.2,
    ctr: 12.8,
    impressions: 18500000,
    trends: {
      views: { value: 24.5, period: '30d' },
      subscribers: { value: 8.2, period: '30d' },
      revenue: { value: 18.3, period: '30d' },
      engagement: { value: -2.1, period: '30d' }
    }
  },
  
  performanceMetrics: {
    last30Days: [
      { date: '2024-06-01', views: 45000, subscribers: 120, revenue: 450.20 },
      { date: '2024-06-02', views: 52000, subscribers: 150, revenue: 520.80 },
      { date: '2024-06-03', views: 48000, subscribers: 135, revenue: 480.50 },
      { date: '2024-06-04', views: 61000, subscribers: 180, revenue: 610.75 },
      { date: '2024-06-05', views: 58000, subscribers: 165, revenue: 580.30 },
      { date: '2024-06-06', views: 55000, subscribers: 140, revenue: 550.60 },
      { date: '2024-06-07', views: 67000, subscribers: 200, revenue: 670.90 }
    ]
  },

  abTests: [
    {
      id: 'test_001',
      name: 'Thumbnail Style A vs B',
      status: 'running',
      startDate: '2024-06-20',
      endDate: '2024-06-27',
      variants: [
        { name: 'Variant A', views: 25400, ctr: 14.2, conversions: 230 },
        { name: 'Variant B', views: 26800, ctr: 16.8, conversions: 285 }
      ],
      confidence: 87.5,
      winner: 'Variant B',
      improvement: 18.3
    },
    {
      id: 'test_002', 
      name: 'Title Length: Short vs Long',
      status: 'completed',
      startDate: '2024-06-10',
      endDate: '2024-06-17',
      variants: [
        { name: 'Short Title', views: 18200, ctr: 11.5, conversions: 185 },
        { name: 'Long Title', views: 22100, ctr: 13.8, conversions: 245 }
      ],
      confidence: 95.2,
      winner: 'Long Title',
      improvement: 20.1
    }
  ],

  revenueBreakdown: {
    sources: [
      { name: 'YouTube AdSense', value: 7200.30, percentage: 56.1 },
      { name: 'Brand Sponsorships', value: 3800.50, percentage: 29.6 },
      { name: 'Affiliate Marketing', value: 1246.70, percentage: 9.7 },
      { name: 'Channel Memberships', value: 600.00, percentage: 4.6 }
    ],
    monthly: [
      { month: 'Jan', revenue: 8500 },
      { month: 'Feb', revenue: 9200 },
      { month: 'Mar', revenue: 10100 },
      { month: 'Apr', revenue: 11400 },
      { month: 'May', revenue: 12200 },
      { month: 'Jun', revenue: 12847 }
    ]
  },

  topVideos: [
    {
      id: 'v1',
      title: 'Ultimate YouTube SEO Guide 2024',
      views: 89400,
      revenue: 1240.50,
      engagement: 5.8,
      published: '2024-06-15',
      thumbnail: '/api/placeholder/160/90'
    },
    {
      id: 'v2',
      title: 'AI Content Creation Secrets',
      views: 67800,
      revenue: 890.20,
      engagement: 6.2,
      published: '2024-06-10',
      thumbnail: '/api/placeholder/160/90'
    },
    {
      id: 'v3',
      title: 'Social Media Automation 101',
      views: 54200,
      revenue: 720.80,
      engagement: 4.9,
      published: '2024-06-05',
      thumbnail: '/api/placeholder/160/90'
    }
  ],

  demographics: {
    age: [
      { range: '18-24', percentage: 28.5 },
      { range: '25-34', percentage: 42.1 },
      { range: '35-44', percentage: 18.7 },
      { range: '45-54', percentage: 8.2 },
      { range: '55+', percentage: 2.5 }
    ],
    gender: [
      { type: 'Male', percentage: 67.3 },
      { type: 'Female', percentage: 31.2 },
      { type: 'Other', percentage: 1.5 }
    ],
    topCountries: [
      { country: 'United States', percentage: 34.2 },
      { country: 'United Kingdom', percentage: 12.8 },
      { country: 'Canada', percentage: 9.1 },
      { country: 'Australia', percentage: 6.7 },
      { country: 'Germany', percentage: 5.9 }
    ]
  }
};

const StatCard = ({ title, value, change, icon: Icon, trend, prefix = '', suffix = '' }) => (
  <motion.div 
    className="glass-card group hover:shadow-xl transition-all duration-300"
    whileHover={{ y: -4, scale: 1.02 }}
    initial={{ opacity: 0, y: 20 }}
    animate={{ opacity: 1, y: 0 }}
  >
    <div className="flex items-center justify-between">
      <div className="flex-1">
        <p className="text-sm font-medium text-slate-600 dark:text-slate-400 mb-1">{title}</p>
        <p className="text-3xl font-bold text-slate-900 dark:text-white">
          {prefix}{typeof value === 'number' ? value.toLocaleString() : value}{suffix}
        </p>
        <div className={`flex items-center mt-3 text-sm font-medium ${
          trend === 'up' ? 'text-emerald-600 dark:text-emerald-400' : 'text-red-600 dark:text-red-400'
        }`}>
          {trend === 'up' ? <ArrowUpRight className="h-4 w-4 mr-1" /> : <ArrowDownRight className="h-4 w-4 mr-1" />}
          <span>{Math.abs(change)}%</span>
          <span className="text-slate-500 dark:text-slate-400 ml-1 font-normal">vs last month</span>
        </div>
      </div>
      <motion.div 
        className={`p-4 rounded-2xl ${
          trend === 'up' 
            ? 'bg-emerald-100 dark:bg-emerald-900/30' 
            : 'bg-red-100 dark:bg-red-900/30'
        } group-hover:scale-110 transition-transform duration-200`}
        whileHover={{ rotate: 5 }}
      >
        <Icon className={`h-8 w-8 ${
          trend === 'up' 
            ? 'text-emerald-600 dark:text-emerald-400' 
            : 'text-red-600 dark:text-red-400'
        }`} />
      </motion.div>
    </div>
  </motion.div>
);

const ABTestCard = ({ test, index }) => (
  <motion.div
    className="glass-card hover:shadow-lg transition-all duration-300"
    initial={{ opacity: 0, x: -20 }}
    animate={{ opacity: 1, x: 0 }}
    transition={{ delay: index * 0.1 }}
    whileHover={{ y: -2 }}
  >
    <div className="flex items-center justify-between mb-4">
      <div className="flex items-center space-x-3">
        <div className={`p-2 rounded-lg ${
          test.status === 'running' 
            ? 'bg-blue-100 dark:bg-blue-900/30' 
            : 'bg-emerald-100 dark:bg-emerald-900/30'
        }`}>
          <TestTube className={`h-5 w-5 ${
            test.status === 'running' 
              ? 'text-blue-600 dark:text-blue-400' 
              : 'text-emerald-600 dark:text-emerald-400'
          }`} />
        </div>
        <div>
          <h3 className="font-semibold text-slate-900 dark:text-white">{test.name}</h3>
          <p className="text-sm text-slate-500 dark:text-slate-400">
            {test.startDate} - {test.endDate}
          </p>
        </div>
      </div>
      <div className={`px-3 py-1 rounded-full text-xs font-medium ${
        test.status === 'running'
          ? 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300'
          : 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-300'
      }`}>
        {test.status}
      </div>
    </div>

    <div className="grid grid-cols-2 gap-4 mb-4">
      {test.variants.map((variant, idx) => (
        <div key={idx} className={`p-3 rounded-lg border-2 transition-all ${
          test.winner === variant.name
            ? 'border-emerald-500 bg-emerald-50 dark:bg-emerald-900/20'
            : 'border-slate-200 dark:border-slate-700'
        }`}>
          <div className="flex items-center justify-between mb-2">
            <span className="font-medium text-slate-900 dark:text-white">{variant.name}</span>
            {test.winner === variant.name && (
              <Trophy className="h-4 w-4 text-emerald-600 dark:text-emerald-400" />
            )}
          </div>
          <div className="space-y-1 text-sm">
            <div className="flex justify-between">
              <span className="text-slate-600 dark:text-slate-400">Views:</span>
              <span className="font-medium">{variant.views.toLocaleString()}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-600 dark:text-slate-400">CTR:</span>
              <span className="font-medium">{variant.ctr}%</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-600 dark:text-slate-400">Conversions:</span>
              <span className="font-medium">{variant.conversions}</span>
            </div>
          </div>
        </div>
      ))}
    </div>

    <div className="flex items-center justify-between pt-3 border-t border-slate-200 dark:border-slate-700">
      <div className="flex items-center space-x-4 text-sm">
        <div>
          <span className="text-slate-600 dark:text-slate-400">Confidence: </span>
          <span className="font-semibold text-slate-900 dark:text-white">{test.confidence}%</span>
        </div>
        <div>
          <span className="text-slate-600 dark:text-slate-400">Improvement: </span>
          <span className="font-semibold text-emerald-600 dark:text-emerald-400">+{test.improvement}%</span>
        </div>
      </div>
      <button className="btn-ghost text-sm">View Details</button>
    </div>
  </motion.div>
);

const VideoPerformanceCard = ({ video, index }) => (
  <motion.div
    className="glass-card group hover:shadow-lg transition-all duration-300"
    initial={{ opacity: 0, y: 20 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{ delay: index * 0.1 }}
    whileHover={{ y: -2 }}
  >
    <div className="flex space-x-4">
      <div className="relative flex-shrink-0">
        <div className="w-24 h-16 bg-gradient-to-br from-slate-200 to-slate-300 dark:from-slate-700 dark:to-slate-800 rounded-lg overflow-hidden">
          <div className="w-full h-full flex items-center justify-center">
            <Play className="h-6 w-6 text-slate-400 dark:text-slate-500" />
          </div>
        </div>
        <div className="absolute top-1 right-1 px-1 py-0.5 bg-black/70 text-white text-xs rounded">
          {video.engagement}%
        </div>
      </div>
      
      <div className="flex-1 min-w-0">
        <h3 className="font-semibold text-slate-900 dark:text-white group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors line-clamp-2 mb-2">
          {video.title}
        </h3>
        
        <div className="grid grid-cols-3 gap-4 text-sm">
          <div>
            <p className="text-slate-500 dark:text-slate-400">Views</p>
            <p className="font-semibold text-slate-900 dark:text-white">{video.views.toLocaleString()}</p>
          </div>
          <div>
            <p className="text-slate-500 dark:text-slate-400">Revenue</p>
            <p className="font-semibold text-emerald-600 dark:text-emerald-400">${video.revenue}</p>
          </div>
          <div>
            <p className="text-slate-500 dark:text-slate-400">Published</p>
            <p className="font-semibold text-slate-900 dark:text-white">
              {new Date(video.published).toLocaleDateString()}
            </p>
          </div>
        </div>
      </div>
      
      <button className="p-2 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors opacity-0 group-hover:opacity-100">
        <ExternalLink className="h-4 w-4 text-slate-500 dark:text-slate-400" />
      </button>
    </div>
  </motion.div>
);

export default function AdvancedAnalyticsDashboard() {
  const [timeRange, setTimeRange] = useState('30d');
  const [activeTab, setActiveTab] = useState('overview');
  const [isRefreshing, setIsRefreshing] = useState(false);

  const tabs = [
    { id: 'overview', name: 'Overview', icon: BarChart3 },
    { id: 'performance', name: 'Performance', icon: TrendingUp },
    { id: 'abtesting', name: 'A/B Testing', icon: TestTube },
    { id: 'revenue', name: 'Revenue', icon: DollarSign },
    { id: 'audience', name: 'Audience', icon: Users },
  ];

  // Chart configurations
  const performanceChartData = {
    labels: mockAnalyticsData.performanceMetrics.last30Days.map(d => 
      new Date(d.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
    ),
    datasets: [
      {
        label: 'Views',
        data: mockAnalyticsData.performanceMetrics.last30Days.map(d => d.views),
        borderColor: 'rgb(59, 130, 246)',
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        tension: 0.4,
        fill: true,
      },
      {
        label: 'Subscribers',
        data: mockAnalyticsData.performanceMetrics.last30Days.map(d => d.subscribers),
        borderColor: 'rgb(16, 185, 129)',
        backgroundColor: 'rgba(16, 185, 129, 0.1)',
        tension: 0.4,
        fill: true,
        yAxisID: 'y1',
      }
    ],
  };

  const revenueChartData = {
    labels: mockAnalyticsData.revenueBreakdown.monthly.map(d => d.month),
    datasets: [
      {
        label: 'Monthly Revenue',
        data: mockAnalyticsData.revenueBreakdown.monthly.map(d => d.revenue),
        backgroundColor: 'rgba(168, 85, 247, 0.8)',
        borderColor: 'rgba(168, 85, 247, 1)',
        borderWidth: 2,
        borderRadius: 8,
      }
    ],
  };

  const revenueSourcesData = {
    labels: mockAnalyticsData.revenueBreakdown.sources.map(s => s.name),
    datasets: [
      {
        data: mockAnalyticsData.revenueBreakdown.sources.map(s => s.value),
        backgroundColor: [
          'rgba(239, 68, 68, 0.8)',
          'rgba(59, 130, 246, 0.8)',
          'rgba(16, 185, 129, 0.8)',
          'rgba(245, 158, 11, 0.8)',
        ],
        borderWidth: 0,
      }
    ],
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top' as const,
      },
    },
    scales: {
      y: {
        type: 'linear' as const,
        display: true,
        position: 'left' as const,
      },
      y1: {
        type: 'linear' as const,
        display: true,
        position: 'right' as const,
        grid: {
          drawOnChartArea: false,
        },
      },
    },
  };

  const handleRefresh = async () => {
    setIsRefreshing(true);
    await new Promise(resolve => setTimeout(resolve, 2000));
    setIsRefreshing(false);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <motion.div 
        className="flex flex-col lg:flex-row lg:items-center lg:justify-between space-y-4 lg:space-y-0"
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <div>
          <h1 className="text-3xl font-bold gradient-text">Advanced Analytics</h1>
          <p className="text-slate-600 dark:text-slate-400 mt-1">
            Comprehensive performance insights and A/B testing results
          </p>
        </div>
        
        <div className="flex items-center space-x-3">
          <select 
            value={timeRange}
            onChange={(e) => setTimeRange(e.target.value)}
            className="input text-sm w-auto"
          >
            <option value="7d">Last 7 days</option>
            <option value="30d">Last 30 days</option>
            <option value="90d">Last 90 days</option>
            <option value="1y">Last year</option>
          </select>
          
          <motion.button
            onClick={handleRefresh}
            disabled={isRefreshing}
            className="btn-secondary flex items-center space-x-2"
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
          >
            <RefreshCw className={`h-4 w-4 ${isRefreshing ? 'animate-spin' : ''}`} />
            <span>Refresh</span>
          </motion.button>
          
          <button className="btn-ghost flex items-center space-x-2">
            <Download className="h-4 w-4" />
            <span>Export</span>
          </button>
        </div>
      </motion.div>

      {/* Navigation Tabs */}
      <div className="border-b border-slate-200 dark:border-slate-700">
        <nav className="-mb-px flex space-x-8">
          {tabs.map((tab) => (
            <motion.button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center space-x-2 py-2 px-1 border-b-2 font-medium text-sm transition-colors ${
                activeTab === tab.id
                  ? 'border-blue-500 text-blue-600 dark:text-blue-400'
                  : 'border-transparent text-slate-500 hover:text-slate-700 hover:border-slate-300 dark:text-slate-400 dark:hover:text-slate-300'
              }`}
              whileHover={{ y: -1 }}
              whileTap={{ y: 0 }}
            >
              <tab.icon className="h-4 w-4" />
              <span>{tab.name}</span>
            </motion.button>
          ))}
        </nav>
      </div>

      <AnimatePresence mode="wait">
        {activeTab === 'overview' && (
          <motion.div
            key="overview"
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            transition={{ duration: 0.3 }}
            className="space-y-6"
          >
            {/* Overview Stats */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <StatCard
                title="Total Views"
                value={mockAnalyticsData.overview.totalViews}
                change={mockAnalyticsData.overview.trends.views.value}
                icon={Eye}
                trend="up"
              />
              <StatCard
                title="Subscribers"
                value={mockAnalyticsData.overview.totalSubscribers}
                change={mockAnalyticsData.overview.trends.subscribers.value}
                icon={Users}
                trend="up"
              />
              <StatCard
                title="Revenue"
                value={mockAnalyticsData.overview.totalRevenue}
                change={mockAnalyticsData.overview.trends.revenue.value}
                icon={DollarSign}
                trend="up"
                prefix="$"
              />
              <StatCard
                title="Engagement Rate"
                value={mockAnalyticsData.overview.engagementRate}
                change={Math.abs(mockAnalyticsData.overview.trends.engagement.value)}
                icon={Heart}
                trend={mockAnalyticsData.overview.trends.engagement.value > 0 ? 'up' : 'down'}
                suffix="%"
              />
            </div>

            {/* Performance Chart */}
            <motion.div 
              className="glass-card"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
            >
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-semibold text-slate-900 dark:text-white">Performance Trends</h2>
                <div className="flex items-center space-x-2">
                  <button className="btn-ghost text-sm">Views</button>
                  <button className="btn-ghost text-sm">Engagement</button>
                  <button className="btn-ghost text-sm">Revenue</button>
                </div>
              </div>
              <div className="h-80">
                <Line data={performanceChartData} options={chartOptions} />
              </div>
            </motion.div>

            {/* Top Videos */}
            <motion.div 
              className="glass-card"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
            >
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-semibold text-slate-900 dark:text-white">Top Performing Videos</h2>
                <button className="btn-ghost text-sm">View All</button>
              </div>
              <div className="space-y-4">
                {mockAnalyticsData.topVideos.map((video, index) => (
                  <VideoPerformanceCard key={video.id} video={video} index={index} />
                ))}
              </div>
            </motion.div>
          </motion.div>
        )}

        {activeTab === 'abtesting' && (
          <motion.div
            key="abtesting"
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            transition={{ duration: 0.3 }}
            className="space-y-6"
          >
            {/* A/B Testing Header */}
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-2xl font-bold text-slate-900 dark:text-white">A/B Testing Center</h2>
                <p className="text-slate-600 dark:text-slate-400">Optimize your content with data-driven testing</p>
              </div>
              <motion.button 
                className="btn-primary flex items-center space-x-2"
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                <TestTube className="h-4 w-4" />
                <span>Create New Test</span>
              </motion.button>
            </div>

            {/* Active Tests */}
            <div className="space-y-4">
              {mockAnalyticsData.abTests.map((test, index) => (
                <ABTestCard key={test.id} test={test} index={index} />
              ))}
            </div>

            {/* Testing Insights */}
            <motion.div 
              className="glass-card"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
            >
              <div className="flex items-center space-x-3 mb-6">
                <div className="p-2 bg-blue-100 dark:bg-blue-900/30 rounded-lg">
                  <Lightbulb className="h-5 w-5 text-blue-600 dark:text-blue-400" />
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-slate-900 dark:text-white">Testing Insights</h3>
                  <p className="text-sm text-slate-600 dark:text-slate-400">AI-powered recommendations for your next tests</p>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="p-4 bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 rounded-lg border border-blue-200 dark:border-blue-700">
                  <h4 className="font-semibold text-blue-900 dark:text-blue-300 mb-2">Recommended Test</h4>
                  <p className="text-sm text-blue-800 dark:text-blue-200">
                    Test video upload times: Your audience is most active between 6-8 PM EST. 
                    Try splitting uploads between 6 PM and 7 PM to optimize engagement.
                  </p>
                </div>
                
                <div className="p-4 bg-gradient-to-r from-emerald-50 to-teal-50 dark:from-emerald-900/20 dark:to-teal-900/20 rounded-lg border border-emerald-200 dark:border-emerald-700">
                  <h4 className="font-semibold text-emerald-900 dark:text-emerald-300 mb-2">Success Pattern</h4>
                  <p className="text-sm text-emerald-800 dark:text-emerald-200">
                    Longer titles (60+ characters) consistently outperform shorter ones by 18% 
                    in your niche. Consider testing even longer descriptive titles.
                  </p>
                </div>
              </div>
            </motion.div>
          </motion.div>
        )}

        {activeTab === 'revenue' && (
          <motion.div
            key="revenue"
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            transition={{ duration: 0.3 }}
            className="space-y-6"
          >
            {/* Revenue Overview */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <motion.div 
                className="glass-card"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1 }}
              >
                <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-4">Monthly Revenue Trend</h3>
                <div className="h-64">
                  <Bar data={revenueChartData} options={{ responsive: true, maintainAspectRatio: false }} />
                </div>
              </motion.div>

              <motion.div 
                className="glass-card"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2 }}
              >
                <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-4">Revenue Sources</h3>
                <div className="h-64">
                  <Doughnut data={revenueSourcesData} options={{ responsive: true, maintainAspectRatio: false }} />
                </div>
              </motion.div>
            </div>

            {/* Revenue Breakdown */}
            <motion.div 
              className="glass-card"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
            >
              <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-6">Revenue Source Breakdown</h3>
              <div className="space-y-4">
                {mockAnalyticsData.revenueBreakdown.sources.map((source, index) => (
                  <motion.div 
                    key={source.name}
                    className="flex items-center justify-between p-4 bg-slate-50 dark:bg-slate-800/50 rounded-lg"
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.1 }}
                  >
                    <div className="flex items-center space-x-3">
                      <div className="w-4 h-4 rounded-full" style={{
                        backgroundColor: ['#ef4444', '#3b82f6', '#10b981', '#f59e0b'][index]
                      }} />
                      <span className="font-medium text-slate-900 dark:text-white">{source.name}</span>
                    </div>
                    <div className="text-right">
                      <div className="font-semibold text-slate-900 dark:text-white">${source.value.toLocaleString()}</div>
                      <div className="text-sm text-slate-500 dark:text-slate-400">{source.percentage}%</div>
                    </div>
                  </motion.div>
                ))}
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}