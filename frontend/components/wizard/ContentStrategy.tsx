'use client'

import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Calendar, Clock, TrendingUp, Users, Target, DollarSign, Video, Lightbulb, CheckCircle } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Badge } from '@/components/ui/badge'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Skeleton } from '@/components/ui/skeleton'

interface ContentCalendarItem {
  date: string
  title: string
  content_pillar: string
  keywords: string[]
  estimated_length: number
  content_type: string
  priority: string
}

interface SeriesIdea {
  title: string
  description: string
  episodes: number
  frequency: string
}

interface ContentStrategyData {
  content_calendar: ContentCalendarItem[]
  content_pillars: string[]
  series_ideas: SeriesIdea[]
  collaboration_opportunities: string[]
  monetization_timeline: Record<string, string>
}

interface ContentStrategyProps {
  data: any
  onUpdate: (data: any) => void
  onComplete: (data: any) => void
  isActive: boolean
}

const CONTENT_FREQUENCIES = [
  { value: 'daily', label: 'Daily', description: '7 videos per week' },
  { value: 'twice_weekly', label: 'Twice Weekly', description: '2 videos per week' },
  { value: 'weekly', label: 'Weekly', description: '1 video per week' },
  { value: 'bi_weekly', label: 'Bi-weekly', description: '1 video every 2 weeks' }
]

