"use client"

import React, { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Progress } from "@/components/ui/progress"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Sheet, SheetContent, SheetTrigger } from "@/components/ui/sheet"
import { useTheme } from 'next-themes'
import { 
  Video, 
  Wand2, 
  Share2, 
  BarChart3, 
  Target, 
  DollarSign,
  Users,
  Globe,
  PlayCircle,
  TrendingUp,
  CheckCircle,
  Clock,
  Zap,
  Youtube,
  Settings,
  Building2,
  AlertCircle,
  Activity,
  Calendar,
  Download,
  Menu,
  Home,
  FileVideo,
  Sparkles,
  Network,
  MessageSquare,
  Database,
  Shield,
  MonitorSpeaker,
  Palette,
  Bot,
  Workflow,
  Rocket,
  Star,
  Crown,
  Gem,
  Plus,
  Sun,
  Moon
} from 'lucide-react'

interface DashboardStats {
  totalVideos: number
  completedVideos: number
  successRate: number
  queueLength: number
  processingTime: number
}

interface Video {
  id: number
  title: string
  status: string
  created_at: string
  updated_at: string
  result_url?: string
}

interface SystemMetrics {
  cpu_usage: number
  memory_usage: { percent: number }
  disk_usage: { percent: number }
}

// Enhanced sidebar configuration with beautiful icons and colors
const sidebarItems = [
  {
    title: "🏠 Dashboard",
    icon: Home,
    href: "/",
    description: "Overview and analytics",
    gradient: "from-blue-500 to-purple-600",
    isActive: true
  },
  {
    title: "🎬 Video Generation",
    icon: Video,
    href: "/videos",
    description: "VEO3 AI video creation",
    gradient: "from-red-500 to-pink-600",
    badge: "VEO3"
  },
  {
    title: "🪄 AI Wizard",
    icon: Wand2,
    href: "/wizard",
    description: "Channel setup assistant",
    gradient: "from-purple-500 to-indigo-600",
    badge: "AI"
  },
  {
    title: "🚀 Publisher",
    icon: Share2,
    href: "/publisher",
    description: "Multi-platform publishing",
    gradient: "from-green-500 to-teal-600"
  },
  {
    title: "📊 Analytics",
    icon: BarChart3,
    href: "/analytics",
    description: "Performance insights",
    gradient: "from-yellow-500 to-orange-600"
  },
  {
    title: "💰 Monetization",
    icon: DollarSign,
    href: "/monetization",
    description: "Revenue tracking",
    gradient: "from-emerald-500 to-green-600",
    badge: "Pro"
  },
  {
    title: "🎯 A/B Testing",
    icon: Target,
    href: "/ab-testing",
    description: "Optimize performance",
    gradient: "from-cyan-500 to-blue-600"
  },
  {
    title: "👥 Team Management",
    icon: Users,
    href: "/team",
    description: "Collaborate efficiently",
    gradient: "from-violet-500 to-purple-600"
  },
  {
    title: "🌐 Multi-Platform",
    icon: Globe,
    href: "/multi-platform",
    description: "Cross-platform sync",
    gradient: "from-pink-500 to-rose-600"
  },
  {
    title: "📅 Scheduler",
    icon: Calendar,
    href: "/scheduler",
    description: "Content calendar",
    gradient: "from-indigo-500 to-blue-600"
  },
  {
    title: "⚙️ Settings",
    icon: Settings,
    href: "/settings",
    description: "Platform configuration",
    gradient: "from-gray-500 to-slate-600"
  }
]

