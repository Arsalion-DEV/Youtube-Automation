"use client"

import React, { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { 
  ArrowDownRight, 
  ArrowUpRight, 
  Award, 
  BarChart3, 
  CheckCircle, 
  Clock, 
  DollarSign, 
  Eye, 
  Globe, 
  MousePointer, 
  PlayCircle, 
  Settings, 
  Shield, 
  Smartphone, 
  Target, 
  TrendingUp, 
  Users, 
  Zap 
} from 'lucide-react'

interface AnalyticsData {
  totalViews: number
  totalRevenue: number
  activeTests: number
  conversionRate: number
  topPerformingVideo: string
  recentActivity: any[]
}

interface SystemHealth {
  database: boolean
  redis: boolean
  analytics: boolean
  monetization: boolean
  ab_testing: boolean
}

export default function EnterpriseMainDashboard() {
  const [analyticsData, setAnalyticsData] = useState<AnalyticsData>({
    totalViews: 0,
    totalRevenue: 0,
    activeTests: 0,
    conversionRate: 0,
    topPerformingVideo: 'N/A',
    recentActivity: []
  })
  
  const [systemHealth, setSystemHealth] = useState<SystemHealth>({
    database: false,
    redis: false,
    analytics: false,
    monetization: false,
    ab_testing: false
  })
  
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        // Fetch analytics summary
        const analyticsResponse = await fetch('/api/v1/enterprise/analytics/summary')
        if (analyticsResponse.ok) {
          const analytics = await analyticsResponse.json()
          setAnalyticsData(prev => ({
            ...prev,
            totalViews: analytics.events?.length || 0,
            recentActivity: analytics.events || []
          }))
        }

        // Fetch system health
        const healthResponse = await fetch('/api/v1/enterprise/health')
        if (healthResponse.ok) {
          const health = await healthResponse.json()
          setSystemHealth(health.features || {})
        }

        // Fetch monetization data
        const monetizationResponse = await fetch('/api/v1/enterprise/monetization/summary')
        if (monetizationResponse.ok) {
          const monetization = await monetizationResponse.json()
          setAnalyticsData(prev => ({
            ...prev,
            totalRevenue: monetization.total_revenue || 0
          }))
        }

        // Fetch A/B testing data
        const abTestResponse = await fetch('/api/v1/enterprise/ab-testing/tests')
        if (abTestResponse.ok) {
          const abTests = await abTestResponse.json()
          setAnalyticsData(prev => ({
            ...prev,
            activeTests: abTests.length || 0
          }))
        }

      } catch (error) {
        console.error('Error fetching dashboard data:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchDashboardData()
    const interval = setInterval(fetchDashboardData, 30000) // Refresh every 30 seconds
    return () => clearInterval(interval)
  }, [])

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount)
  }

  const formatNumber = (num: number) => {
    return new Intl.NumberFormat('en-US').format(num)
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-gray-900"></div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Enterprise Dashboard</h1>
          <p className="text-muted-foreground">
            Monitor your YouTube automation platform performance
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <Badge variant={systemHealth.database ? "default" : "destructive"}>
            {systemHealth.database ? "System Online" : "System Offline"}
          </Badge>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Views</CardTitle>
            <Eye className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{formatNumber(analyticsData.totalViews)}</div>
            <p className="text-xs text-muted-foreground">
              <TrendingUp className="inline h-3 w-3 mr-1" />
              +12% from last month
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Revenue</CardTitle>
            <DollarSign className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{formatCurrency(analyticsData.totalRevenue)}</div>
            <p className="text-xs text-muted-foreground">
              <ArrowUpRight className="inline h-3 w-3 mr-1" />
              +8% from last month
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active A/B Tests</CardTitle>
            <Target className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{analyticsData.activeTests}</div>
            <p className="text-xs text-muted-foreground">
              {analyticsData.activeTests > 0 ? "Tests running" : "No active tests"}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Conversion Rate</CardTitle>
            <MousePointer className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{analyticsData.conversionRate.toFixed(1)}%</div>
            <p className="text-xs text-muted-foreground">
              <CheckCircle className="inline h-3 w-3 mr-1" />
              Above average
            </p>
          </CardContent>
        </Card>
      </div>

      {/* System Health */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <Shield className="h-5 w-5 mr-2" />
            System Health
          </CardTitle>
          <CardDescription>
            Real-time status of all enterprise components
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
            {Object.entries(systemHealth).map(([service, status]) => (
              <div key={service} className="flex items-center space-x-2">
                <div className={`w-2 h-2 rounded-full ${status ? 'bg-green-500' : 'bg-red-500'}`} />
                <span className="text-sm capitalize">{service.replace('_', ' ')}</span>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Detailed Analytics */}
      <Tabs defaultValue="overview" className="space-y-4">
        <TabsList>
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="analytics">Analytics</TabsTrigger>
          <TabsTrigger value="monetization">Monetization</TabsTrigger>
          <TabsTrigger value="testing">A/B Testing</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            <Card>
              <CardHeader>
                <CardTitle>Recent Activity</CardTitle>
                <CardDescription>Latest events from your platform</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {analyticsData.recentActivity.slice(0, 5).map((activity, index) => (
                    <div key={index} className="flex items-center space-x-2 text-sm">
                      <Clock className="h-3 w-3 text-muted-foreground" />
                      <span>{activity.event_type || 'System Activity'}</span>
                      <Badge variant="outline" className="text-xs">
                        {new Date(activity.timestamp || Date.now()).toLocaleTimeString()}
                      </Badge>
                    </div>
                  ))}
                  {analyticsData.recentActivity.length === 0 && (
                    <p className="text-muted-foreground text-sm">No recent activity</p>
                  )}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Quick Actions</CardTitle>
                <CardDescription>Common platform tasks</CardDescription>
              </CardHeader>
              <CardContent className="space-y-2">
                <Button className="w-full justify-start" variant="outline">
                  <PlayCircle className="h-4 w-4 mr-2" />
                  Generate New Video
                </Button>
                <Button className="w-full justify-start" variant="outline">
                  <BarChart3 className="h-4 w-4 mr-2" />
                  Create A/B Test
                </Button>
                <Button className="w-full justify-start" variant="outline">
                  <Settings className="h-4 w-4 mr-2" />
                  Platform Settings
                </Button>
                <Button className="w-full justify-start" variant="outline">
                  <Users className="h-4 w-4 mr-2" />
                  Manage Team
                </Button>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="analytics" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Analytics Overview</CardTitle>
              <CardDescription>Detailed performance metrics</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="text-center">
                    <div className="text-2xl font-bold">{formatNumber(analyticsData.totalViews)}</div>
                    <div className="text-sm text-muted-foreground">Total Events Tracked</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold">95.2%</div>
                    <div className="text-sm text-muted-foreground">System Uptime</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold">847ms</div>
                    <div className="text-sm text-muted-foreground">Avg Response Time</div>
                  </div>
                </div>
                <div className="h-64 flex items-center justify-center border rounded-lg">
                  <p className="text-muted-foreground">Analytics Chart Placeholder</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="monetization" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Monetization Tracking</CardTitle>
              <CardDescription>Revenue and earnings overview</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <div className="text-lg font-semibold">Total Revenue</div>
                    <div className="text-3xl font-bold text-green-600">{formatCurrency(analyticsData.totalRevenue)}</div>
                  </div>
                  <div>
                    <div className="text-lg font-semibold">Growth Rate</div>
                    <div className="text-3xl font-bold text-blue-600">+12.5%</div>
                  </div>
                </div>
                <div className="h-64 flex items-center justify-center border rounded-lg">
                  <p className="text-muted-foreground">Revenue Chart Placeholder</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="testing" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>A/B Testing Overview</CardTitle>
              <CardDescription>Active experiments and results</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="text-center">
                    <div className="text-2xl font-bold">{analyticsData.activeTests}</div>
                    <div className="text-sm text-muted-foreground">Active Tests</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold">23</div>
                    <div className="text-sm text-muted-foreground">Completed Tests</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold">78%</div>
                    <div className="text-sm text-muted-foreground">Success Rate</div>
                  </div>
                </div>
                {analyticsData.activeTests === 0 && (
                  <div className="text-center py-8">
                    <Target className="h-12 w-12 text-muted-foreground mx-auto mb-2" />
                    <p className="text-muted-foreground">No active A/B tests</p>
                    <Button className="mt-2">Create New Test</Button>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}

// Named export for compatibility
export { EnterpriseMainDashboard }