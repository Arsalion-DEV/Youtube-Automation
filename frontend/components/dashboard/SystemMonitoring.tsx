"use client";

import { useState, useEffect } from "react";
import { apiClient } from "@/lib/api/client";
import { useAppStore } from "@/lib/store";
import { 
  Activity, 
  Server, 
  Cpu, 
  HardDrive, 
  Wifi,
  AlertTriangle,
  CheckCircle,
  RefreshCw
} from "lucide-react";

interface SystemHealth {
  status: string;
  modules: Record<string, boolean>;
  timestamp: string;
}

interface SystemMetrics {
  cpu_usage: number;
  memory_usage: number;
  disk_usage: number;
  active_processes: number;
  api_response_time: number;
  uptime: string;
}

export function SystemMonitoring() {
  const [health, setHealth] = useState<SystemHealth | null>(null);
  const [metrics, setMetrics] = useState<SystemMetrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date());

  const { setLoading: setGlobalLoading, setError: setGlobalError } = useAppStore();

  useEffect(() => {
    loadSystemData();
    const interval = setInterval(loadSystemData, 30000); // Update every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const loadSystemData = async () => {
    try {
      setLoading(true);
      setGlobalLoading(true);

      const startTime = Date.now();
      const healthResponse = await apiClient.getHealth();
      const responseTime = Date.now() - startTime;

      setHealth({
        ...healthResponse,
        timestamp: new Date().toISOString(),
      });

      // Simulate system metrics (in a real app, these would come from the backend)
      setMetrics({
        cpu_usage: Math.random() * 30 + 10, // 10-40%
        memory_usage: Math.random() * 20 + 40, // 40-60%
        disk_usage: Math.random() * 10 + 25, // 25-35%
        active_processes: Math.floor(Math.random() * 5) + 3, // 3-8 processes
        api_response_time: responseTime,
        uptime: "2 days, 23 hours", // Would come from backend
      });

      setLastUpdate(new Date());
      setError(null);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : "Failed to load system data";
      setError(errorMessage);
      setGlobalError(errorMessage);
    } finally {
      setLoading(false);
      setGlobalLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "healthy":
        return "text-green-600";
      case "warning":
        return "text-yellow-600";
      case "error":
        return "text-red-600";
      default:
        return "text-gray-600";
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "healthy":
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      case "warning":
        return <AlertTriangle className="w-5 h-5 text-yellow-500" />;
      case "error":
        return <AlertTriangle className="w-5 h-5 text-red-500" />;
      default:
        return <Activity className="w-5 h-5 text-gray-500" />;
    }
  };

  const getUsageColor = (usage: number, thresholds = { warning: 70, critical: 90 }) => {
    if (usage >= thresholds.critical) return "bg-red-600";
    if (usage >= thresholds.warning) return "bg-yellow-600";
    return "bg-green-600";
  };

  if (loading && !health) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error && !health) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <div className="flex items-center">
          <AlertTriangle className="w-5 h-5 text-red-500 mr-2" />
          <span className="text-red-700">{error}</span>
        </div>
        <button
          onClick={loadSystemData}
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
          <h2 className="text-2xl font-bold text-gray-900">System Monitoring</h2>
          <p className="text-gray-600">Real-time system health and performance metrics</p>
        </div>
        <div className="flex items-center gap-4">
          <div className="text-sm text-gray-500">
            Last updated: {lastUpdate.toLocaleTimeString()}
          </div>
          <button
            onClick={loadSystemData}
            disabled={loading}
            className="flex items-center gap-2 px-3 py-2 text-sm bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors disabled:opacity-50"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? "animate-spin" : ""}`} />
            Refresh
          </button>
        </div>
      </div>

      {/* System Status */}
      <div className="bg-white p-6 rounded-lg shadow-sm border">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900">System Status</h3>
          <div className="flex items-center gap-2">
            {health && getStatusIcon(health.status)}
            <span className={`font-medium ${health && getStatusColor(health.status)}`}>
              {health?.status?.toUpperCase() || "UNKNOWN"}
            </span>
          </div>
        </div>

        {health && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {Object.entries(health.modules).map(([module, isHealthy]) => (
              <div key={module} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                <div className="flex items-center gap-3">
                  <div className={`w-3 h-3 rounded-full ${isHealthy ? "bg-green-500" : "bg-red-500"}`}></div>
                  <span className="font-medium text-gray-900 capitalize">
                    {module.replace("_", " ")}
                  </span>
                </div>
                <span className={`text-sm font-medium ${isHealthy ? "text-green-600" : "text-red-600"}`}>
                  {isHealthy ? "Online" : "Offline"}
                </span>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Performance Metrics */}
      {metrics && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="bg-white p-6 rounded-lg shadow-sm border">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-blue-100 rounded-lg">
                  <Cpu className="w-5 h-5 text-blue-600" />
                </div>
                <div>
                  <div className="text-sm text-gray-600">CPU Usage</div>
                  <div className="text-2xl font-bold text-gray-900">{metrics.cpu_usage.toFixed(1)}%</div>
                </div>
              </div>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div 
                className={`h-2 rounded-full transition-all duration-300 ${getUsageColor(metrics.cpu_usage)}`}
                style={{ width: `${metrics.cpu_usage}%` }}
              ></div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-sm border">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-green-100 rounded-lg">
                  <Activity className="w-5 h-5 text-green-600" />
                </div>
                <div>
                  <div className="text-sm text-gray-600">Memory Usage</div>
                  <div className="text-2xl font-bold text-gray-900">{metrics.memory_usage.toFixed(1)}%</div>
                </div>
              </div>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div 
                className={`h-2 rounded-full transition-all duration-300 ${getUsageColor(metrics.memory_usage)}`}
                style={{ width: `${metrics.memory_usage}%` }}
              ></div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-sm border">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-purple-100 rounded-lg">
                  <HardDrive className="w-5 h-5 text-purple-600" />
                </div>
                <div>
                  <div className="text-sm text-gray-600">Disk Usage</div>
                  <div className="text-2xl font-bold text-gray-900">{metrics.disk_usage.toFixed(1)}%</div>
                </div>
              </div>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div 
                className={`h-2 rounded-full transition-all duration-300 ${getUsageColor(metrics.disk_usage)}`}
                style={{ width: `${metrics.disk_usage}%` }}
              ></div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-sm border">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-yellow-100 rounded-lg">
                  <Wifi className="w-5 h-5 text-yellow-600" />
                </div>
                <div>
                  <div className="text-sm text-gray-600">API Response</div>
                  <div className="text-2xl font-bold text-gray-900">{metrics.api_response_time}ms</div>
                </div>
              </div>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div 
                className={`h-2 rounded-full transition-all duration-300 ${
                  metrics.api_response_time < 100 ? "bg-green-600" : 
                  metrics.api_response_time < 500 ? "bg-yellow-600" : "bg-red-600"
                }`}
                style={{ width: `${Math.min((metrics.api_response_time / 1000) * 100, 100)}%` }}
              ></div>
            </div>
          </div>
        </div>
      )}

      {/* System Information */}
      {metrics && (
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">System Information</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-gray-600">System Uptime</span>
                <span className="font-medium">{metrics.uptime}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Active Processes</span>
                <span className="font-medium">{metrics.active_processes}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">API Response Time</span>
                <span className="font-medium">{metrics.api_response_time}ms</span>
              </div>
            </div>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-gray-600">Platform Version</span>
                <span className="font-medium">v1.0.0</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Environment</span>
                <span className="font-medium">Production</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Last Health Check</span>
                <span className="font-medium">{lastUpdate.toLocaleTimeString()}</span>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
