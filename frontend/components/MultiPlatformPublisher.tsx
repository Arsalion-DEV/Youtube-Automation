"use client"

import React, { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { 
  Upload, 
  Youtube, 
  Music, 
  Instagram, 
  Globe, 
  Calendar,
  CheckCircle,
  AlertCircle,
  Clock,
  ExternalLink,
  Share2,
  Settings
} from 'lucide-react'

interface Platform {
  name: string
  display_name: string
  supported_formats: string[]
  max_duration: number
  features: string[]
}

interface PublishRequest {
  video_id: string
  platforms: string[]
  title: string
  description: string
  tags: string[]
  visibility: string
  scheduled_time?: string
}

interface VideoStatus {
  id: string
  status: string
  download_url?: string
  thumbnail_url?: string
}

export default function MultiPlatformPublisher() {
  const [platforms, setPlatforms] = useState<Platform[]>([])
  const [availableVideos, setAvailableVideos] = useState<VideoStatus[]>([])
  const [selectedVideo, setSelectedVideo] = useState<string>('')
  const [selectedPlatforms, setSelectedPlatforms] = useState<string[]>([])
  const [publishData, setPublishData] = useState({
    title: '',
    description: '',
    tags: '',
    visibility: 'public',
    scheduled_time: ''
  })
  const [isPublishing, setIsPublishing] = useState(false)
  const [publishHistory, setPublishHistory] = useState<any[]>([])

  useEffect(() => {
    fetchPlatforms()
    fetchAvailableVideos()
    fetchPublishHistory()
  }, [])

  const fetchPlatforms = async () => {
    try {
      const response = await fetch('/api/v1/platforms')
      if (response.ok) {
        const data = await response.json()
        setPlatforms(data.platforms || [])
      }
    } catch (error) {
      console.error('Failed to fetch platforms:', error)
    }
  }

  const fetchAvailableVideos = async () => {
    try {
      const response = await fetch('/api/v1/video/queue')
      if (response.ok) {
        const data = await response.json()
        const completedVideos = data.videos?.filter((v: VideoStatus) => v.status === 'completed') || []
        setAvailableVideos(completedVideos)
      }
    } catch (error) {
      console.error('Failed to fetch videos:', error)
    }
  }

  const fetchPublishHistory = async () => {
    // Mock publish history - in real app, this would come from API
    setPublishHistory([
      {
        id: '1',
        video_id: 'vid_123',
        title: 'How to Cook Perfect Pasta',
        platforms: ['youtube', 'tiktok'],
        published_at: new Date().toISOString(),
        status: 'success'
      }
    ])
  }

  const togglePlatform = (platformName: string) => {
    setSelectedPlatforms(prev => 
      prev.includes(platformName)
        ? prev.filter(p => p !== platformName)
        : [...prev, platformName]
    )
  }

  const publishVideo = async () => {
    if (!selectedVideo || selectedPlatforms.length === 0) {
      alert('Please select a video and at least one platform')
      return
    }

    if (!publishData.title.trim() || !publishData.description.trim()) {
      alert('Please fill in title and description')
      return
    }

    setIsPublishing(true)

    try {
      const request: PublishRequest = {
        video_id: selectedVideo,
        platforms: selectedPlatforms,
        title: publishData.title,
        description: publishData.description,
        tags: publishData.tags.split(',').map(tag => tag.trim()).filter(tag => tag),
        visibility: publishData.visibility,
        scheduled_time: publishData.scheduled_time || undefined,
        user_id: 'current_user' // Replace with actual user ID
      }

      const response = await fetch('/api/v1/publish', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
      })

      if (response.ok) {
        const result = await response.json()
        console.log('Video published:', result)
        
        // Reset form
        setSelectedVideo('')
        setSelectedPlatforms([])
        setPublishData({
          title: '',
          description: '',
          tags: '',
          visibility: 'public',
          scheduled_time: ''
        })
        
        alert('Video published successfully!')
        fetchPublishHistory()
      } else {
        const error = await response.json()
        alert(`Error: ${error.detail || 'Failed to publish video'}`)
      }
    } catch (error) {
      console.error('Error publishing video:', error)
      alert('Failed to connect to publishing service')
    } finally {
      setIsPublishing(false)
    }
  }

  const getPlatformIcon = (platformName: string) => {
    switch (platformName) {
      case 'youtube':
        return <Youtube className="h-5 w-5 text-red-500" />
      case 'tiktok':
        return <Music className="h-5 w-5 text-black" />
      case 'instagram':
        return <Instagram className="h-5 w-5 text-pink-500" />
      default:
        return <Globe className="h-5 w-5 text-gray-500" />
    }
  }

  const formatDuration = (seconds: number) => {
    const hours = Math.floor(seconds / 3600)
    const minutes = Math.floor((seconds % 3600) / 60)
    
    if (hours > 0) {
      return `${hours}h ${minutes}m`
    }
    return `${minutes}m`
  }

  return (
    <div className="space-y-6 p-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight flex items-center">
            <Share2 className="h-8 w-8 mr-3" />
            Multi-Platform Publisher
          </h1>
          <p className="text-muted-foreground">
            Publish your videos to multiple platforms simultaneously
          </p>
        </div>
        <Badge variant="default" className="bg-gradient-to-r from-blue-500 to-green-600">
          <Globe className="h-3 w-3 mr-1" />
          Multi-Platform
        </Badge>
      </div>

      <Tabs defaultValue="publish" className="space-y-4">
        <TabsList>
          <TabsTrigger value="publish">Publish Video</TabsTrigger>
          <TabsTrigger value="platforms">Platforms ({platforms.length})</TabsTrigger>
          <TabsTrigger value="history">History ({publishHistory.length})</TabsTrigger>
        </TabsList>

        <TabsContent value="publish" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Video Selection */}
            <Card>
              <CardHeader>
                <CardTitle>Select Video</CardTitle>
                <CardDescription>Choose a completed video to publish</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                {availableVideos.length === 0 ? (
                  <div className="text-center py-8">
                    <Upload className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                    <p className="text-muted-foreground">
                      No completed videos available. Generate a video first!
                    </p>
                  </div>
                ) : (
                  <div className="space-y-2">
                    {availableVideos.map((video) => (
                      <div
                        key={video.id}
                        className={`p-3 border rounded-lg cursor-pointer transition-colors ${
                          selectedVideo === video.id ? 'bg-blue-50 border-blue-200' : 'hover:bg-gray-50'
                        }`}
                        onClick={() => setSelectedVideo(video.id)}
                      >
                        <div className="flex items-center space-x-3">
                          <input
                            type="radio"
                            checked={selectedVideo === video.id}
                            onChange={() => setSelectedVideo(video.id)}
                          />
                          <div className="flex-1">
                            <p className="font-medium">Video {video.id.slice(0, 8)}</p>
                            <div className="flex items-center space-x-2 mt-1">
                              <CheckCircle className="h-3 w-3 text-green-500" />
                              <span className="text-xs text-muted-foreground">Ready to publish</span>
                            </div>
                          </div>
                          {video.download_url && (
                            <Button variant="ghost" size="sm" asChild>
                              <a href={video.download_url} target="_blank" rel="noopener noreferrer">
                                <ExternalLink className="h-4 w-4" />
                              </a>
                            </Button>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Platform Selection */}
            <Card>
              <CardHeader>
                <CardTitle>Select Platforms</CardTitle>
                <CardDescription>Choose where to publish your video</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-3">
                  {platforms.map((platform) => (
                    <div
                      key={platform.name}
                      className={`p-4 border rounded-lg cursor-pointer transition-colors ${
                        selectedPlatforms.includes(platform.name) 
                          ? 'bg-blue-50 border-blue-200' 
                          : 'hover:bg-gray-50'
                      }`}
                      onClick={() => togglePlatform(platform.name)}
                    >
                      <div className="flex items-center space-x-3">
                        <input
                          type="checkbox"
                          checked={selectedPlatforms.includes(platform.name)}
                          onChange={() => togglePlatform(platform.name)}
                        />
                        {getPlatformIcon(platform.name)}
                        <div className="flex-1">
                          <p className="font-medium">{platform.display_name}</p>
                          <div className="flex items-center space-x-4 mt-1 text-xs text-muted-foreground">
                            <span>Max: {formatDuration(platform.max_duration)}</span>
                            <span>Formats: {platform.supported_formats.join(', ')}</span>
                          </div>
                          <div className="flex flex-wrap gap-1 mt-1">
                            {platform.features.map((feature) => (
                              <Badge key={feature} variant="outline" className="text-xs">
                                {feature}
                              </Badge>
                            ))}
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Publishing Details */}
          <Card>
            <CardHeader>
              <CardTitle>Publishing Details</CardTitle>
              <CardDescription>Add title, description, and other details</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <label className="text-sm font-medium">Title *</label>
                  <Input
                    placeholder="Enter video title"
                    value={publishData.title}
                    onChange={(e) => setPublishData({...publishData, title: e.target.value})}
                  />
                </div>

                <div className="space-y-2">
                  <label className="text-sm font-medium">Visibility</label>
                  <select 
                    className="w-full p-2 border rounded-md"
                    value={publishData.visibility}
                    onChange={(e) => setPublishData({...publishData, visibility: e.target.value})}
                  >
                    <option value="public">Public</option>
                    <option value="unlisted">Unlisted</option>
                    <option value="private">Private</option>
                  </select>
                </div>
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium">Description *</label>
                <Textarea
                  placeholder="Enter video description"
                  value={publishData.description}
                  onChange={(e) => setPublishData({...publishData, description: e.target.value})}
                  rows={4}
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <label className="text-sm font-medium">Tags</label>
                  <Input
                    placeholder="Enter tags separated by commas"
                    value={publishData.tags}
                    onChange={(e) => setPublishData({...publishData, tags: e.target.value})}
                  />
                </div>

                <div className="space-y-2">
                  <label className="text-sm font-medium">Schedule (Optional)</label>
                  <Input
                    type="datetime-local"
                    value={publishData.scheduled_time}
                    onChange={(e) => setPublishData({...publishData, scheduled_time: e.target.value})}
                  />
                </div>
              </div>

              <Button 
                onClick={publishVideo}
                disabled={!selectedVideo || selectedPlatforms.length === 0 || isPublishing}
                className="w-full"
                size="lg"
              >
                {isPublishing ? (
                  <>
                    <Upload className="h-4 w-4 mr-2" />
                    Publishing...
                  </>
                ) : (
                  <>
                    <Share2 className="h-4 w-4 mr-2" />
                    Publish to {selectedPlatforms.length} Platform{selectedPlatforms.length !== 1 ? 's' : ''}
                  </>
                )}
              </Button>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="platforms" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {platforms.map((platform) => (
              <Card key={platform.name}>
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    {getPlatformIcon(platform.name)}
                    <span>{platform.display_name}</span>
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div>
                    <p className="text-sm font-medium">Supported Formats</p>
                    <div className="flex gap-1 mt-1">
                      {platform.supported_formats.map((format) => (
                        <Badge key={format} variant="outline">{format}</Badge>
                      ))}
                    </div>
                  </div>
                  
                  <div>
                    <p className="text-sm font-medium">Max Duration</p>
                    <p className="text-sm text-muted-foreground">{formatDuration(platform.max_duration)}</p>
                  </div>
                  
                  <div>
                    <p className="text-sm font-medium">Features</p>
                    <div className="flex flex-wrap gap-1 mt-1">
                      {platform.features.map((feature) => (
                        <Badge key={feature} variant="secondary" className="text-xs">{feature}</Badge>
                      ))}
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="history" className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold">Publishing History</h2>
            <Button variant="outline" onClick={fetchPublishHistory}>
              Refresh
            </Button>
          </div>

          {publishHistory.length === 0 ? (
            <Card>
              <CardContent className="flex flex-col items-center justify-center py-8">
                <Share2 className="h-12 w-12 text-muted-foreground mb-4" />
                <p className="text-muted-foreground text-center">
                  No publishing history yet. Publish your first video to see it here!
                </p>
              </CardContent>
            </Card>
          ) : (
            <div className="space-y-4">
              {publishHistory.map((entry) => (
                <Card key={entry.id}>
                  <CardContent className="p-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <h3 className="font-medium">{entry.title}</h3>
                        <p className="text-sm text-muted-foreground">
                          Published: {new Date(entry.published_at).toLocaleString()}
                        </p>
                        <div className="flex items-center space-x-2 mt-2">
                          {entry.platforms.map((platform: string) => (
                            <div key={platform} className="flex items-center space-x-1">
                              {getPlatformIcon(platform)}
                              <span className="text-xs">{platform}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                      
                      <div className="flex items-center space-x-2">
                        {entry.status === 'success' ? (
                          <Badge className="bg-green-500">Published</Badge>
                        ) : (
                          <Badge variant="destructive">Failed</Badge>
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
    </div>
  )
}