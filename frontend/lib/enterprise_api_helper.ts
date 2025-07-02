// Enterprise API Helper
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001'

export interface SystemHealth {
  timestamp: string
  database: boolean
  redis: boolean
  features: {
    analytics: boolean
    monetization: boolean
    ab_testing: boolean
  }
}

export interface AnalyticsData {
  success: boolean
  events: Array<{
    event_type: string
    count: number
    unique_users: number
    last_event: string
  }>
  generated_at: string
}

// System Health API
export async function getSystemHealth(): Promise<SystemHealth> {
  const response = await fetch(`${API_BASE_URL}/api/v1/enterprise/health`)
  if (!response.ok) throw new Error('Failed to fetch system health')
  return response.json()
}

// Analytics API
export async function getAnalyticsSummary(): Promise<AnalyticsData> {
  const response = await fetch(`${API_BASE_URL}/api/v1/enterprise/analytics/summary`)
  if (!response.ok) throw new Error('Failed to fetch analytics')
  return response.json()
}

// Monetization API
export async function trackRevenue(userId: string, amount: number, source: string) {
  const response = await fetch(`${API_BASE_URL}/api/v1/enterprise/monetization/track?user_id=${userId}&amount=${amount}&source=${encodeURIComponent(source)}`, {
    method: 'POST'
  })
  if (!response.ok) throw new Error('Failed to track revenue')
  return response.json()
}

// System Status API
export async function getSystemStatus() {
  const response = await fetch(`${API_BASE_URL}/api/system/status`)
  if (!response.ok) throw new Error('Failed to fetch system status')
  return response.json()
}

// Real-time hooks for React components
export function useSystemHealth() {
  const [health, setHealth] = React.useState<SystemHealth | null>(null)
  const [loading, setLoading] = React.useState(true)
  const [error, setError] = React.useState<string | null>(null)

  React.useEffect(() => {
    const fetchHealth = async () => {
      try {
        const data = await getSystemHealth()
        setHealth(data)
        setError(null)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unknown error')
      } finally {
        setLoading(false)
      }
    }

    fetchHealth()
    const interval = setInterval(fetchHealth, 30000) // Update every 30 seconds
    
    return () => clearInterval(interval)
  }, [])

  return { health, loading, error }
}

export function useAnalytics() {
  const [analytics, setAnalytics] = React.useState<AnalyticsData | null>(null)
  const [loading, setLoading] = React.useState(true)
  const [error, setError] = React.useState<string | null>(null)

  React.useEffect(() => {
    const fetchAnalytics = async () => {
      try {
        const data = await getAnalyticsSummary()
        setAnalytics(data)
        setError(null)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unknown error')
      } finally {
        setLoading(false)
      }
    }

    fetchAnalytics()
    const interval = setInterval(fetchAnalytics, 30000) // Update every 30 seconds
    
    return () => clearInterval(interval)
  }, [])

  return { analytics, loading, error, refetch: fetchAnalytics }
}