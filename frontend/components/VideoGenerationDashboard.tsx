"use client"

import React, { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { 
  Video, 
  Play, 
  Upload, 
  Download, 
  Clock, 
  CheckCircle, 
  AlertCircle,
  RefreshCw,
  Zap,
  Youtube,
  Globe
} from 'lucide-react'

interface VideoGenerationRequest {
  prompt: string
  duration: number
  aspect_ratio: string
  voice: string
  style: string
  include_captions: boolean
  music: string
}

interface VideoStatus {
  id: string
  status: string
  progress: number
  created_at: string
  download_url?: string
  thumbnail_url?: string
}

export default function VideoGenerationDashboard() {
  const [request, setRequest] = useState<VideoGenerationRequest>({
    prompt: '',
    duration: 60,
    aspect_ratio: '16:9',
    voice: 'natural',
    style: 'engaging',
    include_captions: true,
    music: 'upbeat'
  })
  
  const [videoQueue, setVideoQueue] = useState<VideoStatus[]>([])
  const [isGenerating, setIsGenerating] = useState(false)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    fetchVideoQueue()
    const interval = setInterval(fetchVideoQueue, 5000) // Poll every 5 seconds
    return () => clearInterval(interval)
  }, [])

  const fetchVideoQueue = async () => {
    try {
      const response = await fetch('/api/v1/video/queue')
      if (response.ok) {
        const data = await response.json()
        setVideoQueue(data.videos || [])
      }
    } catch (error) {
      console.error('Failed to fetch video queue:', error)
    }
  }

  const generateVideo = async () => {
    if (!request.prompt.trim()) {
      alert('Please enter a video prompt')
      return
    }

    setIsGenerating(true)
    setLoading(true)

    try {
      const response = await fetch('/api/v1/video/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ...request,
          user_id: 'current_user' // Replace with actual user ID
        }),
      })

      if (response.ok) {
        const result = await response.json()
        console.log('Video generation started:', result)
        
        // Clear form and refresh queue
        setRequest({
          ...request,
          prompt: ''
        })
        
        fetchVideoQueue()
      } else {
        const error = await response.json()
        alert(`Error: ${error.detail || 'Failed to generate video'}`)
      }
    } catch (error) {
      console.error('Error generating video:', error)
      alert('Failed to connect to video generation service')
    } finally {
      setIsGenerating(false)
      setLoading(false)
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="h-4 w-4 text-green-500" />
      case 'processing':
      case 'generating_scenes':
      case 'adding_voice':
      case 'adding_music':
        return <RefreshCw className="h-4 w-4 text-blue-500 animate-spin" />
      case 'failed':
        return <AlertCircle className="h-4 w-4 text-red-500" />
      default:
        return <Clock className="h-4 w-4 text-gray-500" />
    }
  }

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'completed':
        return <Badge className="bg-green-500">Completed</Badge>
      case 'processing':
        return <Badge className="bg-blue-500">Processing</Badge>
      case 'generating_scenes':
        return <Badge className="bg-blue-500">Generating Scenes</Badge>
      case 'adding_voice':
        return <Badge className="bg-blue-500">Adding Voice</Badge>
      case 'adding_music':
        return <Badge className="bg-blue-500">Adding Music</Badge>
      case 'failed':
        return <Badge variant="destructive">Failed</Badge>
      default:
        return <Badge variant="outline">Unknown</Badge>
    }
  }

  return (
    <div className="space-y-6 p-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight flex items-center">
            <Video className="h-8 w-8 mr-3" />
            AI Video Generation
          </h1>
          <p className="text-muted-foreground">
            Create engaging videos from text prompts using advanced AI
          </p>
        </div>
        <Badge variant="default" className="bg-gradient-to-r from-purple-500 to-pink-600">
          <Zap className="h-3 w-3 mr-1" />
          AI-Powered
        </Badge>
      </div>

      <Tabs defaultValue="generate" className="space-y-4">
        <TabsList>
          <TabsTrigger value="generate">Generate Video</TabsTrigger>
          <TabsTrigger value="queue">Video Queue ({videoQueue.length})</TabsTrigger>
        </TabsList>

        <TabsContent value="generate" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Create New Video</CardTitle>
              <CardDescription>
                Describe what you want your video to be about and our AI will create it for you
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <label className="text-sm font-medium">Video Prompt *</label>
                <Textarea
                  placeholder="Describe your video idea... (e.g., 'Create a tutorial about healthy cooking with quick 5-minute recipes')"
                  value={request.prompt}
                  onChange={(e) => setRequest({...request, prompt: e.target.value})}
                  rows={3}
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="space-y-2">
                  <label className="text-sm font-medium">Duration (seconds)</label>
                  <Input
                    type="number"
                    min="15"
                    max="600"
                    value={request.duration}
                    onChange={(e) => setRequest({...request, duration: parseInt(e.target.value)})}
                  />
                </div>

                <div className="space-y-2">
                  <label className="text-sm font-medium">Aspect Ratio</label>
                  <select 
                    className="w-full p-2 border rounded-md"
                    value={request.aspect_ratio}
                    onChange={(e) => setRequest({...request, aspect_ratio: e.target.value})}
                  >
                    <option value="16:9">16:9 (YouTube)</option>
                    <option value="9:16">9:16 (Shorts/TikTok)</option>
                    <option value="1:1">1:1 (Square)</option>
                  </select>
                </div>

                <div className="space-y-2">
                  <label className="text-sm font-medium">Voice Style</label>
                  <select 
                    className="w-full p-2 border rounded-md"
                    value={request.voice}
                    onChange={(e) => setRequest({...request, voice: e.target.value})}
                  >
                    <option value="natural">Natural</option>
                    <option value="professional">Professional</option>
                    <option value="energetic">Energetic</option>
                    <option value="calm">Calm</option>
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <label className="text-sm font-medium">Video Style</label>
                  <select 
                    className="w-full p-2 border rounded-md"
                    value={request.style}
                    onChange={(e) => setRequest({...request, style: e.target.value})}
                  >
                    <option value="engaging">Engaging</option>
                    <option value="educational">Educational</option>
                    <option value="entertainment">Entertainment</option>
                    <option value="professional">Professional</option>
                  </select>
                </div>

                <div className="space-y-2">
                  <label className="text-sm font-medium">Background Music</label>
                  <select 
                    className="w-full p-2 border rounded-md"
                    value={request.music}
                    onChange={(e) => setRequest({...request, music: e.target.value})}
                  >
                    <option value="upbeat">Upbeat</option>
                    <option value="calm">Calm</option>
                    <option value="cinematic">Cinematic</option>
                    <option value="none">No Music</option>
                  </select>
                </div>
              </div>

              <div className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  id="captions"
                  checked={request.include_captions}
                  onChange={(e) => setRequest({...request, include_captions: e.target.checked})}
                />
                <label htmlFor="captions" className="text-sm font-medium">
                  Include automatic captions
                </label>
              </div>

              <Button 
                onClick={generateVideo}
                disabled={isGenerating || !request.prompt.trim()}
                className="w-full"
                size="lg"
              >
                {isGenerating ? (
                  <>
                    <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                    Generating Video...
                  </>
                ) : (
                  <>
                    <Play className="h-4 w-4 mr-2" />
                    Generate Video
                  </>
                )}
              </Button>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="queue" className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold">Video Generation Queue</h2>
            <Button variant="outline" onClick={fetchVideoQueue}>
              <RefreshCw className="h-4 w-4 mr-2" />
              Refresh
            </Button>
          </div>

          {videoQueue.length === 0 ? (
            <Card>
              <CardContent className="flex flex-col items-center justify-center py-8">
                <Video className="h-12 w-12 text-muted-foreground mb-4" />
                <p className="text-muted-foreground text-center">
                  No videos in queue. Create your first video to get started!
                </p>
              </CardContent>
            </Card>
          ) : (
            <div className="space-y-4">
              {videoQueue.map((video) => (
                <Card key={video.id}>
                  <CardContent className="p-4">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-3">
                        {getStatusIcon(video.status)}
                        <div>
                          <p className="font-medium">Video {video.id.slice(0, 8)}</p>
                          <p className="text-sm text-muted-foreground">
                            Created: {new Date(video.created_at).toLocaleString()}
                          </p>
                        </div>
                      </div>

                      <div className="flex items-center space-x-4">
                        {getStatusBadge(video.status)}
                        
                        {video.status !== 'completed' && video.status !== 'failed' && (
                          <div className="flex items-center space-x-2">
                            <div className="w-20 bg-gray-200 rounded-full h-2">
                              <div 
                                className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                                style={{ width: `${video.progress}%` }}
                              ></div>
                            </div>
                            <span className="text-sm text-muted-foreground">{video.progress}%</span>
                          </div>
                        )}

                        {video.status === 'completed' && (
                          <div className="flex space-x-2">
                            {video.download_url && (
                              <Button variant="outline" size="sm" asChild>
                                <a href={video.download_url} target="_blank" rel="noopener noreferrer">
                                  <Download className="h-4 w-4 mr-1" />
                                  Download
                                </a>
                              </Button>
                            )}
                            <Button variant="outline" size="sm">
                              <Upload className="h-4 w-4 mr-1" />
                              Publish
                            </Button>
                          </div>
                        )}
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </TabsContent>
      </Tabs>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <Video className="h-5 w-5 text-blue-500" />
              <div>
                <p className="text-sm font-medium">Total Videos</p>
                <p className="text-2xl font-bold">{videoQueue.length}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <CheckCircle className="h-5 w-5 text-green-500" />
              <div>
                <p className="text-sm font-medium">Completed</p>
                <p className="text-2xl font-bold">
                  {videoQueue.filter(v => v.status === 'completed').length}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <RefreshCw className="h-5 w-5 text-blue-500" />
              <div>
                <p className="text-sm font-medium">Processing</p>
                <p className="text-2xl font-bold">
                  {videoQueue.filter(v => v.status !== 'completed' && v.status !== 'failed').length}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}