"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import Link from 'next/link'
import { 
  BarChart3, 
  Video, 
  Globe, 
  Target, 
  Users, 
  DollarSign,
  PlayCircle,
  Settings,
  TrendingUp,
  Zap
} from 'lucide-react'

export default function EnhancedDashboard() {
  return (
    <div className="space-y-6 p-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">YouTube Automation Platform</h1>
          <p className="text-muted-foreground">
            Enterprise-grade automation for content creators
          </p>
        </div>
        <Badge variant="default" className="bg-gradient-to-r from-blue-500 to-purple-600">
          <Zap className="h-3 w-3 mr-1" />
          Enterprise
        </Badge>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Videos</CardTitle>
            <Video className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">1,247</div>
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
            <div className="text-2xl font-bold">$12,547</div>
            <p className="text-xs text-muted-foreground">
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
            <div className="text-2xl font-bold">7</div>
            <p className="text-xs text-muted-foreground">
              3 completed this week
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Team Members</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">12</div>
            <p className="text-xs text-muted-foreground">
              +2 new this month
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Action Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <BarChart3 className="h-5 w-5 mr-2" />
              Analytics Dashboard
            </CardTitle>
            <CardDescription>
              View detailed performance metrics and insights
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Link href="/dashboard">
              <Button className="w-full">
                View Analytics
              </Button>
            </Link>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <Target className="h-5 w-5 mr-2" />
              A/B Testing
            </CardTitle>
            <CardDescription>
              Create and manage experiments to optimize performance
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Link href="/ab-testing">
              <Button className="w-full">
                Manage Tests
              </Button>
            </Link>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <DollarSign className="h-5 w-5 mr-2" />
              Monetization
            </CardTitle>
            <CardDescription>
              Track revenue and optimize monetization strategies
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Link href="/monetization">
              <Button className="w-full">
                View Revenue
              </Button>
            </Link>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <PlayCircle className="h-5 w-5 mr-2" />
              Video Generator
            </CardTitle>
            <CardDescription>
              AI-powered video creation and automation
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Link href="/videos">
              <Button className="w-full">
                Generate Video
              </Button>
            </Link>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <Globe className="h-5 w-5 mr-2" />
              Publisher
            </CardTitle>
            <CardDescription>
              Multi-platform publishing and distribution
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Link href="/publisher">
              <Button className="w-full">
                Publish Content
              </Button>
            </Link>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <Users className="h-5 w-5 mr-2" />
              Team Management
            </CardTitle>
            <CardDescription>
              Manage team members and permissions
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Link href="/team">
              <Button className="w-full">
                Manage Team
              </Button>
            </Link>
          </CardContent>
        </Card>
      </div>

      {/* System Status */}
      <Card>
        <CardHeader>
          <CardTitle>System Status</CardTitle>
          <CardDescription>Real-time platform health monitoring</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-green-500 rounded-full"></div>
              <span className="text-sm">All Systems Operational</span>
            </div>
            <Badge variant="outline">99.9% Uptime</Badge>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}