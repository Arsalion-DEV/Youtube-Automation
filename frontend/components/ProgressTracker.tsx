'use client'

import React, { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  CheckCircle, Clock, AlertCircle, TrendingUp, Target, Users,
  Zap, Calendar, BarChart3, Globe, Settings, Trophy, Star,
  ArrowRight, RefreshCw, PlayCircle, Video, MessageCircle
} from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Progress } from '@/components/ui/progress'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'

interface ProgressItem {
  id: string
  title: string
  description: string
  category: 'setup' | 'content' | 'growth' | 'automation'
  status: 'not_started' | 'in_progress' | 'completed' | 'blocked'
  progress: number
  priority: 'low' | 'medium' | 'high'
  estimatedTime: string
  reward?: {
    type: 'badge' | 'feature' | 'bonus'
    name: string
    description: string
  }
  action?: () => void
  dependencies?: string[]
  lastUpdated?: Date
}

interface ProgressStats {
  totalTasks: number
  completedTasks: number
  inProgressTasks: number
  overallProgress: number
  categoryProgress: Record<string, number>
  streakDays: number
  pointsEarned: number
}

interface ProgressTrackerProps {
  userId?: string
  onTaskComplete?: (taskId: string) => void
}

const PROGRESS_ITEMS: ProgressItem[] = [
  // Setup Category
  {
    id: 'channel-setup',
    title: 'Complete Channel Setup',
    description: 'Set up your YouTube channel with AI wizard',
    category: 'setup',
    status: 'not_started',
    progress: 0,
    priority: 'high',
    estimatedTime: '10 minutes',
    reward: {
      type: 'badge',
      name: 'Channel Creator',
      description: 'Completed initial channel setup'
    },
    action: () => window.location.href = '/wizard'
  },
  {
    id: 'platform-connections',
    title: 'Connect Social Platforms',
    description: 'Link your social media accounts for cross-platform publishing',
    category: 'setup',
    status: 'not_started',
    progress: 0,
    priority: 'high',
    estimatedTime: '15 minutes',
    dependencies: ['channel-setup'],
    action: () => window.location.href = '/publisher'
  },
  {
    id: 'profile-optimization',
    title: 'Optimize Your Profile',
    description: 'Complete your channel branding and description',
    category: 'setup',
    status: 'not_started',
    progress: 0,
    priority: 'medium',
    estimatedTime: '20 minutes',
    dependencies: ['channel-setup']
  },

  // Content Category
  {
    id: 'first-video',
    title: 'Create Your First Video',
    description: 'Use AI tools to generate your first video content',
    category: 'content',
    status: 'not_started',
    progress: 0,
    priority: 'high',
    estimatedTime: '30 minutes',
    reward: {
      type: 'feature',
      name: 'Advanced Analytics',
      description: 'Unlock detailed performance insights'
    },
    dependencies: ['channel-setup']
  },
  {
    id: 'content-calendar',
    title: 'Set Up Content Calendar',
    description: 'Plan your content schedule for the next month',
    category: 'content',
    status: 'not_started',
    progress: 0,
    priority: 'medium',
    estimatedTime: '25 minutes',
    action: () => window.location.href = '/scheduler'
  },
  {
    id: 'batch-content',
    title: 'Create Batch Content',
    description: 'Generate multiple videos for efficient publishing',
    category: 'content',
    status: 'not_started',
    progress: 0,
    priority: 'medium',
    estimatedTime: '45 minutes',
    dependencies: ['first-video']
  },

  // Growth Category
  {
    id: 'seo-optimization',
    title: 'SEO Optimization',
    description: 'Optimize your videos for search discovery',
    category: 'growth',
    status: 'not_started',
    progress: 0,
    priority: 'high',
    estimatedTime: '15 minutes',
    dependencies: ['first-video']
  },
  {
    id: 'audience-research',
    title: 'Audience Research',
    description: 'Analyze your target audience and competitors',
    category: 'growth',
    status: 'not_started',
    progress: 0,
    priority: 'medium',
    estimatedTime: '20 minutes'
  },
  {
    id: 'engagement-strategy',
    title: 'Engagement Strategy',
    description: 'Set up automated responses and community management',
    category: 'growth',
    status: 'not_started',
    progress: 0,
    priority: 'medium',
    estimatedTime: '30 minutes',
    dependencies: ['audience-research']
  },

  // Automation Category
  {
    id: 'posting-automation',
    title: 'Automated Posting',
    description: 'Set up automated publishing schedules',
    category: 'automation',
    status: 'not_started',
    progress: 0,
    priority: 'medium',
    estimatedTime: '10 minutes',
    dependencies: ['content-calendar', 'platform-connections']
  },
  {
    id: 'analytics-tracking',
    title: 'Analytics Automation',
    description: 'Configure automated performance tracking and reports',
    category: 'automation',
    status: 'not_started',
    progress: 0,
    priority: 'low',
    estimatedTime: '15 minutes',
    dependencies: ['first-video']
  },
  {
    id: 'workflow-optimization',
    title: 'Workflow Optimization',
    description: 'Fine-tune your automated content creation workflow',
    category: 'automation',
    status: 'not_started',
    progress: 0,
    priority: 'low',
    estimatedTime: '25 minutes',
    dependencies: ['posting-automation', 'batch-content']
  }
]

