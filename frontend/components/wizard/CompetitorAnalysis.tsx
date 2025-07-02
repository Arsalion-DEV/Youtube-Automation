'use client'

import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Users, TrendingUp, Clock, Video, Eye, Target, BarChart3, Lightbulb } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Progress } from '@/components/ui/progress'
import { Badge } from '@/components/ui/badge'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Skeleton } from '@/components/ui/skeleton'

interface Competitor {
  name: string
  subscribers: string
  avg_views: string
  upload_frequency: string
}

interface CompetitorData {
  top_competitors: Competitor[]
  content_gaps: string[]
  trending_formats: string[]
  optimal_video_length: {
    tutorial: number
    review: number
    vlog: number
    short: number
    live: number
  }
  engagement_insights: {
    best_posting_time: string
    optimal_frequency: string
    high_engagement_topics: string[]
    audience_demographics: {
      age: string
      interests: string[]
    }
  }
  market_analysis: string
}

interface CompetitorAnalysisProps {
  data: any
  onUpdate: (data: any) => void
  onComplete: (data: any) => void
  isActive: boolean
}

export function CompetitorAnalysis({ data, onUpdate, onComplete, isActive }: CompetitorAnalysisProps) {
  const [competitorData, setCompetitorData] = useState<CompetitorData | null>(data.competitor_data || null)
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [error, setError] = useState('')

  const niche = data.detected_niche?.detected_niche || data.niche
  const targetCountry = data.target_country || 'US'

  const analyzeCompetitors = async () => {
    if (!niche) {
      setError('Please complete niche analysis first')
      return
    }

    setIsAnalyzing(true)
    setError('')

    try {
      const token = localStorage.getItem('access_token')
      const response = await fetch('/api/wizard/competitor-analysis', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          niche: niche,
          target_country: targetCountry
        })
      })

      if (!response.ok) {
        throw new Error('Failed to analyze competitors')
      }

      const result = await response.json()
      setCompetitorData(result)
      
      // Update parent component
      onUpdate({ competitor_data: result })

    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to analyze competitors')
    } finally {
      setIsAnalyzing(false)
    }
  }

  const handleComplete = () => {
    if (competitorData) {
      onComplete({ competitor_data: competitorData })
    }
  }

  const formatVideoLength = (seconds: number): string => {
    const minutes = Math.floor(seconds / 60)
    const remainingSeconds = seconds % 60
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="text-center">
        <div className="flex justify-center mb-4">
          <div className="p-3 bg-orange-100 dark:bg-orange-900/50 rounded-full">
            <BarChart3 className="w-8 h-8 text-orange-600 dark:text-orange-400" />
          </div>
        </div>
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
          Competitor Analysis
        </h2>
        <p className="text-gray-600 dark:text-gray-400 max-w-2xl mx-auto">
          Analyze your competition and discover content opportunities in the {niche} niche.
        </p>
      </div>

      {/* Analysis Trigger */}
      {!competitorData && !isAnalyzing && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Target className="w-5 h-5" />
              Market Intelligence
            </CardTitle>
            <CardDescription>
              Analyze top competitors in your niche to identify opportunities and strategies
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center gap-4 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
              <div className="text-blue-600 dark:text-blue-400">
                <BarChart3 className="w-6 h-6" />
              </div>
              <div>
                <h3 className="font-medium text-blue-900 dark:text-blue-100">
                  Analysis includes:
                </h3>
                <ul className="text-sm text-blue-700 dark:text-blue-300 list-disc list-inside mt-1 space-y-1">
                  <li>Top competitors and their metrics</li>
                  <li>Content gaps and opportunities</li>
                  <li>Trending video formats</li>
                  <li>Optimal content length and timing</li>
                  <li>Audience insights and demographics</li>
                </ul>
              </div>
            </div>

            {error && (
              <Alert variant="destructive">
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            )}

            <Button 
              onClick={analyzeCompetitors}
              disabled={!niche}
              className="w-full"
            >
              <BarChart3 className="w-4 h-4 mr-2" />
              Analyze Market Competition
            </Button>
          </CardContent>
        </Card>
      )}

      {/* Loading State */}
      {isAnalyzing && (
        <div className="space-y-6">
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center gap-3 mb-4">
                <div className="animate-pulse">
                  <BarChart3 className="w-5 h-5 text-orange-500" />
                </div>
                <span className="text-sm text-gray-600">Analyzing competitors...</span>
              </div>
              <Progress value={33} className="mb-2" />
              <p className="text-xs text-gray-500">This may take a moment while we gather market data</p>
            </CardContent>
          </Card>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {[1, 2, 3, 4].map((i) => (
              <Card key={i}>
                <CardContent className="p-6">
                  <Skeleton className="h-6 w-32 mb-4" />
                  <div className="space-y-2">
                    <Skeleton className="h-4 w-full" />
                    <Skeleton className="h-4 w-3/4" />
                    <Skeleton className="h-4 w-1/2" />
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      )}

      {/* Analysis Results */}
      {competitorData && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-6"
        >
          {/* Top Competitors */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Users className="w-5 h-5 text-blue-600" />
                Top Competitors
              </CardTitle>
              <CardDescription>
                Leading channels in your niche
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {competitorData.top_competitors.map((competitor, index) => (
                  <div key={index} className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
                    <div className="flex items-center gap-4">
                      <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center text-white font-bold">
                        #{index + 1}
                      </div>
                      <div>
                        <h3 className="font-semibold text-gray-900 dark:text-white">
                          {competitor.name}
                        </h3>
                        <p className="text-sm text-gray-500">
                          {competitor.upload_frequency}
                        </p>
                      </div>
                    </div>
                    <div className="flex gap-4 text-right">
                      <div>
                        <div className="text-sm font-medium text-gray-900 dark:text-white">
                          {competitor.subscribers}
                        </div>
                        <div className="text-xs text-gray-500">subscribers</div>
                      </div>
                      <div>
                        <div className="text-sm font-medium text-gray-900 dark:text-white">
                          {competitor.avg_views}
                        </div>
                        <div className="text-xs text-gray-500">avg views</div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Content Gaps */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Lightbulb className="w-5 h-5 text-yellow-600" />
                  Content Opportunities
                </CardTitle>
                <CardDescription>
                  Underserved content gaps you can fill
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {competitorData.content_gaps.map((gap, index) => (
                    <div key={index} className="flex items-center gap-2 p-2 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg">
                      <div className="w-2 h-2 bg-yellow-500 rounded-full flex-shrink-0" />
                      <span className="text-sm text-yellow-800 dark:text-yellow-200">
                        {gap}
                      </span>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Trending Formats */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <TrendingUp className="w-5 h-5 text-green-600" />
                  Trending Formats
                </CardTitle>
                <CardDescription>
                  Popular video formats in your niche
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {competitorData.trending_formats.map((format, index) => (
                    <Badge key={index} variant="outline" className="block w-full text-left justify-start">
                      <Video className="w-3 h-3 mr-2" />
                      {format}
                    </Badge>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Video Length Optimization */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Clock className="w-5 h-5 text-purple-600" />
                Optimal Video Lengths
              </CardTitle>
              <CardDescription>
                Recommended durations for different content types
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
                {Object.entries(competitorData.optimal_video_length).map(([type, length]) => (
                  <div key={type} className="text-center p-3 bg-purple-50 dark:bg-purple-900/20 rounded-lg">
                    <div className="text-2xl font-bold text-purple-600 dark:text-purple-400">
                      {formatVideoLength(length)}
                    </div>
                    <div className="text-sm text-purple-800 dark:text-purple-200 capitalize">
                      {type}
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Engagement Insights */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Eye className="w-5 h-5 text-indigo-600" />
                Engagement Insights
              </CardTitle>
              <CardDescription>
                Audience behavior and optimization tips
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="p-4 bg-indigo-50 dark:bg-indigo-900/20 rounded-lg">
                  <h4 className="font-semibold text-indigo-800 dark:text-indigo-200 mb-2">
                    Optimal Posting
                  </h4>
                  <div className="space-y-1 text-sm">
                    <div>
                      <strong>Best time:</strong> {competitorData.engagement_insights.best_posting_time}
                    </div>
                    <div>
                      <strong>Frequency:</strong> {competitorData.engagement_insights.optimal_frequency}
                    </div>
                  </div>
                </div>
                
                <div className="p-4 bg-indigo-50 dark:bg-indigo-900/20 rounded-lg">
                  <h4 className="font-semibold text-indigo-800 dark:text-indigo-200 mb-2">
                    Audience Demographics
                  </h4>
                  <div className="space-y-1 text-sm">
                    <div>
                      <strong>Age group:</strong> {competitorData.engagement_insights.audience_demographics.age}
                    </div>
                    <div>
                      <strong>Interests:</strong> {competitorData.engagement_insights.audience_demographics.interests.join(', ')}
                    </div>
                  </div>
                </div>
              </div>
              
              <div>
                <h4 className="font-semibold mb-2">High Engagement Topics:</h4>
                <div className="flex flex-wrap gap-2">
                  {competitorData.engagement_insights.high_engagement_topics.map((topic, index) => (
                    <Badge key={index} variant="secondary" className="bg-indigo-100 text-indigo-800 dark:bg-indigo-900 dark:text-indigo-100">
                      {topic}
                    </Badge>
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Market Analysis */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <BarChart3 className="w-5 h-5 text-gray-600" />
                Market Analysis Summary
              </CardTitle>
              <CardDescription>
                Strategic insights and recommendations
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
                <pre className="text-sm whitespace-pre-wrap text-gray-700 dark:text-gray-300">
                  {competitorData.market_analysis}
                </pre>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      )}

      {/* Action Button */}
      {competitorData && (
        <div className="flex justify-center">
          <Button 
            onClick={handleComplete}
            size="lg"
            className="bg-gradient-to-r from-orange-600 to-red-600 hover:from-orange-700 hover:to-red-700"
          >
            <BarChart3 className="w-4 h-4 mr-2" />
            Continue to Content Strategy
          </Button>
        </div>
      )}
    </div>
  )
}