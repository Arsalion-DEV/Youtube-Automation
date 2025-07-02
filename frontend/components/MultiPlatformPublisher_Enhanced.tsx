'use client'

import React, { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  Upload, Calendar, Settings, BarChart3, Clock, CheckCircle, X, AlertCircle,
  Facebook, Twitter, Instagram, Linkedin, Video, Globe, Play, RefreshCw,
  Zap, Target, Users, Eye, Heart, MessageCircle, Share, TrendingUp
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Switch } from '@/components/ui/switch'
import { toast } from '@/components/ui/use-toast'

interface Platform {
  id: string
  name: string
  icon: React.ReactNode
  connected: boolean
  color: string
  oauthUrl: string
  videoSpecs: {
    maxSizeMb: number
    maxDurationSeconds: number
    formats: string[]
    aspectRatios: string[]
  }
}

interface PublishingJob {
  id: string
  title: string
  platforms: string[]
  status: 'pending' | 'processing' | 'publishing' | 'completed' | 'failed'
  platformResults: Record<string, any>
  createdAt: string
  completedAt?: string
  progress: number
}

interface ApiResponse<T = any> {
  success: boolean
  data?: T
  error?: string
  message?: string
}

export default function MultiPlatformPublisher() {
  const [platforms, setPlatforms] = useState<Platform[]>([])
  const [connectedPlatforms, setConnectedPlatforms] = useState<string[]>([])
  const [selectedPlatforms, setSelectedPlatforms] = useState<string[]>([])
  const [publishingJobs, setPublishingJobs] = useState<PublishingJob[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [isConnecting, setIsConnecting] = useState<Record<string, boolean>>({})
  
  // Form state
  const [title, setTitle] = useState('')
  const [description, setDescription] = useState('')
  const [tags, setTags] = useState('')
  const [videoFile, setVideoFile] = useState<File | null>(null)
  const [scheduledTime, setScheduledTime] = useState<Date | null>(null)

  // Load available platforms on component mount
  useEffect(() => {
    loadAvailablePlatforms()
    loadConnectedPlatforms()
    loadPublishingJobs()
  }, [])

  // Poll for job updates
  useEffect(() => {
    const interval = setInterval(() => {
      loadPublishingJobs()
    }, 5000) // Update every 5 seconds

    return () => clearInterval(interval)
  }, [])

  const loadAvailablePlatforms = async () => {
    try {
      const response = await fetch('/api/social/platforms/available')
      const data: ApiResponse = await response.json()
      
      if (data.success && data.data?.platforms) {
        const formattedPlatforms: Platform[] = data.data.platforms.map((p: any) => ({
          id: p.id,
          name: p.name,
          icon: getPlatformIcon(p.id),
          connected: false,
          color: getPlatformColor(p.id),
          oauthUrl: p.oauth_url,
          videoSpecs: p.video_specs
        }))
        setPlatforms(formattedPlatforms)
      }
    } catch (error) {
      console.error('Failed to load platforms:', error)
      toast({
        title: 'Error',
        description: 'Failed to load available platforms',
        variant: 'destructive'
      })
    }
  }

  const loadConnectedPlatforms = async () => {
    try {
      const token = localStorage.getItem('authToken')
      const response = await fetch('/api/social/platforms/connected', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      const data: ApiResponse = await response.json()
      
      if (data.success && data.data?.platforms) {
        const connected = data.data.platforms
          .filter((p: any) => p.connected)
          .map((p: any) => p.platform)
        setConnectedPlatforms(connected)
      }
    } catch (error) {
      console.error('Failed to load connected platforms:', error)
    }
  }

  const loadPublishingJobs = async () => {
    try {
      const token = localStorage.getItem('authToken')
      const response = await fetch('/api/social/publishing/jobs', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      const data: ApiResponse = await response.json()
      
      if (data.success && data.data?.jobs) {
        setPublishingJobs(data.data.jobs)
      }
    } catch (error) {
      console.error('Failed to load publishing jobs:', error)
    }
  }

  const connectPlatform = async (platformId: string, oauthUrl: string) => {
    setIsConnecting(prev => ({ ...prev, [platformId]: true }))
    
    try {
      // Open OAuth popup
      const popup = window.open(
        oauthUrl,
        `oauth_${platformId}`,
        'width=500,height=600,scrollbars=yes,resizable=yes'
      )

      // Listen for OAuth completion
      const checkClosed = setInterval(() => {
        if (popup?.closed) {
          clearInterval(checkClosed)
          setIsConnecting(prev => ({ ...prev, [platformId]: false }))
          // Reload connected platforms
          loadConnectedPlatforms()
        }
      }, 1000)

    } catch (error) {
      console.error(`Failed to connect ${platformId}:`, error)
      setIsConnecting(prev => ({ ...prev, [platformId]: false }))
      toast({
        title: 'Connection Failed',
        description: `Failed to connect to ${platformId}`,
        variant: 'destructive'
      })
    }
  }

  const publishContent = async () => {
    if (!videoFile || selectedPlatforms.length === 0 || !title.trim()) {
      toast({
        title: 'Missing Information',
        description: 'Please provide a video, title, and select at least one platform',
        variant: 'destructive'
      })
      return
    }

    setIsLoading(true)

    try {
      const formData = new FormData()
      formData.append('video', videoFile)
      formData.append('title', title)
      formData.append('description', description)
      formData.append('platforms', JSON.stringify(selectedPlatforms))
      formData.append('tags', JSON.stringify(tags.split(',').map(t => t.trim()).filter(t => t)))
      
      if (scheduledTime) {
        formData.append('scheduled_time', scheduledTime.toISOString())
      }

      const token = localStorage.getItem('authToken')
      const response = await fetch('/api/social/publish', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        },
        body: formData
      })

      const data: ApiResponse = await response.json()

      if (data.success) {
        toast({
          title: 'Publishing Started',
          description: 'Your content is being published to selected platforms',
        })
        
        // Reset form
        setTitle('')
        setDescription('')
        setTags('')
        setVideoFile(null)
        setSelectedPlatforms([])
        
        // Reload jobs
        loadPublishingJobs()
      } else {
        throw new Error(data.error || 'Publishing failed')
      }
    } catch (error) {
      console.error('Publishing error:', error)
      toast({
        title: 'Publishing Failed',
        description: error instanceof Error ? error.message : 'An unexpected error occurred',
        variant: 'destructive'
      })
    } finally {
      setIsLoading(false)
    }
  }

  const retryFailedJob = async (jobId: string) => {
    try {
      const token = localStorage.getItem('authToken')
      const response = await fetch(`/api/social/publishing/retry/${jobId}`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })

      const data: ApiResponse = await response.json()

      if (data.success) {
        toast({
          title: 'Retry Started',
          description: 'Publishing job has been restarted',
        })
        loadPublishingJobs()
      }
    } catch (error) {
      console.error('Retry failed:', error)
      toast({
        title: 'Retry Failed',
        description: 'Failed to retry publishing job',
        variant: 'destructive'
      })
    }
  }

  const getPlatformIcon = (platformId: string) => {
    const icons = {
      facebook: <Facebook className="h-5 w-5" />,
      twitter: <Twitter className="h-5 w-5" />,
      instagram: <Instagram className="h-5 w-5" />,
      linkedin: <Linkedin className="h-5 w-5" />,
      tiktok: <Video className="h-5 w-5" />,
    }
    return icons[platformId as keyof typeof icons] || <Globe className="h-5 w-5" />
  }

  const getPlatformColor = (platformId: string) => {
    const colors = {
      facebook: 'bg-blue-500',
      twitter: 'bg-sky-500',
      instagram: 'bg-pink-500',
      linkedin: 'bg-blue-700',
      tiktok: 'bg-black',
    }
    return colors[platformId as keyof typeof colors] || 'bg-gray-500'
  }

  const getJobStatusIcon = (status: string) => {
    switch (status) {
      case 'completed': return <CheckCircle className="h-4 w-4 text-green-500" />
      case 'failed': return <X className="h-4 w-4 text-red-500" />
      case 'publishing': case 'processing': return <RefreshCw className="h-4 w-4 text-blue-500 animate-spin" />
      default: return <Clock className="h-4 w-4 text-yellow-500" />
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Multi-Platform Publisher</h1>
          <p className="text-muted-foreground">Publish your content across all social media platforms</p>
        </div>
        <Button onClick={loadConnectedPlatforms} variant="outline" size="sm">
          <RefreshCw className="h-4 w-4 mr-2" />
          Refresh
        </Button>
      </div>

      <Tabs defaultValue="publish" className="space-y-6">
        <TabsList>
          <TabsTrigger value="publish">Publish Content</TabsTrigger>
          <TabsTrigger value="platforms">Platform Management</TabsTrigger>
          <TabsTrigger value="jobs">Publishing Jobs</TabsTrigger>
          <TabsTrigger value="analytics">Analytics</TabsTrigger>
        </TabsList>

        {/* Publish Content Tab */}
        <TabsContent value="publish" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Content Form */}
            <Card>
              <CardHeader>
                <CardTitle>Content Details</CardTitle>
                <CardDescription>Enter your content information</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <label className="text-sm font-medium">Video File</label>
                  <div className="mt-2">
                    <input
                      type="file"
                      accept="video/*"
                      onChange={(e) => setVideoFile(e.target.files?.[0] || null)}
                      className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
                    />
                  </div>
                </div>

                <div>
                  <label className="text-sm font-medium">Title</label>
                  <Input
                    value={title}
                    onChange={(e) => setTitle(e.target.value)}
                    placeholder="Enter video title..."
                    className="mt-2"
                  />
                </div>

                <div>
                  <label className="text-sm font-medium">Description</label>
                  <Textarea
                    value={description}
                    onChange={(e) => setDescription(e.target.value)}
                    placeholder="Enter video description..."
                    className="mt-2"
                    rows={4}
                  />
                </div>

                <div>
                  <label className="text-sm font-medium">Tags (comma-separated)</label>
                  <Input
                    value={tags}
                    onChange={(e) => setTags(e.target.value)}
                    placeholder="tag1, tag2, tag3..."
                    className="mt-2"
                  />
                </div>
              </CardContent>
            </Card>

            {/* Platform Selection */}
            <Card>
              <CardHeader>
                <CardTitle>Select Platforms</CardTitle>
                <CardDescription>Choose where to publish your content</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {platforms.map((platform) => {
                    const isConnected = connectedPlatforms.includes(platform.id)
                    const isSelected = selectedPlatforms.includes(platform.id)
                    const isConnectingThisPlatform = isConnecting[platform.id]

                    return (
                      <div key={platform.id} className="flex items-center justify-between p-3 border rounded-lg">
                        <div className="flex items-center space-x-3">
                          <div className={`p-2 rounded-lg ${platform.color} text-white`}>
                            {platform.icon}
                          </div>
                          <div>
                            <div className="font-medium">{platform.name}</div>
                            <div className="text-sm text-muted-foreground">
                              Max: {platform.videoSpecs.maxSizeMb}MB, {platform.videoSpecs.maxDurationSeconds}s
                            </div>
                          </div>
                        </div>
                        
                        <div className="flex items-center space-x-2">
                          {isConnected ? (
                            <>
                              <Badge variant="secondary" className="text-green-700 bg-green-100">
                                Connected
                              </Badge>
                              <Switch
                                checked={isSelected}
                                onCheckedChange={(checked) => {
                                  if (checked) {
                                    setSelectedPlatforms([...selectedPlatforms, platform.id])
                                  } else {
                                    setSelectedPlatforms(selectedPlatforms.filter(p => p !== platform.id))
                                  }
                                }}
                              />
                            </>
                          ) : (
                            <Button
                              size="sm"
                              onClick={() => connectPlatform(platform.id, platform.oauthUrl)}
                              disabled={isConnectingThisPlatform}
                            >
                              {isConnectingThisPlatform ? (
                                <RefreshCw className="h-4 w-4 animate-spin" />
                              ) : (
                                'Connect'
                              )}
                            </Button>
                          )}
                        </div>
                      </div>
                    )
                  })}
                </div>

                {selectedPlatforms.length > 0 && (
                  <div className="mt-6">
                    <Button
                      onClick={publishContent}
                      disabled={isLoading}
                      className="w-full"
                      size="lg"
                    >
                      {isLoading ? (
                        <>
                          <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                          Publishing...
                        </>
                      ) : (
                        <>
                          <Play className="h-4 w-4 mr-2" />
                          Publish to {selectedPlatforms.length} Platform{selectedPlatforms.length > 1 ? 's' : ''}
                        </>
                      )}
                    </Button>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Publishing Jobs Tab */}
        <TabsContent value="jobs" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Publishing Jobs</CardTitle>
              <CardDescription>Track your content publishing progress</CardDescription>
            </CardHeader>
            <CardContent>
              {publishingJobs.length === 0 ? (
                <div className="text-center py-8 text-muted-foreground">
                  No publishing jobs yet. Start by publishing some content!
                </div>
              ) : (
                <div className="space-y-4">
                  {publishingJobs.map((job) => (
                    <div key={job.id} className="border rounded-lg p-4">
                      <div className="flex items-center justify-between mb-3">
                        <div className="flex items-center space-x-3">
                          {getJobStatusIcon(job.status)}
                          <div>
                            <div className="font-medium">{job.title}</div>
                            <div className="text-sm text-muted-foreground">
                              {new Date(job.createdAt).toLocaleString()}
                            </div>
                          </div>
                        </div>
                        <div className="flex items-center space-x-2">
                          <Badge variant={job.status === 'completed' ? 'default' : 
                                        job.status === 'failed' ? 'destructive' : 'secondary'}>
                            {job.status}
                          </Badge>
                          {job.status === 'failed' && (
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => retryFailedJob(job.id)}
                            >
                              Retry
                            </Button>
                          )}
                        </div>
                      </div>
                      
                      {job.status === 'processing' || job.status === 'publishing' ? (
                        <Progress value={job.progress} className="mb-3" />
                      ) : null}
                      
                      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-2">
                        {job.platforms.map((platformId) => {
                          const result = job.platformResults[platformId] || {}
                          return (
                            <div key={platformId} className="flex items-center space-x-2 text-sm">
                              {getPlatformIcon(platformId)}
                              <span className="capitalize">{platformId}</span>
                              {result.success ? (
                                <CheckCircle className="h-3 w-3 text-green-500" />
                              ) : result.success === false ? (
                                <X className="h-3 w-3 text-red-500" />
                              ) : (
                                <Clock className="h-3 w-3 text-yellow-500" />
                              )}
                            </div>
                          )
                        })}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Platform Management Tab */}
        <TabsContent value="platforms" className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {platforms.map((platform) => {
              const isConnected = connectedPlatforms.includes(platform.id)
              
              return (
                <Card key={platform.id}>
                  <CardHeader>
                    <div className="flex items-center space-x-3">
                      <div className={`p-2 rounded-lg ${platform.color} text-white`}>
                        {platform.icon}
                      </div>
                      <div>
                        <CardTitle className="text-lg">{platform.name}</CardTitle>
                        <CardDescription>
                          {isConnected ? 'Connected' : 'Not connected'}
                        </CardDescription>
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      <div className="text-sm">
                        <div className="font-medium">Video Specifications:</div>
                        <div className="text-muted-foreground">
                          • Max size: {platform.videoSpecs.maxSizeMb}MB<br/>
                          • Max duration: {platform.videoSpecs.maxDurationSeconds}s<br/>
                          • Formats: {platform.videoSpecs.formats.join(', ')}<br/>
                          • Aspect ratios: {platform.videoSpecs.aspectRatios.join(', ')}
                        </div>
                      </div>
                      
                      {!isConnected && (
                        <Button
                          className="w-full"
                          onClick={() => connectPlatform(platform.id, platform.oauthUrl)}
                          disabled={isConnecting[platform.id]}
                        >
                          {isConnecting[platform.id] ? 'Connecting...' : 'Connect Account'}
                        </Button>
                      )}
                    </div>
                  </CardContent>
                </Card>
              )
            })}
          </div>
        </TabsContent>

        {/* Analytics Tab */}
        <TabsContent value="analytics" className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <Card>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-muted-foreground">Total Posts</p>
                    <p className="text-2xl font-bold">{publishingJobs.length}</p>
                  </div>
                  <TrendingUp className="h-8 w-8 text-blue-500" />
                </div>
              </CardContent>
            </Card>
            
            <Card>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-muted-foreground">Successful</p>
                    <p className="text-2xl font-bold text-green-600">
                      {publishingJobs.filter(job => job.status === 'completed').length}
                    </p>
                  </div>
                  <CheckCircle className="h-8 w-8 text-green-500" />
                </div>
              </CardContent>
            </Card>
            
            <Card>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-muted-foreground">Failed</p>
                    <p className="text-2xl font-bold text-red-600">
                      {publishingJobs.filter(job => job.status === 'failed').length}
                    </p>
                  </div>
                  <AlertCircle className="h-8 w-8 text-red-500" />
                </div>
              </CardContent>
            </Card>
            
            <Card>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-muted-foreground">Platforms</p>
                    <p className="text-2xl font-bold">{connectedPlatforms.length}</p>
                  </div>
                  <Globe className="h-8 w-8 text-purple-500" />
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  )
}