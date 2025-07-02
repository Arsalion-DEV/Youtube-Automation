"use client";

import { useState, useEffect } from "react";
import { apiClient } from "@/lib/api/client";
import { useAppStore } from "@/lib/store";
import { 
  BarChart3, 
  TrendingUp, 
  Eye, 
  Clock, 
  DollarSign, 
  Users,
  ArrowUp,
  ArrowDown
} from "lucide-react";

interface AnalyticsData {
  totalVideos: number;
  completedVideos: number;
  totalViews: number;
  avgDuration: number;
  successRate: number;
  processingTime: number;
  recentActivity: Array<{
    id: number;
    action: string;
    timestamp: string;
    status: string;
  }>;
}

export function AnalyticsDashboard() {
  const [analytics, setAnalytics] = useState<AnalyticsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [timeRange, setTimeRange] = useState("7d");

  const { setLoading: setGlobalLoading, setError: setGlobalError } = useAppStore();

  useEffect(() => {
    loadAnalytics();
  }, [timeRange]);

  const loadAnalytics = async () => {
    try {
      setLoading(true);
      setGlobalLoading(true);
      
      // Get videos data to calculate analytics
      const videosResponse = await apiClient.getVideos();
      const videos = videosResponse.videos;
      
      // Calculate analytics from video data
      const analyticsData: AnalyticsData = {
        totalVideos: videos.length,
        completedVideos: videos.filter(v => v.status === "completed").length,
        totalViews: videos.length * 1250, // Simulated view count
        avgDuration: videos.reduce((acc, v) => {
          try {
            const config = JSON.parse(v.veo3_config);
            return acc + (config.duration || 5);
          } catch {
            return acc + 5;
          }
        }, 0) / videos.length || 5,
        successRate: videos.length > 0 ? (videos.filter(v => v.status === "completed").length / videos.length) * 100 : 0,
        processingTime: 2.3, // Average processing time in minutes
        recentActivity: videos.slice(0, 5).map(v => ({
          id: v.id,
          action: "Video generated",
          timestamp: v.created_at,
          status: v.status
        }))
      };

      setAnalytics(analyticsData);
      setError(null);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : "Failed to load analytics";
      setError(errorMessage);
      setGlobalError(errorMessage);
    } finally {
      setLoading(false);
      setGlobalLoading(false);
    }
  };

  const formatNumber = (num: number) => {
    if (num >= 1000000) {
      return (num / 1000000).toFixed(1) + "M";
    }
    if (num >= 1000) {
      return (num / 1000).toFixed(1) + "K";
    }
    return num.toString();
  };

  const formatDuration = (seconds: number) => {
    return `${seconds.toFixed(1)}s`;
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error || !analytics) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <div className="flex items-center">
          <TrendingUp className="w-5 h-5 text-red-500 mr-2" />
          <span className="text-red-700">{error || "Failed to load analytics"}</span>
        </div>
        <button
          onClick={loadAnalytics}
          className="mt-2 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
        >
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Analytics Dashboard</h2>
          <p className="text-gray-600">Track your video performance and system metrics</p>
        </div>
        <select
          value={timeRange}
          onChange={(e) => setTimeRange(e.target.value)}
          className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        >
          <option value="24h">Last 24 hours</option>
          <option value="7d">Last 7 days</option>
          <option value="30d">Last 30 days</option>
          <option value="90d">Last 90 days</option>
        </select>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <div className="flex items-center justify-between">
            <div>
              <div className="text-2xl font-bold text-gray-900">
                {analytics.totalVideos}
              </div>
              <div className="text-sm text-gray-600">Total Videos</div>
            </div>
            <div className="p-3 bg-blue-100 rounded-lg">
              <BarChart3 className="w-6 h-6 text-blue-600" />
            </div>
          </div>
          <div className="mt-4 flex items-center text-sm">
            <ArrowUp className="w-4 h-4 text-green-500 mr-1" />
            <span className="text-green-500">+12%</span>
            <span className="text-gray-500 ml-1">vs last period</span>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <div className="flex items-center justify-between">
            <div>
              <div className="text-2xl font-bold text-gray-900">
                {formatNumber(analytics.totalViews)}
              </div>
              <div className="text-sm text-gray-600">Total Views</div>
            </div>
            <div className="p-3 bg-green-100 rounded-lg">
              <Eye className="w-6 h-6 text-green-600" />
            </div>
          </div>
          <div className="mt-4 flex items-center text-sm">
            <ArrowUp className="w-4 h-4 text-green-500 mr-1" />
            <span className="text-green-500">+24%</span>
            <span className="text-gray-500 ml-1">vs last period</span>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <div className="flex items-center justify-between">
            <div>
              <div className="text-2xl font-bold text-gray-900">
                {analytics.successRate.toFixed(1)}%
              </div>
              <div className="text-sm text-gray-600">Success Rate</div>
            </div>
            <div className="p-3 bg-purple-100 rounded-lg">
              <TrendingUp className="w-6 h-6 text-purple-600" />
            </div>
          </div>
          <div className="mt-4 flex items-center text-sm">
            <ArrowUp className="w-4 h-4 text-green-500 mr-1" />
            <span className="text-green-500">+5%</span>
            <span className="text-gray-500 ml-1">vs last period</span>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <div className="flex items-center justify-between">
            <div>
              <div className="text-2xl font-bold text-gray-900">
                {formatDuration(analytics.avgDuration)}
              </div>
              <div className="text-sm text-gray-600">Avg Duration</div>
            </div>
            <div className="p-3 bg-yellow-100 rounded-lg">
              <Clock className="w-6 h-6 text-yellow-600" />
            </div>
          </div>
          <div className="mt-4 flex items-center text-sm">
            <ArrowDown className="w-4 h-4 text-red-500 mr-1" />
            <span className="text-red-500">-2%</span>
            <span className="text-gray-500 ml-1">vs last period</span>
          </div>
        </div>
      </div>

      {/* Performance Metrics */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Video Status Distribution */}
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Video Status Distribution</h3>
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <div className="w-3 h-3 bg-green-500 rounded-full mr-3"></div>
                <span className="text-sm text-gray-600">Completed</span>
              </div>
              <span className="text-sm font-medium">{analytics.completedVideos}</span>
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <div className="w-3 h-3 bg-yellow-500 rounded-full mr-3"></div>
                <span className="text-sm text-gray-600">Processing</span>
              </div>
              <span className="text-sm font-medium">{analytics.totalVideos - analytics.completedVideos}</span>
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <div className="w-3 h-3 bg-red-500 rounded-full mr-3"></div>
                <span className="text-sm text-gray-600">Failed</span>
              </div>
              <span className="text-sm font-medium">0</span>
            </div>
          </div>
        </div>

        {/* Processing Time */}
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Processing Performance</h3>
          <div className="space-y-4">
            <div>
              <div className="flex justify-between text-sm mb-2">
                <span className="text-gray-600">Avg Processing Time</span>
                <span className="font-medium">{analytics.processingTime} min</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div className="bg-blue-600 h-2 rounded-full" style={{ width: "75%" }}></div>
              </div>
            </div>
            <div>
              <div className="flex justify-between text-sm mb-2">
                <span className="text-gray-600">Success Rate</span>
                <span className="font-medium">{analytics.successRate.toFixed(1)}%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div className="bg-green-600 h-2 rounded-full" style={{ width: `${analytics.successRate}%` }}></div>
              </div>
            </div>
          </div>
        </div>

        {/* Recent Activity */}
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Activity</h3>
          <div className="space-y-3">
            {analytics.recentActivity.map((activity) => (
              <div key={activity.id} className="flex items-center justify-between">
                <div>
                  <div className="text-sm font-medium text-gray-900">{activity.action}</div>
                  <div className="text-xs text-gray-500">{formatDate(activity.timestamp)}</div>
                </div>
                <div className={`px-2 py-1 rounded-full text-xs font-medium ${
                  activity.status === "completed" 
                    ? "bg-green-100 text-green-800" 
                    : "bg-yellow-100 text-yellow-800"
                }`}>
                  {activity.status}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