export default function ProgressTracker({ userId, onTaskComplete }: ProgressTrackerProps) {
  const [progressItems, setProgressItems] = useState<ProgressItem[]>(PROGRESS_ITEMS)
  const [stats, setStats] = useState<ProgressStats>({
    totalTasks: PROGRESS_ITEMS.length,
    completedTasks: 0,
    inProgressTasks: 0,
    overallProgress: 0,
    categoryProgress: {},
    streakDays: 0,
    pointsEarned: 0
  })
  const [selectedCategory, setSelectedCategory] = useState<string>('all')
  const [isLoading, setIsLoading] = useState(false)

  // Load progress from localStorage or API
  useEffect(() => {
    loadProgressData()
  }, [userId])

  // Calculate stats whenever progress items change
  useEffect(() => {
    calculateStats()
  }, [progressItems])

  const loadProgressData = async () => {
    try {
      setIsLoading(true)
      
      // Try to load from API if userId is provided
      if (userId) {
        const token = localStorage.getItem('authToken')
        const response = await fetch(`/api/user/progress/${userId}`, {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        })
        
        if (response.ok) {
          const data = await response.json()
          if (data.success && data.data?.progress) {
            setProgressItems(data.data.progress)
            return
          }
        }
      }
      
      // Fallback to localStorage
      const savedProgress = localStorage.getItem('user_progress')
      if (savedProgress) {
        const parsed = JSON.parse(savedProgress)
        setProgressItems(parsed)
      }
    } catch (error) {
      console.error('Failed to load progress:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const saveProgressData = async (updatedItems: ProgressItem[]) => {
    try {
      // Save to localStorage
      localStorage.setItem('user_progress', JSON.stringify(updatedItems))
      
      // Save to API if userId is provided
      if (userId) {
        const token = localStorage.getItem('authToken')
        await fetch(`/api/user/progress/${userId}`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          },
          body: JSON.stringify({ progress: updatedItems })
        })
      }
    } catch (error) {
      console.error('Failed to save progress:', error)
    }
  }

  const calculateStats = () => {
    const completed = progressItems.filter(item => item.status === 'completed')
    const inProgress = progressItems.filter(item => item.status === 'in_progress')
    
    const categoryProgress: Record<string, number> = {}
    const categories = ['setup', 'content', 'growth', 'automation']
    
    categories.forEach(category => {
      const categoryItems = progressItems.filter(item => item.category === category)
      const categoryCompleted = categoryItems.filter(item => item.status === 'completed')
      categoryProgress[category] = categoryItems.length > 0 
        ? (categoryCompleted.length / categoryItems.length) * 100 
        : 0
    })
    
    const overallProgress = (completed.length / progressItems.length) * 100
    const pointsEarned = completed.length * 10 + inProgress.length * 5
    
    setStats({
      totalTasks: progressItems.length,
      completedTasks: completed.length,
      inProgressTasks: inProgress.length,
      overallProgress,
      categoryProgress,
      streakDays: getStreakDays(),
      pointsEarned
    })
  }

  const getStreakDays = (): number => {
    // Calculate streak based on completion dates
    const completed = progressItems
      .filter(item => item.status === 'completed' && item.lastUpdated)
      .sort((a, b) => (b.lastUpdated?.getTime() || 0) - (a.lastUpdated?.getTime() || 0))
    
    if (completed.length === 0) return 0
    
    let streak = 0
    let currentDate = new Date()
    currentDate.setHours(0, 0, 0, 0)
    
    for (const item of completed) {
      const itemDate = new Date(item.lastUpdated!)
      itemDate.setHours(0, 0, 0, 0)
      
      const diffDays = Math.floor((currentDate.getTime() - itemDate.getTime()) / (1000 * 60 * 60 * 24))
      
      if (diffDays === streak) {
        streak++
      } else {
        break
      }
    }
    
    return streak
  }

  const updateTaskStatus = async (taskId: string, status: ProgressItem['status'], progress?: number) => {
    const updatedItems = progressItems.map(item => {
      if (item.id === taskId) {
        const updatedItem = {
          ...item,
          status,
          progress: progress !== undefined ? progress : (status === 'completed' ? 100 : item.progress),
          lastUpdated: new Date()
        }
        return updatedItem
      }
      return item
    })
    
    setProgressItems(updatedItems)
    await saveProgressData(updatedItems)
    
    if (status === 'completed' && onTaskComplete) {
      onTaskComplete(taskId)
    }
  }

  const startTask = (taskId: string) => {
    updateTaskStatus(taskId, 'in_progress', 10)
  }

  const completeTask = (taskId: string) => {
    updateTaskStatus(taskId, 'completed', 100)
  }

  const executeTaskAction = (task: ProgressItem) => {
    if (task.action) {
      task.action()
    }
    if (task.status === 'not_started') {
      startTask(task.id)
    }
  }

  const getStatusIcon = (status: ProgressItem['status']) => {
    switch (status) {
      case 'completed': return <CheckCircle className="h-5 w-5 text-green-500" />
      case 'in_progress': return <RefreshCw className="h-5 w-5 text-blue-500 animate-spin" />
      case 'blocked': return <AlertCircle className="h-5 w-5 text-red-500" />
      default: return <Clock className="h-5 w-5 text-gray-400" />
    }
  }

  const getCategoryIcon = (category: string) => {
    const icons = {
      setup: <Settings className="h-5 w-5" />,
      content: <Video className="h-5 w-5" />,
      growth: <TrendingUp className="h-5 w-5" />,
      automation: <Zap className="h-5 w-5" />
    }
    return icons[category as keyof typeof icons] || <Target className="h-5 w-5" />
  }

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high': return 'border-red-200 bg-red-50'
      case 'medium': return 'border-yellow-200 bg-yellow-50'
      default: return 'border-gray-200 bg-gray-50'
    }
  }

  const isTaskBlocked = (task: ProgressItem) => {
    if (!task.dependencies) return false
    return task.dependencies.some(depId => {
      const depTask = progressItems.find(item => item.id === depId)
      return depTask?.status !== 'completed'
    })
  }

  const filteredItems = selectedCategory === 'all' 
    ? progressItems 
    : progressItems.filter(item => item.category === selectedCategory)

  const availableTasks = filteredItems.filter(task => 
    task.status === 'not_started' && !isTaskBlocked(task)
  )

  if (isLoading) {
    return (
      <div className="flex items-center justify-center p-8">
        <RefreshCw className="h-8 w-8 animate-spin text-blue-500" />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Progress Overview */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center space-x-2">
                <Trophy className="h-6 w-6 text-yellow-500" />
                <span>Your Progress</span>
              </CardTitle>
              <CardDescription>Track your journey to YouTube success</CardDescription>
            </div>
            <div className="text-right">
              <div className="text-2xl font-bold">{Math.round(stats.overallProgress)}%</div>
              <div className="text-sm text-muted-foreground">Complete</div>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {/* Overall progress */}
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium">Overall Progress</span>
                <span className="text-sm text-muted-foreground">
                  {stats.completedTasks} of {stats.totalTasks} tasks
                </span>
              </div>
              <Progress value={stats.overallProgress} className="h-3" />
            </div>

            {/* Category progress */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {Object.entries(stats.categoryProgress).map(([category, progress]) => (
                <div key={category} className="text-center">
                  <div className="flex items-center justify-center mb-2">
                    {getCategoryIcon(category)}
                  </div>
                  <div className="text-sm font-medium capitalize">{category}</div>
                  <div className="text-lg font-bold">{Math.round(progress)}%</div>
                </div>
              ))}
            </div>

            {/* Stats */}
            <div className="flex items-center justify-between pt-4 border-t">
              <div className="flex items-center space-x-6 text-sm">
                <div className="flex items-center space-x-2">
                  <Star className="h-4 w-4 text-yellow-500" />
                  <span>{stats.pointsEarned} points</span>
                </div>
                <div className="flex items-center space-x-2">
                  <TrendingUp className="h-4 w-4 text-green-500" />
                  <span>{stats.streakDays} day streak</span>
                </div>
              </div>
              <Badge variant="secondary">
                {stats.inProgressTasks} in progress
              </Badge>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Task List */}
      <Tabs value={selectedCategory} onValueChange={setSelectedCategory}>
        <TabsList className="grid grid-cols-5 w-full">
          <TabsTrigger value="all">All Tasks</TabsTrigger>
          <TabsTrigger value="setup">Setup</TabsTrigger>
          <TabsTrigger value="content">Content</TabsTrigger>
          <TabsTrigger value="growth">Growth</TabsTrigger>
          <TabsTrigger value="automation">Automation</TabsTrigger>
        </TabsList>

        <TabsContent value={selectedCategory} className="space-y-4">
          {/* Quick Actions */}
          {availableTasks.length > 0 && (
            <Card className="border-blue-200 bg-blue-50">
              <CardHeader>
                <CardTitle className="text-lg flex items-center space-x-2">
                  <PlayCircle className="h-5 w-5 text-blue-600" />
                  <span>Recommended Next Steps</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {availableTasks.slice(0, 4).map((task) => (
                    <Button
                      key={task.id}
                      variant="outline"
                      className="justify-start h-auto p-3"
                      onClick={() => executeTaskAction(task)}
                    >
                      <div className="flex items-center space-x-3 text-left">
                        {getCategoryIcon(task.category)}
                        <div>
                          <div className="font-medium">{task.title}</div>
                          <div className="text-xs text-muted-foreground">{task.estimatedTime}</div>
                        </div>
                      </div>
                    </Button>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Task Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {filteredItems.map((task) => {
              const blocked = isTaskBlocked(task)
              
              return (
                <motion.div
                  key={task.id}
                  layout
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.2 }}
                >
                  <Card className={`transition-all duration-200 hover:shadow-md ${
                    task.status === 'completed' ? 'border-green-200 bg-green-50' :
                    blocked ? 'border-gray-200 bg-gray-50 opacity-60' :
                    getPriorityColor(task.priority)
                  }`}>
                    <CardContent className="p-4">
                      <div className="flex items-start justify-between mb-3">
                        <div className="flex items-start space-x-3">
                          {getStatusIcon(task.status)}
                          <div>
                            <h3 className="font-medium">{task.title}</h3>
                            <p className="text-sm text-muted-foreground mt-1">
                              {task.description}
                            </p>
                          </div>
                        </div>
                        <div className="flex items-center space-x-2">
                          <Badge variant="outline" className="text-xs">
                            {task.estimatedTime}
                          </Badge>
                          {task.priority === 'high' && (
                            <Badge variant="destructive" className="text-xs">High</Badge>
                          )}
                        </div>
                      </div>

                      {task.status === 'in_progress' && (
                        <div className="mb-3">
                          <Progress value={task.progress} className="h-2" />
                        </div>
                      )}

                      {task.reward && task.status === 'not_started' && (
                        <div className="mb-3 p-2 bg-yellow-50 border border-yellow-200 rounded-lg">
                          <div className="flex items-center space-x-2 text-xs text-yellow-800">
                            <Trophy className="h-3 w-3" />
                            <span>Reward: {task.reward.name}</span>
                          </div>
                        </div>
                      )}

                      {blocked && (
                        <div className="mb-3 p-2 bg-gray-50 border border-gray-200 rounded-lg">
                          <div className="flex items-center space-x-2 text-xs text-gray-600">
                            <AlertCircle className="h-3 w-3" />
                            <span>Complete dependencies first</span>
                          </div>
                        </div>
                      )}

                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-2">
                          {getCategoryIcon(task.category)}
                          <span className="text-xs text-muted-foreground capitalize">
                            {task.category}
                          </span>
                        </div>
                        
                        {task.status === 'not_started' && !blocked && (
                          <Button
                            size="sm"
                            onClick={() => executeTaskAction(task)}
                          >
                            Start
                            <ArrowRight className="h-3 w-3 ml-1" />
                          </Button>
                        )}
                        
                        {task.status === 'in_progress' && (
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => completeTask(task.id)}
                          >
                            Complete
                          </Button>
                        )}
                        
                        {task.status === 'completed' && (
                          <Badge variant="secondary">
                            <CheckCircle className="h-3 w-3 mr-1" />
                            Done
                          </Badge>
                        )}
                      </div>
                    </CardContent>
                  </Card>
                </motion.div>
              )
            })}
          </div>
        </TabsContent>
      </Tabs>
    </div>
  )
}