export function ContentStrategy({ data, onUpdate, onComplete, isActive }: ContentStrategyProps) {
  const [contentFrequency, setContentFrequency] = useState(data.content_frequency || 'weekly')
  const [strategyData, setStrategyData] = useState<ContentStrategyData | null>(data.content_strategy || null)
  const [isGenerating, setIsGenerating] = useState(false)
  const [error, setError] = useState('')

  const niche = data.detected_niche?.detected_niche || data.niche
  const targetCountry = data.target_country || 'US'
  const channelName = data.channel_name || 'Your Channel'

  const generateContentStrategy = async () => {
    if (!niche) {
      setError('Please complete niche analysis first')
      return
    }

    setIsGenerating(true)
    setError('')

    try {
      const token = localStorage.getItem('access_token')
      const response = await fetch('/api/wizard/content-strategy', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          channel_setup: {
            channel_name: channelName,
            niche: niche,
            target_country: targetCountry
          },
          content_frequency: contentFrequency
        })
      })

      if (!response.ok) {
        throw new Error('Failed to generate content strategy')
      }

      const result = await response.json()
      setStrategyData(result)
      
      // Update parent component
      onUpdate({ 
        content_frequency: contentFrequency,
        content_strategy: result 
      })

    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to generate content strategy')
    } finally {
      setIsGenerating(false)
    }
  }

  const handleComplete = () => {
    if (strategyData) {
      onComplete({ 
        content_frequency: contentFrequency,
        content_strategy: strategyData 
      })
    }
  }

  const formatDate = (dateString: string): string => {
    const date = new Date(dateString)
    return date.toLocaleDateString('en-US', { 
      weekday: 'short', 
      month: 'short', 
      day: 'numeric' 
    })
  }

  const formatVideoLength = (seconds: number): string => {
    const minutes = Math.floor(seconds / 60)
    return `${minutes}min`
  }

  const getPriorityColor = (priority: string): string => {
    switch (priority.toLowerCase()) {
      case 'high': return 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-100'
      case 'medium': return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-100'
      case 'low': return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-100'
      default: return 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-100'
    }
  }

  const selectedFrequency = CONTENT_FREQUENCIES.find(f => f.value === contentFrequency)

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="text-center">
        <div className="flex justify-center mb-4">
          <div className="p-3 bg-indigo-100 dark:bg-indigo-900/50 rounded-full">
            <Calendar className="w-8 h-8 text-indigo-600 dark:text-indigo-400" />
          </div>
        </div>
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
          Content Strategy
        </h2>
        <p className="text-gray-600 dark:text-gray-400 max-w-2xl mx-auto">
          Generate a comprehensive 30-day content calendar and long-term strategy for your {niche} channel.
        </p>
      </div>

      {/* Content Frequency Selection */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Clock className="w-5 h-5" />
            Content Publishing Schedule
          </CardTitle>
          <CardDescription>
            Choose your preferred content publishing frequency
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-2">Publishing Frequency</label>
            <Select value={contentFrequency} onValueChange={setContentFrequency}>
              <SelectTrigger>
                <SelectValue placeholder="Select publishing frequency" />
              </SelectTrigger>
              <SelectContent>
                {CONTENT_FREQUENCIES.map((freq) => (
                  <SelectItem key={freq.value} value={freq.value}>
                    <div>
                      <div className="font-medium">{freq.label}</div>
                      <div className="text-sm text-gray-500">{freq.description}</div>
                    </div>
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            {selectedFrequency && (
              <p className="text-xs text-gray-500 mt-1">
                {selectedFrequency.description}
              </p>
            )}
          </div>

          {error && (
            <Alert variant="destructive">
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          <Button 
            onClick={generateContentStrategy}
            disabled={isGenerating || !niche}
            className="w-full"
          >
            {isGenerating ? (
              <>
                <Calendar className="w-4 h-4 mr-2 animate-pulse" />
                Generating Content Strategy...
              </>
            ) : (
              <>
                <TrendingUp className="w-4 h-4 mr-2" />
                Generate 30-Day Content Plan
              </>
            )}
          </Button>
        </CardContent>
      </Card>

      {/* Loading State */}
      {isGenerating && (
        <div className="space-y-6">
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center gap-3 mb-4">
                <div className="animate-pulse">
                  <Calendar className="w-5 h-5 text-indigo-500" />
                </div>
                <span className="text-sm text-gray-600">Creating your content calendar...</span>
              </div>
              <div className="grid grid-cols-7 gap-2">
                {Array.from({ length: 35 }).map((_, i) => (
                  <Skeleton key={i} className="h-16 w-full" />
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Content Strategy Results */}
      {strategyData && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-6"
        >
          {/* Content Calendar */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Calendar className="w-5 h-5 text-indigo-600" />
                30-Day Content Calendar
              </CardTitle>
              <CardDescription>
                Your personalized content schedule with optimized topics
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {strategyData.content_calendar.map((item, index) => (
                  <div key={index} className="p-4 border border-gray-200 dark:border-gray-700 rounded-lg hover:shadow-md transition-shadow">
                    <div className="flex items-start justify-between mb-2">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <Badge variant="outline" className="text-xs">
                            {formatDate(item.date)}
                          </Badge>
                          <Badge className={getPriorityColor(item.priority)}>
                            {item.priority}
                          </Badge>
                        </div>
                        <h3 className="font-semibold text-gray-900 dark:text-white mb-1">
                          {item.title}
                        </h3>
                        <p className="text-sm text-gray-600 dark:text-gray-400">
                          {item.content_pillar} • {item.content_type} • {formatVideoLength(item.estimated_length)}
                        </p>
                      </div>
                    </div>
                    <div className="flex flex-wrap gap-1 mt-2">
                      {item.keywords.map((keyword, kidx) => (
                        <Badge key={kidx} variant="secondary" className="text-xs">
                          {keyword}
                        </Badge>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Content Pillars */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Target className="w-5 h-5 text-blue-600" />
                  Content Pillars
                </CardTitle>
                <CardDescription>
                  Core content themes for your channel
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {strategyData.content_pillars.map((pillar, index) => (
                    <div key={index} className="flex items-center gap-2 p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                      <div className="w-2 h-2 bg-blue-500 rounded-full flex-shrink-0" />
                      <span className="font-medium text-blue-800 dark:text-blue-200">
                        {pillar}
                      </span>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Series Ideas */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Video className="w-5 h-5 text-purple-600" />
                  Series Ideas
                </CardTitle>
                <CardDescription>
                  Multi-part content series to build audience
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {strategyData.series_ideas.map((series, index) => (
                    <div key={index} className="p-3 border border-purple-200 dark:border-purple-700 rounded-lg">
                      <div className="flex items-center justify-between mb-1">
                        <h4 className="font-medium text-purple-800 dark:text-purple-200">
                          {series.title}
                        </h4>
                        <Badge variant="outline" className="text-xs">
                          {series.episodes} episodes
                        </Badge>
                      </div>
                      <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">
                        {series.description}
                      </p>
                      <p className="text-xs text-purple-600 dark:text-purple-400">
                        {series.frequency}
                      </p>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Collaboration Opportunities */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Users className="w-5 h-5 text-green-600" />
                Collaboration Opportunities
              </CardTitle>
              <CardDescription>
                Ways to collaborate and grow your audience
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {strategyData.collaboration_opportunities.map((opportunity, index) => (
                  <div key={index} className="flex items-center gap-2 p-3 bg-green-50 dark:bg-green-900/20 rounded-lg">
                    <Lightbulb className="w-4 h-4 text-green-600 flex-shrink-0" />
                    <span className="text-sm text-green-800 dark:text-green-200">
                      {opportunity}
                    </span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Monetization Timeline */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <DollarSign className="w-5 h-5 text-yellow-600" />
                Monetization Timeline
              </CardTitle>
              <CardDescription>
                Strategic milestones for channel growth and revenue
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {Object.entries(strategyData.monetization_timeline).map(([period, strategy], index) => (
                  <div key={index} className="flex items-start gap-4">
                    <div className="flex-shrink-0 w-8 h-8 bg-yellow-100 dark:bg-yellow-900/50 rounded-full flex items-center justify-center">
                      <span className="text-sm font-bold text-yellow-800 dark:text-yellow-200">
                        {index + 1}
                      </span>
                    </div>
                    <div className="flex-1">
                      <h4 className="font-semibold text-yellow-800 dark:text-yellow-200 mb-1">
                        {period}
                      </h4>
                      <p className="text-sm text-gray-600 dark:text-gray-400">
                        {strategy}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Success Summary */}
          <Card className="border-2 border-green-200 dark:border-green-700 bg-green-50 dark:bg-green-900/20">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-green-800 dark:text-green-200">
                <CheckCircle className="w-5 h-5" />
                Strategy Complete!
              </CardTitle>
              <CardDescription className="text-green-600 dark:text-green-300">
                Your comprehensive content strategy is ready
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
                <div>
                  <div className="text-2xl font-bold text-green-800 dark:text-green-200">
                    {strategyData.content_calendar.length}
                  </div>
                  <div className="text-sm text-green-600 dark:text-green-300">
                    Videos Planned
                  </div>
                </div>
                <div>
                  <div className="text-2xl font-bold text-green-800 dark:text-green-200">
                    {strategyData.content_pillars.length}
                  </div>
                  <div className="text-sm text-green-600 dark:text-green-300">
                    Content Pillars
                  </div>
                </div>
                <div>
                  <div className="text-2xl font-bold text-green-800 dark:text-green-200">
                    {strategyData.series_ideas.length}
                  </div>
                  <div className="text-sm text-green-600 dark:text-green-300">
                    Series Ideas
                  </div>
                </div>
                <div>
                  <div className="text-2xl font-bold text-green-800 dark:text-green-200">
                    {Object.keys(strategyData.monetization_timeline).length}
                  </div>
                  <div className="text-sm text-green-600 dark:text-green-300">
                    Growth Phases
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      )}

      {/* Action Button */}
      {strategyData && (
        <div className="flex justify-center">
          <Button 
            onClick={handleComplete}
            size="lg"
            className="bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700"
          >
            <CheckCircle className="w-4 h-4 mr-2" />
            Complete Channel Setup
          </Button>
        </div>
      )}
    </div>
  )
}