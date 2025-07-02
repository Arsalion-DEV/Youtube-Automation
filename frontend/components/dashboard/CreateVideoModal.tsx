"use client";

import { useState } from "react";
import { apiClient } from "@/lib/api/client";
import { useAppStore } from "@/lib/store";
import { X, Sparkles, Settings, Play } from "lucide-react";

interface CreateVideoModalProps {
  isOpen: boolean;
  onClose: () => void;
  onVideoCreated: () => void;
}

export function CreateVideoModal({ isOpen, onClose, onVideoCreated }: CreateVideoModalProps) {
  const [formData, setFormData] = useState({
    title: "",
    description: "",
    prompt: "",
    duration: 5,
    quality: "veo-3",
    audio_mode: "full",
    temperature: 0.7,
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showAdvanced, setShowAdvanced] = useState(false);

  const { setLoading, setError } = useAppStore();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.prompt.trim()) {
      setError("Please enter a video prompt");
      return;
    }

    try {
      setIsSubmitting(true);
      setLoading(true);
      
      // First create the video record
      await apiClient.createVideo({
        title: formData.title || "Generated Video",
        description: formData.description,
      });

      // Then generate the VEO3 video
      await apiClient.generateVeo3Video({
        prompt: formData.prompt,
        duration: formData.duration,
        quality: formData.quality,
        audio_mode: formData.audio_mode,
        temperature: formData.temperature,
      });

      // Reset form and close modal
      setFormData({
        title: "",
        description: "",
        prompt: "",
        duration: 5,
        quality: "veo-3",
        audio_mode: "full",
        temperature: 0.7,
      });
      
      onVideoCreated();
      onClose();
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create video");
    } finally {
      setIsSubmitting(false);
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl shadow-xl w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-blue-100 rounded-lg">
              <Sparkles className="w-5 h-5 text-blue-600" />
            </div>
            <div>
              <h2 className="text-xl font-semibold text-gray-900">Create New Video</h2>
              <p className="text-sm text-gray-600">Generate AI-powered content with VEO3</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <X className="w-5 h-5 text-gray-500" />
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          {/* Basic Information */}
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Video Title
              </label>
              <input
                type="text"
                value={formData.title}
                onChange={(e) => setFormData(prev => ({ ...prev, title: e.target.value }))}
                placeholder="Enter video title (optional)"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Description
              </label>
              <textarea
                value={formData.description}
                onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
                placeholder="Brief description of your video (optional)"
                rows={2}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Video Prompt <span className="text-red-500">*</span>
              </label>
              <textarea
                value={formData.prompt}
                onChange={(e) => setFormData(prev => ({ ...prev, prompt: e.target.value }))}
                placeholder="Describe the video you want to generate (e.g., A peaceful sunset over calm ocean waters with gentle waves)"
                rows={4}
                required
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
              />
              <p className="text-xs text-gray-500 mt-1">
                Be specific and descriptive for best results
              </p>
            </div>
          </div>

          {/* Quick Settings */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Duration
              </label>
              <select
                value={formData.duration}
                onChange={(e) => setFormData(prev => ({ ...prev, duration: Number(e.target.value) }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value={3}>3 seconds</option>
                <option value={5}>5 seconds</option>
                <option value={8}>8 seconds</option>
                <option value={10}>10 seconds</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Quality
              </label>
              <select
                value={formData.quality}
                onChange={(e) => setFormData(prev => ({ ...prev, quality: e.target.value }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="veo-3">VEO-3 (Recommended)</option>
                <option value="veo-2">VEO-2</option>
              </select>
            </div>
          </div>

          {/* Advanced Settings Toggle */}
          <button
            type="button"
            onClick={() => setShowAdvanced(!showAdvanced)}
            className="flex items-center gap-2 text-sm text-gray-600 hover:text-gray-800 transition-colors"
          >
            <Settings className="w-4 h-4" />
            Advanced Settings
            <span className="text-xs bg-gray-100 px-2 py-1 rounded">
              {showAdvanced ? "Hide" : "Show"}
            </span>
          </button>

          {/* Advanced Settings */}
          {showAdvanced && (
            <div className="space-y-4 border-t pt-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Audio Mode
                </label>
                <select
                  value={formData.audio_mode}
                  onChange={(e) => setFormData(prev => ({ ...prev, audio_mode: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="full">Full Audio</option>
                  <option value="ambient">Ambient Only</option>
                  <option value="none">No Audio</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Creativity Level: {formData.temperature}
                </label>
                <input
                  type="range"
                  min="0.1"
                  max="1.0"
                  step="0.1"
                  value={formData.temperature}
                  onChange={(e) => setFormData(prev => ({ ...prev, temperature: Number(e.target.value) }))}
                  className="w-full"
                />
                <div className="flex justify-between text-xs text-gray-500 mt-1">
                  <span>Precise</span>
                  <span>Creative</span>
                </div>
              </div>
            </div>
          )}

          {/* Actions */}
          <div className="flex gap-3 pt-4 border-t">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 px-4 py-2 text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSubmitting || !formData.prompt.trim()}
              className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors flex items-center justify-center gap-2"
            >
              {isSubmitting ? (
                <>
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  Generating...
                </>
              ) : (
                <>
                  <Play className="w-4 h-4" />
                  Generate Video
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
