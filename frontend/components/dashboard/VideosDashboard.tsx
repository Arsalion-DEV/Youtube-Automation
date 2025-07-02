"use client";

import { useState, useEffect } from "react";
import { apiClient } from "@/lib/api/client";
import { useAppStore } from "@/lib/store";
import { Play, Clock, CheckCircle, AlertCircle, Plus } from "lucide-react";

interface Video {
  id: number;
  title: string;
  description: string;
  status: string;
  veo3_config: string;
  result_url: string;
  created_at: string;
  updated_at: string;
}

export function VideosDashboard() {
  const [videos, setVideos] = useState<Video[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showCreateModal, setShowCreateModal] = useState(false);

  const { setLoading: setGlobalLoading, setError: setGlobalError } = useAppStore();

  useEffect(() => {
    loadVideos();
  }, []);

  const loadVideos = async () => {
    try {
      setLoading(true);
      setGlobalLoading(true);
      const response = await apiClient.getVideos();
      setVideos(response.videos);
      setError(null);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : "Failed to load videos";
      setError(errorMessage);
      setGlobalError(errorMessage);
    } finally {
      setLoading(false);
      setGlobalLoading(false);
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "completed":
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      case "processing":
        return <Clock className="w-5 h-5 text-yellow-500 animate-spin" />;
      case "failed":
        return <AlertCircle className="w-5 h-5 text-red-500" />;
      default:
        return <Clock className="w-5 h-5 text-gray-500" />;
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  const getVeo3Config = (configString: string | null) => {
    if (!configString) {
      return {};
    }
    try {
      return JSON.parse(configString);
    } catch {
      return {};
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <div className="flex items-center">
          <AlertCircle className="w-5 h-5 text-red-500 mr-2" />
          <span className="text-red-700">{error}</span>
        </div>
        <button
          onClick={loadVideos}
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
          <h2 className="text-2xl font-bold text-gray-900">Video Library</h2>
          <p className="text-gray-600">Manage your VEO3 generated videos</p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          <Plus className="w-4 h-4" />
          Create Video
        </button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <div className="text-2xl font-bold text-gray-900">{videos.length}</div>
          <div className="text-sm text-gray-600">Total Videos</div>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <div className="text-2xl font-bold text-green-600">
            {videos.filter(v => v.status === "completed").length}
          </div>
          <div className="text-sm text-gray-600">Completed</div>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <div className="text-2xl font-bold text-yellow-600">
            {videos.filter(v => v.status === "processing").length}
          </div>
          <div className="text-sm text-gray-600">Processing</div>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <div className="text-2xl font-bold text-red-600">
            {videos.filter(v => v.status === "failed").length}
          </div>
          <div className="text-sm text-gray-600">Failed</div>
        </div>
      </div>

      {/* Videos Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {videos.map((video) => {
          const config = getVeo3Config(video.veo3_config);
          return (
            <div key={video.id} className="bg-white rounded-lg shadow-sm border overflow-hidden">
              {/* Video Preview */}
              <div className="aspect-video bg-gray-100 flex items-center justify-center">
                {video.status === "completed" ? (
                  <div className="relative w-full h-full">
                    <video
                      className="w-full h-full object-cover"
                      controls
                      poster="data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMzIwIiBoZWlnaHQ9IjE4MCIgdmlld0JveD0iMCAwIDMyMCAxODAiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxyZWN0IHdpZHRoPSIzMjAiIGhlaWdodD0iMTgwIiBmaWxsPSIjRjNGNEY2Ii8+CjxwYXRoIGQ9Ik0xMjUgNzVMMTc1IDEwNUwxMjUgMTM1VjEwNVY3NVoiIGZpbGw9IiM2QjczODAiLz4KPC9zdmc+"
                    >
                      <source src={video.result_url} type="video/mp4" />
                      Your browser does not support the video tag.
                    </video>
                  </div>
                ) : (
                  <div className="flex flex-col items-center justify-center text-gray-500">
                    <Play className="w-12 h-12 mb-2" />
                    <span className="text-sm">Video {video.status}</span>
                  </div>
                )}
              </div>

              {/* Video Details */}
              <div className="p-4">
                <div className="flex items-center justify-between mb-2">
                  <h3 className="font-semibold text-gray-900 truncate">{video.title}</h3>
                  {getStatusIcon(video.status)}
                </div>
                
                <p className="text-sm text-gray-600 mb-3 line-clamp-2">
                  {config.prompt || "No description"}
                </p>

                <div className="space-y-2 text-xs text-gray-500">
                  <div className="flex justify-between">
                    <span>Duration:</span>
                    <span>{config.duration || 5}s</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Quality:</span>
                    <span className="font-medium">{config.quality || "veo-3"}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Created:</span>
                    <span>{formatDate(video.created_at)}</span>
                  </div>
                </div>

                {video.status === "completed" && (
                  <div className="mt-4 flex gap-2">
                    <a
                      href={video.result_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex-1 px-3 py-2 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700 transition-colors text-center"
                    >
                      View Video
                    </a>
                    <button className="px-3 py-2 border border-gray-300 text-gray-700 text-sm rounded-lg hover:bg-gray-50 transition-colors">
                      Share
                    </button>
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>

      {videos.length === 0 && (
        <div className="text-center py-12">
          <Play className="w-16 h-16 text-gray-300 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No videos yet</h3>
          <p className="text-gray-600 mb-4">Create your first video to get started</p>
          <button
            onClick={() => setShowCreateModal(true)}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            Create Video
          </button>
        </div>
      )}
    </div>
  );
}