export default function Dashboard() {
  const [mounted, setMounted] = useState(false)
  const [activeItem, setActiveItem] = useState('/')
  const [stats, setStats] = useState<DashboardStats | null>(null)
  const [videos, setVideos] = useState<Video[]>([])
  const [metrics, setMetrics] = useState<SystemMetrics | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const { theme, setTheme } = useTheme()
  const router = useRouter()

  useEffect(() => {
    setMounted(true)
    fetchData()
    const interval = setInterval(fetchData, 30000)
    return () => clearInterval(interval)
  }, [])

  const fetchData = async () => {
    try {
      const [videosRes, analyticsRes, queueRes] = await Promise.all([
        fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/videos/list?limit=10`),
        fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v2/analytics`),
        fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/video/queue`)
      ])

      const [videosData, analyticsData, queueData] = await Promise.all([
        videosRes.json(),
        analyticsRes.json(),
        queueRes.json()
      ])

      setVideos(videosData.videos || [])
      setStats({
        totalVideos: analyticsData.video_count || 0,
        completedVideos: analyticsData.completed || 0,
        successRate: analyticsData.success_rate || 0,
        queueLength: queueData.queue_length || 0,
        processingTime: queueData.estimated_wait_time || 0
      })
    } catch (error) {
      console.error('Error fetching data:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const handleSidebarClick = (href: string) => {
    setActiveItem(href)
    if (href !== '/') {
      router.push(href)
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed': return <CheckCircle className="h-4 w-4 text-green-500" />
      case 'generating': 
      case 'processing': return <Clock className="h-4 w-4 text-yellow-500 animate-spin" />
      case 'failed': return <AlertCircle className="h-4 w-4 text-red-500" />
      default: return <Clock className="h-4 w-4 text-gray-500" />
    }
  }

  const getStatusBadge = (status: string) => {
    const colors = {
      completed: "bg-green-500/20 text-green-400 border-green-500/30",
      generating: "bg-yellow-500/20 text-yellow-400 border-yellow-500/30 animate-pulse",
      processing: "bg-blue-500/20 text-blue-400 border-blue-500/30 animate-pulse",
      failed: "bg-red-500/20 text-red-400 border-red-500/30",
      draft: "bg-gray-500/20 text-gray-400 border-gray-500/30"
    }
    return colors[status as keyof typeof colors] || colors.draft
  }

  const SidebarContent = () => (
    <div className="flex flex-col h-full p-4 space-y-4">
      {/* Logo and branding */}
      <div className="flex items-center space-x-3 p-4 rounded-xl bg-gradient-to-r from-purple-600 to-blue-600 text-white">
        <div className="p-2 bg-white/20 rounded-lg">
          <Crown className="h-6 w-6" />
        </div>
        <div>
          <h2 className="text-lg font-bold tracking-tight">
            VEO-3 Platform
          </h2>
          <p className="text-xs opacity-90">
            World's Best YouTube Automation
          </p>
        </div>
      </div>

      {/* Quick stats */}
      <div className="grid grid-cols-2 gap-3">
        <div className="p-3 rounded-lg bg-gradient-to-br from-green-500/10 to-emerald-500/10 border border-green-500/20">
          <div className="flex items-center space-x-2">
            <CheckCircle className="h-4 w-4 text-green-500" />
            <span className="text-xs text-green-400">Success</span>
          </div>
          <p className="text-lg font-bold text-green-400">{stats?.successRate?.toFixed(1) || 0}%</p>
        </div>
        <div className="p-3 rounded-lg bg-gradient-to-br from-blue-500/10 to-purple-500/10 border border-blue-500/20">
          <div className="flex items-center space-x-2">
            <Activity className="h-4 w-4 text-blue-500" />
            <span className="text-xs text-blue-400">Queue</span>
          </div>
          <p className="text-lg font-bold text-blue-400">{stats?.queueLength || 0}</p>
        </div>
      </div>

      {/* Navigation items */}
      <ScrollArea className="flex-1 custom-scrollbar">
        <div className="space-y-2">
          {sidebarItems.map((item) => (
            <div key={item.href} className="sidebar-item">
              <Button
                variant={activeItem === item.href ? "secondary" : "ghost"}
                className={cn(
                  "w-full justify-start p-3 h-auto text-left transition-all duration-200",
                  activeItem === item.href 
                    ? "bg-gradient-to-r " + item.gradient + " text-white shadow-lg scale-105" 
                    : "hover:bg-white/5 hover:scale-105"
                )}
                onClick={() => handleSidebarClick(item.href)}
              >
                <div className="flex items-center space-x-3 w-full">
                  <div className={cn(
                    "p-2 rounded-lg transition-all",
                    activeItem === item.href 
                      ? "bg-white/20" 
                      : "bg-gradient-to-br " + item.gradient + " bg-opacity-20"
                  )}>
                    <item.icon className="h-4 w-4" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium truncate">{item.title}</p>
                    <p className="text-xs opacity-70 truncate">{item.description}</p>
                  </div>
                  {item.badge && (
                    <Badge className="text-xs px-2 py-1 bg-white/20 text-white border-white/30">
                      {item.badge}
                    </Badge>
                  )}
                </div>
              </Button>
            </div>
          ))}
        </div>
      </ScrollArea>

      {/* Theme toggle and upgrade */}
      <div className="space-y-2">
        <Button
          variant="outline"
          size="sm"
          onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
          className="w-full flex items-center space-x-2 glass-effect border-white/20"
        >
          {theme === 'dark' ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
          <span>Toggle Theme</span>
        </Button>
        
        <div className="p-4 rounded-xl bg-gradient-to-r from-amber-500 to-orange-600 text-white">
          <div className="flex items-center space-x-2 mb-2">
            <Gem className="h-5 w-5" />
            <span className="font-semibold">Enterprise</span>
          </div>
          <p className="text-xs opacity-90 mb-3">Unlock advanced features and unlimited generation</p>
          <Button size="sm" className="w-full bg-white/20 hover:bg-white/30 text-white border-white/30">
            <Crown className="h-4 w-4 mr-2" />
            Upgrade Now
          </Button>
        </div>
      </div>
    </div>
  )

  if (!mounted) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin h-8 w-8 border-2 border-purple-500 border-t-transparent rounded-full mx-auto mb-4"></div>
          <p className="text-white">Loading VEO-3 Platform...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      {/* Desktop sidebar */}
      <div className="hidden lg:flex lg:w-80 lg:flex-col lg:fixed lg:inset-y-0 z-50">
        <div className="flex-1 flex flex-col min-h-0 bg-black/20 backdrop-blur-xl border-r border-white/10">
          <SidebarContent />
        </div>
      </div>

      {/* Mobile header */}
      <div className="lg:hidden">
        <div className="flex items-center justify-between p-4 bg-black/20 backdrop-blur-xl border-b border-white/10">
          <div className="flex items-center space-x-3">
            <Sheet>
              <SheetTrigger asChild>
                <Button variant="ghost" size="icon" className="text-white">
                  <Menu className="h-6 w-6" />
                </Button>
              </SheetTrigger>
              <SheetContent side="left" className="w-80 p-0 bg-black/80 backdrop-blur-xl border-white/10">
                <SidebarContent />
              </SheetContent>
            </Sheet>
            <div>
              <h1 className="text-lg font-bold text-white">VEO-3 Platform</h1>
              <p className="text-xs text-white/70">YouTube Automation</p>
            </div>
          </div>
          <Button
            variant="ghost"
            size="icon"
            onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
            className="text-white"
          >
            {theme === 'dark' ? <Sun className="h-5 w-5" /> : <Moon className="h-5 w-5" />}
          </Button>
        </div>
      </div>

      {/* Main content */}
      <div className="lg:pl-80">
        <main className="p-6 lg:p-8">
          {/* Header */}
          <div className="mb-8">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h1 className="text-3xl font-bold text-white mb-2">
                  Welcome to <span className="text-gradient">VEO-3 Platform</span> 🚀
                </h1>
                <p className="text-white/70">
                  World's most advanced YouTube automation platform with enterprise features
                </p>
              </div>
              <div className="flex items-center space-x-3">
                <Badge className="bg-green-500/20 text-green-400 border-green-500/30 px-3 py-1">
                  <div className="w-2 h-2 bg-green-500 rounded-full mr-2 animate-pulse"></div>
                  System Online
                </Badge>
                <Button className="bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-white btn-glow">
                  <Plus className="h-4 w-4 mr-2" />
                  Generate Video
                </Button>
              </div>
            </div>
          </div>

          {/* Stats grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <Card className="modern-card card-hover">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium text-white/90">Total Videos</CardTitle>
                <Video className="h-4 w-4 text-purple-400" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-white mb-1">{stats?.totalVideos || 0}</div>
                <p className="text-xs text-white/60">
                  +{stats?.completedVideos || 0} completed today
                </p>
                <div className="mt-2 h-1 bg-white/10 rounded-full overflow-hidden">
                  <div 
                    className="h-full bg-gradient-to-r from-purple-500 to-blue-500 progress-gradient"
                    style={{ width: `${Math.min((stats?.successRate || 0), 100)}%` }}
                  />
                </div>
              </CardContent>
            </Card>

            <Card className="modern-card card-hover">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium text-white/90">Success Rate</CardTitle>
                <TrendingUp className="h-4 w-4 text-green-400" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-white mb-1">{stats?.successRate?.toFixed(1) || 0}%</div>
                <p className="text-xs text-green-400">
                  +12.5% from last week
                </p>
                <div className="mt-2 h-1 bg-white/10 rounded-full overflow-hidden">
                  <div 
                    className="h-full bg-gradient-to-r from-green-500 to-emerald-500"
                    style={{ width: `${stats?.successRate || 0}%` }}
                  />
                </div>
              </CardContent>
            </Card>

            <Card className="modern-card card-hover">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium text-white/90">Queue Length</CardTitle>
                <Clock className="h-4 w-4 text-yellow-400" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-white mb-1">{stats?.queueLength || 0}</div>
                <p className="text-xs text-white/60">
                  ~2 seconds avg processing
                </p>
                <div className="mt-2 h-1 bg-white/10 rounded-full overflow-hidden">
                  <div 
                    className="h-full bg-gradient-to-r from-yellow-500 to-orange-500"
                    style={{ width: `${Math.min((stats?.queueLength || 0) * 10, 100)}%` }}
                  />
                </div>
              </CardContent>
            </Card>

            <Card className="modern-card card-hover">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium text-white/90">Revenue</CardTitle>
                <DollarSign className="h-4 w-4 text-emerald-400" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-white mb-1">2,450</div>
                <p className="text-xs text-emerald-400">
                  +23.1% this month
                </p>
                <div className="mt-2 h-1 bg-white/10 rounded-full overflow-hidden">
                  <div className="h-full bg-gradient-to-r from-emerald-500 to-green-500 w-3/4" />
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Recent videos */}
          <Card className="modern-card">
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="text-white flex items-center space-x-2">
                    <PlayCircle className="h-5 w-5 text-purple-400" />
                    <span>Recent Videos</span>
                  </CardTitle>
                  <CardDescription className="text-white/60">
                    Latest video generation results
                  </CardDescription>
                </div>
                <Button variant="outline" size="sm" className="border-white/20 text-white hover:bg-white/10">
                  <Download className="h-4 w-4 mr-2" />
                  Export All
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              <ScrollArea className="h-80 custom-scrollbar">
                <div className="space-y-3">
                  {videos.length === 0 ? (
                    <div className="text-center py-8">
                      <Video className="h-12 w-12 text-white/30 mx-auto mb-4" />
                      <p className="text-white/60">No videos yet. Create your first video!</p>
                      <Button className="mt-4 bg-gradient-to-r from-purple-600 to-blue-600 text-white">
                        <Plus className="h-4 w-4 mr-2" />
                        Generate Video
                      </Button>
                    </div>
                  ) : (
                    videos.map((video) => (
                      <div
                        key={video.id}
                        className="flex items-center justify-between p-4 rounded-lg bg-white/5 hover:bg-white/10 transition-colors border border-white/10"
                      >
                        <div className="flex items-center space-x-4">
                          {getStatusIcon(video.status)}
                          <div className="min-w-0 flex-1">
                            <p className="text-sm font-medium text-white truncate">
                              {video.title}
                            </p>
                            <p className="text-xs text-white/60">
                              {new Date(video.created_at).toLocaleDateString()}
                            </p>
                          </div>
                        </div>
                        <div className="flex items-center space-x-3">
                          <Badge className={getStatusBadge(video.status)}>
                            {video.status}
                          </Badge>
                          {video.result_url && (
                            <Button size="sm" variant="ghost" className="text-purple-400 hover:text-purple-300">
                              <Download className="h-4 w-4" />
                            </Button>
                          )}
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </ScrollArea>
            </CardContent>
          </Card>
        </main>
      </div>
    </div>
  )
}
