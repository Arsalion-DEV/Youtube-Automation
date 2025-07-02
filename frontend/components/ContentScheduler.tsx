'use client'

import React, { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  Calendar, Clock, Plus, Filter, Search, ChevronLeft, ChevronRight,
  Video, Globe, Youtube, Facebook, Twitter, Instagram, Linkedin,
  TrendingUp, Target, Zap, Settings, BarChart3, Eye, AlertCircle,
  CheckCircle, Edit, Trash2, Copy, Star
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Switch } from '@/components/ui/switch'

interface ScheduledPost {
  id: string
  title: string
  description: string
  platforms: string[]
  scheduledTime: Date
  status: 'scheduled' | 'published' | 'failed' | 'pending'
  engagementScore: number
  videoPath?: string
  thumbnailUrl?: string
  tags: string[]
  author: string
}

interface OptimalTime {
  platform: string
  time: string
  score: number
  audience: string
  reason: string
}

interface CalendarDay {
  date: Date
  isCurrentMonth: boolean
  posts: ScheduledPost[]
  optimalTimes: OptimalTime[]
}

export function ContentScheduler() {
  const [currentDate, setCurrentDate] = useState(new Date())
  const [viewMode, setViewMode] = useState<'month' | 'week' | 'day'>('month')
  const [selectedDate, setSelectedDate] = useState<Date | null>(null)
  const [scheduledPosts, setScheduledPosts] = useState<ScheduledPost[]>([])
  const [showOptimalTimes, setShowOptimalTimes] = useState(true)
  const [filterPlatform, setFilterPlatform] = useState<string>('all')
  const [searchQuery, setSearchQuery] = useState('')
  const [showAddModal, setShowAddModal] = useState(false)

  useEffect(() => {
    loadScheduledContent()
  }, [currentDate])

  const loadScheduledContent = async () => {
    // Mock data - in production, fetch from API
    const mockPosts: ScheduledPost[] = [
      {
        id: '1',
        title: 'Ultimate React Tutorial 2024',
        description: 'Complete guide to React hooks and state management',
        platforms: ['youtube', 'twitter', 'linkedin'],
        scheduledTime: new Date(2025, 5, 30, 14, 0), // June 30, 2025 2:00 PM
        status: 'scheduled',
        engagementScore: 1.4,
        tags: ['react', 'tutorial', 'javascript'],
        author: 'Tech Channel'
      },
      {
        id: '2',
        title: 'Quick Tips: CSS Grid Layout',
        description: 'Master CSS Grid in 5 minutes',
        platforms: ['youtube', 'instagram', 'tiktok'],
        scheduledTime: new Date(2025, 5, 30, 19, 0), // June 30, 2025 7:00 PM
        status: 'scheduled',
        engagementScore: 1.2,
        tags: ['css', 'webdev', 'tutorial'],
        author: 'Design Hub'
      },
      {
        id: '3',
        title: 'Behind the Scenes: Studio Setup',
        description: 'How I built my YouTube studio on a budget',
        platforms: ['youtube', 'facebook', 'instagram'],
        scheduledTime: new Date(2025, 6, 1, 12, 0), // July 1, 2025 12:00 PM
        status: 'scheduled',
        engagementScore: 1.3,
        tags: ['studio', 'setup', 'youtube'],
        author: 'Creator Tips'
      }
    ]
    
    setScheduledPosts(mockPosts)
  }

  const getDaysInMonth = (date: Date): CalendarDay[] => {
    const year = date.getFullYear()
    const month = date.getMonth()
    const firstDay = new Date(year, month, 1)
    const lastDay = new Date(year, month + 1, 0)
    const daysInMonth = lastDay.getDate()
    const startingDayOfWeek = firstDay.getDay()

    const days: CalendarDay[] = []

    // Add previous month's trailing days
    for (let i = startingDayOfWeek - 1; i >= 0; i--) {
      const date = new Date(year, month, -i)
      days.push({
        date,
        isCurrentMonth: false,
        posts: [],
        optimalTimes: []
      })
    }

    // Add current month's days
    for (let day = 1; day <= daysInMonth; day++) {
      const date = new Date(year, month, day)
      const postsForDay = scheduledPosts.filter(post => 
        post.scheduledTime.toDateString() === date.toDateString()
      )
      
      days.push({
        date,
        isCurrentMonth: true,
        posts: postsForDay,
        optimalTimes: getOptimalTimesForDate(date)
      })
    }

    // Add next month's leading days to fill the grid
    const remainingDays = 42 - days.length // 6 weeks * 7 days
    for (let day = 1; day <= remainingDays; day++) {
      const date = new Date(year, month + 1, day)
      days.push({
        date,
        isCurrentMonth: false,
        posts: [],
        optimalTimes: []
      })
    }

    return days
  }

  const getOptimalTimesForDate = (date: Date): OptimalTime[] => {
    // Mock optimal times based on research
    const weekday = date.getDay()
    const isWeekend = weekday === 0 || weekday === 6

    if (isWeekend) {
      return [
        { platform: 'youtube', time: '10:00', score: 1.2, audience: '18-34', reason: 'Weekend leisure viewing' },
        { platform: 'instagram', time: '11:00', score: 1.4, audience: '18-34', reason: 'Peak weekend engagement' },
        { platform: 'facebook', time: '14:00', score: 1.1, audience: '25-54', reason: 'Afternoon social check-in' }
      ]
    } else {
      return [
        { platform: 'linkedin', time: '08:00', score: 1.3, audience: '25-54', reason: 'Morning professional browsing' },
        { platform: 'twitter', time: '12:00', score: 1.4, audience: '18-49', reason: 'Lunch break engagement' },
        { platform: 'youtube', time: '15:00', score: 1.3, audience: '18-34', reason: 'Afternoon content consumption' },
        { platform: 'instagram', time: '17:00', score: 1.4, audience: '18-34', reason: 'After-work browsing' },
        { platform: 'facebook', time: '19:00', score: 1.2, audience: '25-54', reason: 'Evening social time' }
      ]
    }
  }

  const getPlatformIcon = (platform: string) => {
    switch (platform) {
      case 'youtube': return <Youtube className="w-3 h-3" />
      case 'facebook': return <Facebook className="w-3 h-3" />
      case 'twitter': return <Twitter className="w-3 h-3" />
      case 'instagram': return <Instagram className="w-3 h-3" />
      case 'linkedin': return <Linkedin className="w-3 h-3" />
      default: return <Globe className="w-3 h-3" />
    }
  }

  const getPlatformColor = (platform: string) => {
    switch (platform) {
      case 'youtube': return 'red'
      case 'facebook': return 'blue'
      case 'twitter': return 'sky'
      case 'instagram': return 'pink'
      case 'linkedin': return 'indigo'
      default: return 'gray'
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'scheduled': return 'blue'
      case 'published': return 'green'
      case 'failed': return 'red'
      case 'pending': return 'yellow'
      default: return 'gray'
    }
  }

  const navigateMonth = (direction: 'prev' | 'next') => {
    setCurrentDate(prev => {
      const newDate = new Date(prev)
      if (direction === 'prev') {
        newDate.setMonth(prev.getMonth() - 1)
      } else {
        newDate.setMonth(prev.getMonth() + 1)
      }
      return newDate
    })
  }

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  }

  const filteredPosts = scheduledPosts.filter(post => {
    const matchesPlatform = filterPlatform === 'all' || post.platforms.includes(filterPlatform)
    const matchesSearch = searchQuery === '' || 
      post.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      post.description.toLowerCase().includes(searchQuery.toLowerCase())
    
    return matchesPlatform && matchesSearch
  })

  const days = getDaysInMonth(currentDate)

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            Content Scheduler
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">
            Plan and schedule your content across all platforms
          </p>
        </div>
        <div className="flex gap-3">
          <Button variant="outline" onClick={() => setShowOptimalTimes(!showOptimalTimes)}>
            <TrendingUp className="w-4 h-4 mr-2" />
            {showOptimalTimes ? 'Hide' : 'Show'} Optimal Times
          </Button>
          <Button onClick={() => setShowAddModal(true)} className="bg-gradient-to-r from-blue-600 to-indigo-600">
            <Plus className="w-4 h-4 mr-2" />
            Schedule Content
          </Button>
        </div>
      </div>

      <Tabs value={viewMode} onValueChange={(value) => setViewMode(value as 'month' | 'week' | 'day')}>
        <div className="flex items-center justify-between">
          <TabsList>
            <TabsTrigger value="month">Month</TabsTrigger>
            <TabsTrigger value="week">Week</TabsTrigger>
            <TabsTrigger value="day">Day</TabsTrigger>
          </TabsList>

          {/* Filters */}
          <div className="flex items-center gap-4">
            <div className="relative">
              <Search className="w-4 h-4 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
              <Input
                placeholder="Search content..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10 w-64"
              />
            </div>
            <Select value={filterPlatform} onValueChange={setFilterPlatform}>
              <SelectTrigger className="w-40">
                <SelectValue placeholder="All Platforms" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Platforms</SelectItem>
                <SelectItem value="youtube">YouTube</SelectItem>
                <SelectItem value="facebook">Facebook</SelectItem>
                <SelectItem value="twitter">Twitter</SelectItem>
                <SelectItem value="instagram">Instagram</SelectItem>
                <SelectItem value="linkedin">LinkedIn</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>

        {/* Month View */}
        <TabsContent value="month" className="space-y-6">
          {/* Calendar Navigation */}
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="flex items-center gap-2">
                  <Calendar className="w-5 h-5" />
                  {currentDate.toLocaleDateString('en-US', { month: 'long', year: 'numeric' })}
                </CardTitle>
                <div className="flex items-center gap-2">
                  <Button variant="outline" size="sm" onClick={() => navigateMonth('prev')}>
                    <ChevronLeft className="w-4 h-4" />
                  </Button>
                  <Button variant="outline" size="sm" onClick={() => setCurrentDate(new Date())}>
                    Today
                  </Button>
                  <Button variant="outline" size="sm" onClick={() => navigateMonth('next')}>
                    <ChevronRight className="w-4 h-4" />
                  </Button>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              {/* Calendar Grid */}
              <div className="grid grid-cols-7 gap-1 mb-4">
                {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map(day => (
                  <div key={day} className="p-2 text-center text-sm font-medium text-gray-500">
                    {day}
                  </div>
                ))}
              </div>
              
              <div className="grid grid-cols-7 gap-1">
                {days.map((day, index) => (
                  <div
                    key={index}
                    className={`min-h-[120px] p-2 border rounded-lg cursor-pointer transition-colors ${
                      day.isCurrentMonth 
                        ? 'bg-white dark:bg-gray-800 border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700'
                        : 'bg-gray-50 dark:bg-gray-900 border-gray-100 dark:border-gray-800 text-gray-400'
                    } ${
                      day.date.toDateString() === new Date().toDateString()
                        ? 'ring-2 ring-blue-500 ring-opacity-50'
                        : ''
                    }`}
                    onClick={() => setSelectedDate(day.date)}
                  >
                    <div className="flex items-center justify-between mb-2">
                      <span className={`text-sm font-medium ${
                        day.date.toDateString() === new Date().toDateString()
                          ? 'text-blue-600 dark:text-blue-400'
                          : ''
                      }`}>
                        {day.date.getDate()}
                      </span>
                      {day.posts.length > 0 && (
                        <Badge variant="secondary" className="text-xs">
                          {day.posts.length}
                        </Badge>
                      )}
                    </div>

                    {/* Optimal Times */}
                    {showOptimalTimes && day.isCurrentMonth && day.optimalTimes.length > 0 && (
                      <div className="space-y-1 mb-2">
                        {day.optimalTimes.slice(0, 2).map((time, idx) => (
                          <div key={idx} className="flex items-center gap-1 text-xs">
                            <div className={`text-${getPlatformColor(time.platform)}-500`}>
                              {getPlatformIcon(time.platform)}
                            </div>
                            <span className="text-gray-600 dark:text-gray-400">
                              {time.time}
                            </span>
                            <div className="flex items-center">
                              {Array.from({ length: Math.floor(time.score) }, (_, i) => (
                                <Star key={i} className="w-2 h-2 fill-yellow-400 text-yellow-400" />
                              ))}
                            </div>
                          </div>
                        ))}
                      </div>
                    )}

                    {/* Scheduled Posts */}
                    <div className="space-y-1">
                      {day.posts.slice(0, 2).map(post => (
                        <div
                          key={post.id}
                          className={`p-1 rounded text-xs bg-${getStatusColor(post.status)}-100 dark:bg-${getStatusColor(post.status)}-900/20 border border-${getStatusColor(post.status)}-200 dark:border-${getStatusColor(post.status)}-700`}
                        >
                          <div className="font-medium truncate">{post.title}</div>
                          <div className="flex items-center gap-1 mt-1">
                            <span className="text-gray-500">{formatTime(post.scheduledTime)}</span>
                            <div className="flex gap-0.5">
                              {post.platforms.slice(0, 3).map(platform => (
                                <div key={platform} className={`text-${getPlatformColor(platform)}-500`}>
                                  {getPlatformIcon(platform)}
                                </div>
                              ))}
                            </div>
                          </div>
                        </div>
                      ))}
                      {day.posts.length > 2 && (
                        <div className="text-xs text-gray-500 text-center">
                          +{day.posts.length - 2} more
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Week View */}
        <TabsContent value="week">
          <Card>
            <CardContent className="p-6">
              <div className="text-center text-gray-500">
                Week view coming soon - enhanced weekly scheduling interface
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Day View */}
        <TabsContent value="day">
          <Card>
            <CardContent className="p-6">
              <div className="text-center text-gray-500">
                Day view coming soon - detailed daily schedule management
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Upcoming Posts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Clock className="w-5 h-5 text-blue-500" />
              Upcoming Posts
            </CardTitle>
            <CardDescription>
              Your next scheduled content
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {filteredPosts
                .filter(post => post.scheduledTime > new Date())
                .sort((a, b) => a.scheduledTime.getTime() - b.scheduledTime.getTime())
                .slice(0, 5)
                .map(post => (
                  <div key={post.id} className="flex items-center justify-between p-3 border rounded-lg">
                    <div className="flex-1">
                      <h3 className="font-medium text-gray-900 dark:text-white">
                        {post.title}
                      </h3>
                      <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                        {post.scheduledTime.toLocaleDateString()} at {formatTime(post.scheduledTime)}
                      </p>
                      <div className="flex items-center gap-2 mt-2">
                        <div className="flex gap-1">
                          {post.platforms.map(platform => (
                            <div key={platform} className={`text-${getPlatformColor(platform)}-500`}>
                              {getPlatformIcon(platform)}
                            </div>
                          ))}
                        </div>
                        <Badge variant="outline" className={`text-${getStatusColor(post.status)}-600`}>
                          {post.status}
                        </Badge>
                        <div className="flex items-center gap-1">
                          <TrendingUp className="w-3 h-3 text-green-500" />
                          <span className="text-xs text-green-600">{post.engagementScore}x</span>
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <Button variant="ghost" size="sm">
                        <Edit className="w-4 h-4" />
                      </Button>
                      <Button variant="ghost" size="sm">
                        <Copy className="w-4 h-4" />
                      </Button>
                      <Button variant="ghost" size="sm" className="text-red-600">
                        <Trash2 className="w-4 h-4" />
                      </Button>
                    </div>
                  </div>
                ))}
            </div>
          </CardContent>
        </Card>

        {/* Optimal Timing Insights */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Target className="w-5 h-5 text-purple-500" />
              Optimal Timing Insights
            </CardTitle>
            <CardDescription>
              AI-powered recommendations for maximum engagement
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {getOptimalTimesForDate(new Date()).map((time, index) => (
                <div key={index} className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
                  <div className="flex items-center gap-3">
                    <div className={`text-${getPlatformColor(time.platform)}-500`}>
                      {getPlatformIcon(time.platform)}
                    </div>
                    <div>
                      <p className="font-medium capitalize">{time.platform}</p>
                      <p className="text-sm text-gray-600 dark:text-gray-400">{time.reason}</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="font-medium">{time.time}</p>
                    <div className="flex items-center gap-1">
                      {Array.from({ length: Math.floor(time.score) }, (_, i) => (
                        <Star key={i} className="w-3 h-3 fill-yellow-400 text-yellow-400" />
                      ))}
                      <span className="text-sm text-gray-500 ml-1">
                        {time.score}x
                      </span>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            <div className="mt-6 p-4 bg-purple-50 dark:bg-purple-900/20 rounded-lg">
              <h4 className="font-medium text-purple-900 dark:text-purple-100 mb-2">
                💡 Pro Tip
              </h4>
              <p className="text-sm text-purple-700 dark:text-purple-300">
                Schedule your most important content during optimal times for up to 40% higher engagement rates.
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}