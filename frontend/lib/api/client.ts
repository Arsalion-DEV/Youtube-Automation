const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://13.60.77.139:8001";

class ApiClient {
  private baseURL: string;

  constructor() {
    this.baseURL = API_BASE_URL;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseURL}${endpoint}`;
    
    const config: RequestInit = {
      headers: {
        "Content-Type": "application/json",
        ...options.headers,
      },
      ...options,
    };

    try {
      const response = await fetch(url, config);
      
      if (!response.ok) {
        throw new Error(`API Error: ${response.status} ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error("API Request failed:", error);
      throw error;
    }
  }

  // Health and System
  async getHealth() {
    return this.request<{
      status: string;
      modules: Record<string, boolean>;
    }>("/health");
  }

  async getApiInfo() {
    return this.request<{
      name: string;
      version: string;
      description: string;
      modules: string[];
      endpoints: string[];
    }>("/api/v2/info");
  }

  // Video Management - Using V2 endpoints
  async getVideos() {
    return this.request<{
      videos: Array<{
        id: number;
        title: string;
        description: string;
        status: string;
        veo3_config: string;
        result_url: string;
        created_at: string;
        updated_at: string;
      }>;
      total: number;
      limit: number;
      offset: number;
    }>("/api/v2/videos");
  }

  async getVideo(id: number) {
    return this.request(`/api/v2/videos/${id}`);
  }

  async createVideo(data: {
    title: string;
    description?: string;
  }) {
    return this.request("/api/v2/videos/create", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  // VEO3 Generation - Using V2 endpoints
  async generateVeo3Video(config: {
    prompt: string;
    duration?: number;
    quality?: string;
    audio_mode?: string;
    temperature?: number;
  }) {
    return this.request("/api/v2/veo3/generate", {
      method: "POST",
      body: JSON.stringify(config),
    });
  }

  // Task Management - Using V2 endpoints  
  async getTaskStatus(taskId: string) {
    return this.request(`/api/v2/tasks/status?task_id=${taskId}`);
  }

  // Analytics - Using V2 endpoints
  async getAnalyticsSummary() {
    return this.request("/api/v2/analytics/summary");
  }

  async getAnalyticsDashboard() {
    return this.request("/api/v2/analytics/dashboard");
  }

  // System Monitoring - Using V2 endpoints
  async getSystemStatus() {
    return this.request("/api/v2/system/status");
  }

  async getSystemMetrics() {
    return this.request("/api/v2/system/metrics");
  }
}

export const apiClient = new ApiClient();
