'use client'

import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { TrendingUp, Globe, Hash, Clock, Target, Copy, CheckCircle } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Badge } from '@/components/ui/badge'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Skeleton } from '@/components/ui/skeleton'

interface SEOData {
  keywords: string[]
  trending_topics: string[]
  optimal_upload_times: string[]
  hashtag_suggestions: string[]
  title_templates: string[]
  description_templates: string[]
}

interface SEOOptimizationProps {
  data: any
  onUpdate: (data: any) => void
  onComplete: (data: any) => void
  isActive: boolean
}

const COUNTRIES = [
  { code: 'US', name: 'United States', timezone: 'America/New_York', language: 'en-US' },
  { code: 'GB', name: 'United Kingdom', timezone: 'Europe/London', language: 'en-GB' },
  { code: 'CA', name: 'Canada', timezone: 'America/Toronto', language: 'en-CA' },
  { code: 'AU', name: 'Australia', timezone: 'Australia/Sydney', language: 'en-AU' },
  { code: 'IN', name: 'India', timezone: 'Asia/Kolkata', language: 'hi-IN' },
  { code: 'DE', name: 'Germany', timezone: 'Europe/Berlin', language: 'de-DE' }
]

export function SEOOptimization({ data, onUpdate, onComplete, isActive }: SEOOptimizationProps) {
  const [selectedCountry, setSelectedCountry] = useState(data.target_country || 'US')
  const [seoData, setSeoData] = useState<SEOData | null>(data.seo_data || null)
  const [isOptimizing, setIsOptimizing] = useState(false)
  const [error, setError] = useState('')
  const [copiedItem, setCopiedItem] = useState('')

  const niche = data.detected_niche?.detected_niche || data.niche

  const optimizeSEO = async () => {
    if (!niche) {
      setError('Please complete niche analysis first')
      return
    }

    setIsOptimizing(true)
    setError('')

    try {
      const token = localStorage.getItem('access_token')
      const response = await fetch('/api/wizard/seo-optimization', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          niche: niche,
          target_country: selectedCountry
        })
      })

      if (!response.ok) {
        throw new Error('Failed to optimize SEO')
      }

      const result = await response.json()
      setSeoData(result)
      
      // Update parent component
      const updateData = {
        target_country: selectedCountry,
        seo_data: result
      }
      onUpdate(updateData)

    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to optimize SEO')
    } finally {
      setIsOptimizing(false)
    }
  }

  const copyToClipboard = (text: string, type: string) => {
    navigator.clipboard.writeText(text)
    setCopiedItem(type)
    setTimeout(() => setCopiedItem(''), 2000)
  }

  const handleComplete = () => {
    if (seoData) {
      onComplete({
        target_country: selectedCountry,
        seo_data: seoData
      })
    }
  }

  const selectedCountryInfo = COUNTRIES.find(c => c.code === selectedCountry)

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="text-center">
        <div className="flex justify-center mb-4">
          <div className="p-3 bg-green-100 dark:bg-green-900/50 rounded-full">
            <TrendingUp className="w-8 h-8 text-green-600 dark:text-green-400" />
          </div>
        </div>
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
          SEO Optimization
        </h2>
        <p className="text-gray-600 dark:text-gray-400 max-w-2xl mx-auto">
          Get country-specific SEO recommendations, keywords, and optimal posting strategies for your {niche} channel.
        </p>
      </div>

      {/* Country Selection */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Globe className="w-5 h-5" />
            Target Country & Market
          </CardTitle>
          <CardDescription>
            Select your primary target market for localized SEO optimization
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-2">Primary Target Country</label>
            <Select value={selectedCountry} onValueChange={setSelectedCountry}>
              <SelectTrigger>
                <SelectValue placeholder="Select target country" />
              </SelectTrigger>
              <SelectContent>
                {COUNTRIES.map((country) => (
                  <SelectItem key={country.code} value={country.code}>
                    <div className="flex items-center gap-2">
                      <span>{country.name}</span>
                      <Badge variant="outline" className="text-xs">
                        {country.language}
                      </Badge>
                    </div>
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            {selectedCountryInfo && (
              <p className="text-xs text-gray-500 mt-1">
                Timezone: {selectedCountryInfo.timezone} | Language: {selectedCountryInfo.language}
              </p>
            )}
          </div>

          {error && (
            <Alert variant="destructive">
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          <Button 
            onClick={optimizeSEO}
            disabled={isOptimizing || !niche}
            className="w-full"
          >
            {isOptimizing ? (
              <>
                <TrendingUp className="w-4 h-4 mr-2 animate-pulse" />
                Optimizing SEO...
              </>
            ) : (
              <>
                <Target className="w-4 h-4 mr-2" />
                Generate SEO Strategy
              </>
            )}
          </Button>
        </CardContent>
      </Card>

      {/* Loading State */}
      {isOptimizing && (
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
      )}

      {/* SEO Results */}
      {seoData && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-6"
        >
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Keywords */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Target className="w-5 h-5 text-blue-600" />
                  Primary Keywords
                </CardTitle>
                <CardDescription>
                  High-value keywords for your niche
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="flex flex-wrap gap-2">
                  {seoData.keywords.map((keyword, index) => (
                    <Badge 
                      key={index}
                      variant="secondary"
                      className="cursor-pointer hover:bg-blue-100 dark:hover:bg-blue-900/50"
                      onClick={() => copyToClipboard(keyword, `keyword-${index}`)}
                    >
                      {keyword}
                      {copiedItem === `keyword-${index}` ? (
                        <CheckCircle className="w-3 h-3 ml-1" />
                      ) : (
                        <Copy className="w-3 h-3 ml-1" />
                      )}
                    </Badge>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Trending Topics */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <TrendingUp className="w-5 h-5 text-green-600" />
                  Trending Topics
                </CardTitle>
                <CardDescription>
                  Hot topics in your market
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="flex flex-wrap gap-2">
                  {seoData.trending_topics.map((topic, index) => (
                    <Badge 
                      key={index}
                      variant="outline"
                      className="cursor-pointer hover:bg-green-100 dark:hover:bg-green-900/50"
                      onClick={() => copyToClipboard(topic, `topic-${index}`)}
                    >
                      {topic}
                      {copiedItem === `topic-${index}` ? (
                        <CheckCircle className="w-3 h-3 ml-1" />
                      ) : (
                        <Copy className="w-3 h-3 ml-1" />
                      )}
                    </Badge>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Upload Times */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Clock className="w-5 h-5 text-purple-600" />
                  Optimal Upload Times
                </CardTitle>
                <CardDescription>
                  Best times to post in {selectedCountryInfo?.name}
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="flex flex-wrap gap-2">
                  {seoData.optimal_upload_times.map((time, index) => (
                    <Badge 
                      key={index}
                      variant="secondary"
                      className="bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-100"
                    >
                      {time}
                    </Badge>
                  ))}
                </div>
                <p className="text-xs text-gray-500 mt-2">
                  Times shown in {selectedCountryInfo?.timezone}
                </p>
              </CardContent>
            </Card>

            {/* Hashtags */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Hash className="w-5 h-5 text-orange-600" />
                  Hashtag Suggestions
                </CardTitle>
                <CardDescription>
                  Recommended hashtags for discovery
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="flex flex-wrap gap-2">
                  {seoData.hashtag_suggestions.map((hashtag, index) => (
                    <Badge 
                      key={index}
                      variant="outline"
                      className="cursor-pointer hover:bg-orange-100 dark:hover:bg-orange-900/50"
                      onClick={() => copyToClipboard(hashtag, `hashtag-${index}`)}
                    >
                      {hashtag}
                      {copiedItem === `hashtag-${index}` ? (
                        <CheckCircle className="w-3 h-3 ml-1" />
                      ) : (
                        <Copy className="w-3 h-3 ml-1" />
                      )}
                    </Badge>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Title Templates */}
          <Card>
            <CardHeader>
              <CardTitle>Video Title Templates</CardTitle>
              <CardDescription>
                Proven title formats that drive clicks and views
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {seoData.title_templates.map((template, index) => (
                  <div 
                    key={index}
                    className="p-3 bg-gray-50 dark:bg-gray-800 rounded-lg cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                    onClick={() => copyToClipboard(template, `title-${index}`)}
                  >
                    <div className="flex items-center justify-between">
                      <span className="font-mono text-sm">{template}</span>
                      {copiedItem === `title-${index}` ? (
                        <CheckCircle className="w-4 h-4 text-green-600" />
                      ) : (
                        <Copy className="w-4 h-4 text-gray-400" />
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Description Templates */}
          <Card>
            <CardHeader>
              <CardTitle>Description Templates</CardTitle>
              <CardDescription>
                Engaging description formats for better SEO
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {seoData.description_templates.map((template, index) => (
                  <div 
                    key={index}
                    className="p-3 bg-gray-50 dark:bg-gray-800 rounded-lg cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                    onClick={() => copyToClipboard(template, `desc-${index}`)}
                  >
                    <div className="flex items-center justify-between">
                      <span className="text-sm">{template}</span>
                      {copiedItem === `desc-${index}` ? (
                        <CheckCircle className="w-4 h-4 text-green-600" />
                      ) : (
                        <Copy className="w-4 h-4 text-gray-400" />
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </motion.div>
      )}

      {/* Action Button */}
      {seoData && (
        <div className="flex justify-center">
          <Button 
            onClick={handleComplete}
            size="lg"
            className="bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700"
          >
            <TrendingUp className="w-4 h-4 mr-2" />
            Continue to Channel Branding
          </Button>
        </div>
      )}
    </div>
  )
}