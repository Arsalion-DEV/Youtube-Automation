"use client"

import React, { useState, useEffect } from 'react'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Toaster } from '@/components/ui/toaster'
import { useToast } from '@/components/ui/use-toast'
import {
  AlertCircle,
  CheckCircle,
  Info,
  RefreshCw,
  Shield,
  Zap,
} from 'lucide-react'

interface SystemStatus {
  overall_status: 'healthy' | 'warning' | 'error'
  database: boolean
  redis: boolean
  enterprise_features: boolean
  analytics: boolean
  monetization: boolean
  ab_testing: boolean
  last_checked: string
}

interface Announcement {
  id: string
  type: 'info' | 'warning' | 'success' | 'error'
  title: string
  message: string
  timestamp: string
  dismissible: boolean
}

export default function EnterpriseApp({ children }: { children: React.ReactNode }) {
  const [systemStatus, setSystemStatus] = useState<SystemStatus | null>(null)
  const [announcements, setAnnouncements] = useState<Announcement[]>([])
  const [loading, setLoading] = useState(true)
  const { toast } = useToast()

  useEffect(() => {
    const checkSystemHealth = async () => {
      try {
        const response = await fetch('/api/v1/enterprise/health')
        if (response.ok) {
          const data = await response.json()
          setSystemStatus({
            overall_status: data.status === 'healthy' ? 'healthy' : 'warning',
            database: data.database || false,
            redis: data.redis || false,
            enterprise_features: data.enterprise_features || false,
            analytics: data.features?.analytics || false,
            monetization: data.features?.monetization || false,
            ab_testing: data.features?.ab_testing || false,
            last_checked: new Date().toISOString(),
          })
        } else {
          setSystemStatus({
            overall_status: 'error',
            database: false,
            redis: false,
            enterprise_features: false,
            analytics: false,
            monetization: false,
            ab_testing: false,
            last_checked: new Date().toISOString(),
          })
        }
      } catch (error) {
        console.error('Failed to check system health:', error)
        setSystemStatus({
          overall_status: 'error',
          database: false,
          redis: false,
          enterprise_features: false,
          analytics: false,
          monetization: false,
          ab_testing: false,
          last_checked: new Date().toISOString(),
        })
      } finally {
        setLoading(false)
      }
    }

    // Initial check
    checkSystemHealth()

    // Set up periodic health checks
    const interval = setInterval(checkSystemHealth, 60000) // Check every minute

    return () => clearInterval(interval)
  }, [])

  useEffect(() => {
    // Generate sample announcements based on system status
    if (systemStatus) {
      const newAnnouncements: Announcement[] = []

      if (systemStatus.overall_status === 'healthy' && systemStatus.enterprise_features) {
        newAnnouncements.push({
          id: 'welcome',
          type: 'success',
          title: 'Enterprise Platform Ready',
          message: 'All enterprise features are online and ready to use.',
          timestamp: new Date().toISOString(),
          dismissible: true,
        })
      }

      if (!systemStatus.database) {
        newAnnouncements.push({
          id: 'db-error',
          type: 'error',
          title: 'Database Connection Issue',
          message: 'Unable to connect to the database. Some features may be unavailable.',
          timestamp: new Date().toISOString(),
          dismissible: false,
        })
      }

      if (!systemStatus.redis) {
        newAnnouncements.push({
          id: 'redis-warning',
          type: 'warning',
          title: 'Cache System Offline',
          message: 'Redis cache is not available. Performance may be impacted.',
          timestamp: new Date().toISOString(),
          dismissible: true,
        })
      }

      if (systemStatus.enterprise_features && systemStatus.analytics && systemStatus.monetization) {
        newAnnouncements.push({
          id: 'features-ready',
          type: 'info',
          title: 'New Features Available',
          message: 'Advanced analytics and monetization tracking are now active.',
          timestamp: new Date().toISOString(),
          dismissible: true,
        })
      }

      setAnnouncements(newAnnouncements)
    }
  }, [systemStatus])

  const dismissAnnouncement = (id: string) => {
    setAnnouncements(prev => prev.filter(announcement => announcement.id !== id))
  }

  const refreshSystemStatus = async () => {
    setLoading(true)
    // Trigger a fresh system health check
    window.location.reload()
  }

  const getStatusIcon = (status: SystemStatus['overall_status']) => {
    switch (status) {
      case 'healthy':
        return <CheckCircle className="h-4 w-4 text-green-500" />
      case 'warning':
        return <AlertCircle className="h-4 w-4 text-yellow-500" />
      case 'error':
        return <AlertCircle className="h-4 w-4 text-red-500" />
      default:
        return <Info className="h-4 w-4 text-gray-500" />
    }
  }

  const getStatusBadgeVariant = (status: SystemStatus['overall_status']) => {
    switch (status) {
      case 'healthy':
        return 'default'
      case 'warning':
        return 'secondary'
      case 'error':
        return 'destructive'
      default:
        return 'outline'
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center space-y-4">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-gray-900 mx-auto"></div>
          <p className="text-muted-foreground">Initializing Enterprise Platform...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-background">
      {/* System Status Bar */}
      {systemStatus && (
        <div className="border-b bg-muted/50">
          <div className="container mx-auto px-4 py-2">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <div className="flex items-center space-x-2">
                  {getStatusIcon(systemStatus.overall_status)}
                  <span className="text-sm font-medium">System Status:</span>
                  <Badge variant={getStatusBadgeVariant(systemStatus.overall_status)}>
                    {systemStatus.overall_status.charAt(0).toUpperCase() + systemStatus.overall_status.slice(1)}
                  </Badge>
                </div>
                
                <div className="hidden md:flex items-center space-x-4 text-xs text-muted-foreground">
                  <div className="flex items-center space-x-1">
                    <div className={`w-2 h-2 rounded-full ${systemStatus.database ? 'bg-green-500' : 'bg-red-500'}`} />
                    <span>Database</span>
                  </div>
                  <div className="flex items-center space-x-1">
                    <div className={`w-2 h-2 rounded-full ${systemStatus.redis ? 'bg-green-500' : 'bg-red-500'}`} />
                    <span>Cache</span>
                  </div>
                  <div className="flex items-center space-x-1">
                    <div className={`w-2 h-2 rounded-full ${systemStatus.enterprise_features ? 'bg-green-500' : 'bg-red-500'}`} />
                    <span>Enterprise</span>
                  </div>
                </div>
              </div>
              
              <div className="flex items-center space-x-2">
                <span className="text-xs text-muted-foreground">
                  Last checked: {new Date(systemStatus.last_checked).toLocaleTimeString()}
                </span>
                <Button variant="ghost" size="sm" onClick={refreshSystemStatus}>
                  <RefreshCw className="h-3 w-3" />
                </Button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Announcements */}
      {announcements.length > 0 && (
        <div className="border-b">
          <div className="container mx-auto px-4 py-4 space-y-2">
            {announcements.map(announcement => (
              <Alert
                key={announcement.id}
                variant={announcement.type === 'error' ? 'destructive' : 'default'}
              >
                {announcement.type === 'success' && <CheckCircle className="h-4 w-4" />}
                {announcement.type === 'warning' && <AlertCircle className="h-4 w-4" />}
                {announcement.type === 'error' && <AlertCircle className="h-4 w-4" />}
                {announcement.type === 'info' && <Info className="h-4 w-4" />}
                <AlertTitle className="flex items-center justify-between">
                  {announcement.title}
                  {announcement.dismissible && (
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => dismissAnnouncement(announcement.id)}
                      className="h-auto p-1 text-muted-foreground hover:text-foreground"
                    >
                      ×
                    </Button>
                  )}
                </AlertTitle>
                <AlertDescription>{announcement.message}</AlertDescription>
              </Alert>
            ))}
          </div>
        </div>
      )}

      {/* Main Content */}
      <main className="container mx-auto px-4 py-6">
        {children}
      </main>

      {/* Enterprise Badge */}
      <div className="fixed bottom-4 right-4 z-50">
        <Card className="p-2">
          <div className="flex items-center space-x-2">
            <div className="w-6 h-6 bg-gradient-to-br from-blue-500 to-purple-600 rounded flex items-center justify-center">
              <Zap className="h-3 w-3 text-white" />
            </div>
            <div className="text-xs">
              <div className="font-semibold">Enterprise</div>
              <div className="text-muted-foreground">v2.0</div>
            </div>
          </div>
        </Card>
      </div>

      {/* Toast Notifications */}
      <Toaster />
    </div>
  )
}

// Named export for compatibility
export { EnterpriseApp }