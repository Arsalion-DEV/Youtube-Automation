"use client"

import React, { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Badge } from "@/components/ui/badge"
import { 
  Video, 
  Plus, 
  Play, 
  Download, 
  Wand2,
  ArrowLeft,
  Sparkles,
  Clock,
  CheckCircle,
  AlertCircle
} from 'lucide-react'

interface Video {
  id: number
  title: string
  status: string
  created_at: string
  updated_at: string
  result_url?: string
  veo3_config?: string
}

export default function VideosPage() {
  const [videos, setVideos] = useState<Video[]>([])
  const [isGenerating, setIsGenerating] = useState(false)
  const [prompt, setPrompt] = useState('')
  const [title, setTitle] = useState('')
  const router = useRouter()

  useEffect(() => {
    fetchVideos()
    const interval = setInterval(fetchVideos, 5000)
    return () => clearInterval(interval)
  }, [])

  const fetchVideos = async () => {
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/videos/list`)
      const data = await response.json()
      setVideos(data.videos || [])
    } catch (error) {
      console.error('Error fetching videos:', error)
    }
  }

  const generateVideo = async () => {
    if (!prompt.trim()) return
    
    setIsGenerating(true)
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/veo3/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          prompt: prompt,
          title: title || 'Generated Video',
          duration: 5,
          quality: 'veo-3'
        }),
      })
      
      const result = await response.json()
      if (response.ok) {
        setPrompt('')
        setTitle('')
        fetchVideos()
      }
    } catch (error) {
      console.error('Error generating video:', error)
    } finally {
      setIsGenerating(false)
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

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 p-6">
      {/* Header */}
      <div className="flex items-center space-x-4 mb-8">
        <Button
          variant="ghost"
          onClick={() => router.push('/')}
          className="text-white hover:bg-white/10"
        >
          <ArrowLeft className="h-5 w-5 mr-2" />
          Back to Dashboard
        </Button>
        <div>
          <h1 className="text-3xl font-bold text-white flex items-center space-x-3">
            <Video className="h-8 w-8 text-purple-400" />
            <span>VEO-3 Video Generation</span>
            <Badge className="bg-purple-500/20 text-purple-400 border-purple-500/30">
              AI Powered
            </Badge>
          </h1>
          <p className="text-white/70 mt-2">
            Generate stunning videos with cutting-edge AI technology
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Video generation form */}
        <div className="lg:col-span-1">
          <Card className="modern-card">
            <CardHeader>
              <CardTitle className="text-white flex items-center space-x-2">
                <Wand2 className="h-5 w-5 text-purple-400" />
                <span>Generate New Video</span>
              </CardTitle>
              <CardDescription className="text-white/60">
                Create amazing videos with AI in seconds
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div>
                <label className="text-sm font-medium text-white/90 mb-2 block">
                  Video Title
                </label>
                <Input
                  placeholder="Enter video title..."
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  className="bg-white/10 border-white/20 text-white placeholder:text-white/50"
                />
              </div>
              
              <div>
                <label className="text-sm font-medium text-white/90 mb-2 block">
                  Video Prompt
                </label>
                <Textarea
                  placeholder="Describe your video... e.g., 'A beautiful sunset over mountains with birds flying'"
                  value={prompt}
                  onChange={(e) => setPrompt(e.target.value)}
                  rows={6}
                  className="bg-white/10 border-white/20 text-white placeholder:text-white/50 resize-none"
                />
              </div>

              <Button
                onClick={generateVideo}
                disabled={!prompt.trim() || isGenerating}
                className="w-full bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-white btn-glow"
              >
                {isGenerating ? (
                  <>
                    <Clock className="h-4 w-4 mr-2 animate-spin" />
                    Generating Video...
                  </>
                ) : (
                  <>
                    <Sparkles className="h-4 w-4 mr-2" />
                    Generate with VEO-3
                  </>
                )}
              </Button>

              <div className="p-4 rounded-lg bg-gradient-to-r from-blue-500/10 to-purple-500/10 border border-blue-500/20">
                <div className="flex items-center space-x-2 mb-2">
                  <Sparkles className="h-4 w-4 text-blue-400" />
                  <span className="text-sm font-medium text-blue-400">VEO-3 Features</span>
                </div>
                <ul className="text-xs text-white/70 space-y-1">
                  <li>• Ultra-realistic video generation</li>
                  <li>• 2-second processing time</li>
                  <li>• Multiple quality options</li>
                  <li>• Enterprise-grade reliability</li>
                </ul>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Videos list */}
        <div className="lg:col-span-2">
          <Card className="modern-card">
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="text-white flex items-center space-x-2">
                    <Play className="h-5 w-5 text-green-400" />
                    <span>Generated Videos</span>
                  </CardTitle>
                  <CardDescription className="text-white/60">
                    Your video generation history
                  </CardDescription>
                </div>
                <Badge className="bg-green-500/20 text-green-400 border-green-500/30">
                  {videos.filter(v => v.status === 'completed').length} Completed
                </Badge>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-4 max-h-96 overflow-y-auto custom-scrollbar">
                {videos.length === 0 ? (
                  <div className="text-center py-12">
                    <Video className="h-16 w-16 text-white/30 mx-auto mb-4" />
                    <p className="text-white/60 mb-4">No videos generated yet</p>
                    <p className="text-sm text-white/40">
                      Create your first video using the form on the left
                    </p>
                  </div>
                ) : (
                  videos.map((video) => (
                    <div
                      key={video.id}
                      className="p-4 rounded-lg bg-white/5 hover:bg-white/10 transition-all border border-white/10 card-hover"
                    >
                      <div className="flex items-start justify-between mb-3">
                        <div className="flex items-center space-x-3">
                          {getStatusIcon(video.status)}
                          <div>
                            <h3 className="font-medium text-white">{video.title}</h3>
                            <p className="text-xs text-white/60">
                              Created {new Date(video.created_at).toLocaleDateString()}
                            </p>
                          </div>
                        </div>
                        <Badge className={getStatusBadge(video.status)}>
                          {video.status}
                        </Badge>
                      </div>
                      
                      {video.veo3_config && (
                        <div className="mb-3">
                          <p className="text-xs text-white/50 mb-1">Prompt:</p>
                          <p className="text-sm text-white/80 bg-white/5 p-2 rounded text-truncate">
                            {JSON.parse(video.veo3_config).prompt}
                          </p>
                        </div>
                      )}

                      <div className="flex items-center justify-between">
                        <div className="text-xs text-white/50">
                          Updated {new Date(video.updated_at).toLocaleTimeString()}
                        </div>
                        {video.result_url && (
                          <div className="flex items-center space-x-2">
                            <Button
                              size="sm"
                              className="bg-green-500/20 hover:bg-green-500/30 text-green-400 border-green-500/30"
                              onClick={() => window.open(video.result_url, '_blank')}
                            >
                              <Play className="h-4 w-4 mr-2" />
                              View
                            </Button>
                            <Button
                              size="sm"
                              variant="ghost"
                              className="text-white/70 hover:text-white"
                            >
                              <Download className="h-4 w-4" />
                            </Button>
                          </div>
                        )}
                      </div>
                    </div>
                  ))
                )}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
