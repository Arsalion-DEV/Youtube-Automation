'use client'

import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Sparkles, Target, TrendingUp, Lightbulb, Search, CheckCircle } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Badge } from '@/components/ui/badge'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Skeleton } from '@/components/ui/skeleton'

interface NicheData {
  detected_niche: string
  confidence: number
  suggested_niches: string[]
  niche_description: string
}

interface NicheAnalysisProps {
  data: any
  onUpdate: (data: any) => void
  onComplete: (data: any) => void
  isActive: boolean
}

export function NicheAnalysis({ data, onUpdate, onComplete, isActive }: NicheAnalysisProps) {
  const [channelDescription, setChannelDescription] = useState(data.channel_description || '')
  const [channelName, setChannelName] = useState(data.channel_name || '')
  const [nicheData, setNicheData] = useState<NicheData | null>(data.detected_niche || null)
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [error, setError] = useState('')

  const availableNiches = [
    { value: 'tech_reviews', label: 'Tech Reviews', description: 'Technology reviews, gadget unboxings' },
    { value: 'gaming', label: 'Gaming', description: 'Video games, streaming, esports' },
    { value: 'lifestyle', label: 'Lifestyle', description: 'Daily life, personal development' },
    { value: 'education', label: 'Education', description: 'Learning, tutorials, how-to guides' },
    { value: 'entertainment', label: 'Entertainment', description: 'Comedy, reaction videos, vlogs' },
    { value: 'music', label: 'Music', description: 'Music production, covers, reviews' },
    { value: 'fitness', label: 'Fitness', description: 'Workouts, nutrition, health tips' },
    { value: 'cooking', label: 'Cooking', description: 'Recipes, cooking tutorials, food reviews' },
    { value: 'travel', label: 'Travel', description: 'Travel vlogs, destination guides' },
    { value: 'business', label: 'Business', description: 'Entrepreneurship, finance, career advice' },
    { value: 'news', label: 'News', description: 'Current events, commentary, analysis' },
    { value: 'comedy', label: 'Comedy', description: 'Sketches, stand-up, funny content' },
    { value: 'beauty', label: 'Beauty', description: 'Makeup tutorials, skincare, fashion' },
    { value: 'diy', label: 'DIY', description: 'Crafts, home improvement, projects' },
    { value: 'automotive', label: 'Automotive', description: 'Car reviews, repairs, modifications' }
  ]

  const analyzeNiche = async () => {
    if (!channelDescription.trim()) {
      setError('Please provide a channel description')
      return
    }

    setIsAnalyzing(true)
    setError('')

    try {
      const token = localStorage.getItem('access_token')
      const response = await fetch('/api/wizard/analyze-niche', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          channel_description: channelDescription
        })
      })

      if (!response.ok) {
        throw new Error('Failed to analyze niche')
      }

      const result = await response.json()
      setNicheData(result)
      
      // Update parent component
      const updateData = {
        channel_description: channelDescription,
        channel_name: channelName,
        detected_niche: result
      }
      onUpdate(updateData)

    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to analyze niche')
    } finally {
      setIsAnalyzing(false)
    }
  }

  const selectNiche = (nicheValue: string) => {
    const selectedNiche = availableNiches.find(n => n.value === nicheValue)
    if (selectedNiche) {
      const customNicheData = {
        detected_niche: nicheValue,
        confidence: 1.0,
        suggested_niches: [],
        niche_description: selectedNiche.description
      }
      setNicheData(customNicheData)
      
      const updateData = {
        channel_description: channelDescription,
        channel_name: channelName,
        detected_niche: customNicheData
      }
      onUpdate(updateData)
    }
  }

  const handleComplete = () => {
    if (nicheData) {
      onComplete({
        channel_description: channelDescription,
        channel_name: channelName,
        detected_niche: nicheData
      })
    }
  }

  const selectedNiche = availableNiches.find(n => n.value === nicheData?.detected_niche)

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="text-center">
        <div className="flex justify-center mb-4">
          <div className="p-3 bg-blue-100 dark:bg-blue-900/50 rounded-full">
            <Target className="w-8 h-8 text-blue-600 dark:text-blue-400" />
          </div>
        </div>
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
          AI Niche Analysis
        </h2>
        <p className="text-gray-600 dark:text-gray-400 max-w-2xl mx-auto">
          Let our AI analyze your channel concept and identify the optimal niche for maximum growth potential.
        </p>
      </div>

      {/* Channel Information */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Lightbulb className="w-5 h-5" />
            Channel Information
          </CardTitle>
          <CardDescription>
            Provide basic information about your channel concept
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-2">Channel Name (Optional)</label>
            <Input
              value={channelName}
              onChange={(e) => setChannelName(e.target.value)}
              placeholder="e.g., TechGuru Reviews"
              className="w-full"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium mb-2">Channel Description *</label>
            <Textarea
              value={channelDescription}
              onChange={(e) => setChannelDescription(e.target.value)}
              placeholder="Describe what your channel will be about. Include the types of videos you plan to create, your target audience, and your unique angle."
              rows={4}
              className="w-full"
            />
            <p className="text-xs text-gray-500 mt-1">
              Be specific about your content style, topics, and what makes your channel unique.
            </p>
          </div>

          {error && (
            <Alert variant="destructive">
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          <Button 
            onClick={analyzeNiche}
            disabled={isAnalyzing || !channelDescription.trim()}
            className="w-full"
          >
            {isAnalyzing ? (
              <>
                <Sparkles className="w-4 h-4 mr-2 animate-spin" />
                Analyzing with AI...
              </>
            ) : (
              <>
                <Search className="w-4 h-4 mr-2" />
                Analyze My Niche
              </>
            )}
          </Button>
        </CardContent>
      </Card>

      {/* AI Analysis Results */}
      {isAnalyzing && (
        <Card>
          <CardContent className="p-6">
            <div className="space-y-4">
              <Skeleton className="h-6 w-48" />
              <Skeleton className="h-4 w-full" />
              <Skeleton className="h-4 w-3/4" />
              <div className="flex gap-2">
                <Skeleton className="h-6 w-20" />
                <Skeleton className="h-6 w-20" />
                <Skeleton className="h-6 w-20" />
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {nicheData && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-4"
        >
          <Card className="border-green-200 dark:border-green-700 bg-green-50 dark:bg-green-900/20">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-green-800 dark:text-green-200">
                <CheckCircle className="w-5 h-5" />
                Niche Analysis Complete
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <div className="flex items-center justify-between mb-2">
                  <h3 className="font-semibold text-lg">{selectedNiche?.label}</h3>
                  <Badge variant="secondary" className="bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-100">
                    {Math.round(nicheData.confidence * 100)}% confidence
                  </Badge>
                </div>
                <p className="text-gray-600 dark:text-gray-400 mb-4">
                  {nicheData.niche_description}
                </p>
                
                {nicheData.suggested_niches.length > 0 && (
                  <div>
                    <h4 className="font-medium mb-2">Alternative Niches to Consider:</h4>
                    <div className="flex flex-wrap gap-2">
                      {nicheData.suggested_niches.map((niche) => {
                        const nicheInfo = availableNiches.find(n => n.value === niche)
                        return (
                          <Badge 
                            key={niche} 
                            variant="outline"
                            className="cursor-pointer hover:bg-blue-50 dark:hover:bg-blue-900/20"
                            onClick={() => selectNiche(niche)}
                          >
                            {nicheInfo?.label || niche}
                          </Badge>
                        )
                      })}
                    </div>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </motion.div>
      )}

      {/* Manual Niche Selection */}
      <Card>
        <CardHeader>
          <CardTitle>Or Choose Your Niche Manually</CardTitle>
          <CardDescription>
            Browse all available niches and select the one that best fits your channel
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
            {availableNiches.map((niche) => (
              <Card 
                key={niche.value}
                className={`cursor-pointer transition-all hover:shadow-md ${
                  nicheData?.detected_niche === niche.value 
                    ? 'ring-2 ring-blue-500 bg-blue-50 dark:bg-blue-900/20' 
                    : 'hover:bg-gray-50 dark:hover:bg-gray-800'
                }`}
                onClick={() => selectNiche(niche.value)}
              >
                <CardContent className="p-4">
                  <div className="flex items-center justify-between mb-2">
                    <h3 className="font-medium">{niche.label}</h3>
                    {nicheData?.detected_niche === niche.value && (
                      <CheckCircle className="w-4 h-4 text-blue-600" />
                    )}
                  </div>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    {niche.description}
                  </p>
                </CardContent>
              </Card>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Action Button */}
      {nicheData && (
        <div className="flex justify-center">
          <Button 
            onClick={handleComplete}
            size="lg"
            className="bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700"
          >
            <TrendingUp className="w-4 h-4 mr-2" />
            Continue to SEO Optimization
          </Button>
        </div>
      )}
    </div>
  )
}