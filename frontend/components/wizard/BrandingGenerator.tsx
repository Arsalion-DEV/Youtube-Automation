'use client'

import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Palette, Wand2, Type, Image, Download, Copy, CheckCircle, Sparkles } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Badge } from '@/components/ui/badge'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Skeleton } from '@/components/ui/skeleton'

interface BrandingData {
  color_palette: string[]
  font_suggestions: string[]
  brand_guidelines: string
  logo_concept: string
  channel_art_concept: string
}

interface BrandingGeneratorProps {
  data: any
  onUpdate: (data: any) => void
  onComplete: (data: any) => void
  isActive: boolean
}

const STYLE_PREFERENCES = [
  { value: 'modern', label: 'Modern', description: 'Clean, minimal, contemporary design' },
  { value: 'classic', label: 'Classic', description: 'Timeless, elegant, traditional' },
  { value: 'bold', label: 'Bold', description: 'Vibrant, eye-catching, energetic' },
  { value: 'professional', label: 'Professional', description: 'Corporate, trustworthy, polished' },
  { value: 'playful', label: 'Playful', description: 'Fun, colorful, creative' },
  { value: 'minimalist', label: 'Minimalist', description: 'Simple, clean, understated' }
]

export function BrandingGenerator({ data, onUpdate, onComplete, isActive }: BrandingGeneratorProps) {
  const [channelName, setChannelName] = useState(data.channel_name || '')
  const [stylePreference, setStylePreference] = useState(data.style_preference || 'modern')
  const [brandingData, setBrandingData] = useState<BrandingData | null>(data.branding_data || null)
  const [isGenerating, setIsGenerating] = useState(false)
  const [error, setError] = useState('')
  const [copiedItem, setCopiedItem] = useState('')

  const niche = data.detected_niche?.detected_niche || data.niche

  const generateBranding = async () => {
    if (!channelName.trim()) {
      setError('Please provide a channel name')
      return
    }

    if (!niche) {
      setError('Please complete niche analysis first')
      return
    }

    setIsGenerating(true)
    setError('')

    try {
      const token = localStorage.getItem('access_token')
      const response = await fetch('/api/wizard/branding', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          channel_name: channelName,
          niche: niche,
          style_preference: stylePreference
        })
      })

      if (!response.ok) {
        throw new Error('Failed to generate branding')
      }

      const result = await response.json()
      setBrandingData(result)
      
      // Update parent component
      const updateData = {
        channel_name: channelName,
        style_preference: stylePreference,
        branding_data: result
      }
      onUpdate(updateData)

    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to generate branding')
    } finally {
      setIsGenerating(false)
    }
  }

  const copyToClipboard = (text: string, type: string) => {
    navigator.clipboard.writeText(text)
    setCopiedItem(type)
    setTimeout(() => setCopiedItem(''), 2000)
  }

  const handleComplete = () => {
    if (brandingData) {
      onComplete({
        channel_name: channelName,
        style_preference: stylePreference,
        branding_data: brandingData
      })
    }
  }

  const selectedStyle = STYLE_PREFERENCES.find(s => s.value === stylePreference)

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="text-center">
        <div className="flex justify-center mb-4">
          <div className="p-3 bg-purple-100 dark:bg-purple-900/50 rounded-full">
            <Palette className="w-8 h-8 text-purple-600 dark:text-purple-400" />
          </div>
        </div>
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
          Channel Branding
        </h2>
        <p className="text-gray-600 dark:text-gray-400 max-w-2xl mx-auto">
          Generate a cohesive brand identity with colors, fonts, and design guidelines for your {niche} channel.
        </p>
      </div>

      {/* Branding Configuration */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Wand2 className="w-5 h-5" />
            Brand Configuration
          </CardTitle>
          <CardDescription>
            Customize your channel's visual identity and style
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-2">Channel Name *</label>
            <Input
              value={channelName}
              onChange={(e) => setChannelName(e.target.value)}
              placeholder="e.g., TechGuru Reviews"
              className="w-full"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium mb-2">Style Preference</label>
            <Select value={stylePreference} onValueChange={setStylePreference}>
              <SelectTrigger>
                <SelectValue placeholder="Select style preference" />
              </SelectTrigger>
              <SelectContent>
                {STYLE_PREFERENCES.map((style) => (
                  <SelectItem key={style.value} value={style.value}>
                    <div>
                      <div className="font-medium">{style.label}</div>
                      <div className="text-sm text-gray-500">{style.description}</div>
                    </div>
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            {selectedStyle && (
              <p className="text-xs text-gray-500 mt-1">
                {selectedStyle.description}
              </p>
            )}
          </div>

          {error && (
            <Alert variant="destructive">
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          <Button 
            onClick={generateBranding}
            disabled={isGenerating || !channelName.trim() || !niche}
            className="w-full"
          >
            {isGenerating ? (
              <>
                <Sparkles className="w-4 h-4 mr-2 animate-spin" />
                Generating Brand Identity...
              </>
            ) : (
              <>
                <Palette className="w-4 h-4 mr-2" />
                Generate Brand Identity
              </>
            )}
          </Button>
        </CardContent>
      </Card>

      {/* Loading State */}
      {isGenerating && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {[1, 2, 3, 4].map((i) => (
            <Card key={i}>
              <CardContent className="p-6">
                <Skeleton className="h-6 w-32 mb-4" />
                <div className="space-y-2">
                  <Skeleton className="h-8 w-full" />
                  <Skeleton className="h-4 w-3/4" />
                  <Skeleton className="h-4 w-1/2" />
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Branding Results */}
      {brandingData && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-6"
        >
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Color Palette */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Palette className="w-5 h-5 text-purple-600" />
                  Color Palette
                </CardTitle>
                <CardDescription>
                  Primary brand colors for consistency
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 gap-3">
                  {brandingData.color_palette.map((color, index) => (
                    <div 
                      key={index}
                      className="cursor-pointer group"
                      onClick={() => copyToClipboard(color, `color-${index}`)}
                    >
                      <div 
                        className="w-full h-16 rounded-lg border-2 border-gray-200 dark:border-gray-700 group-hover:border-gray-400 transition-colors"
                        style={{ backgroundColor: color }}
                      />
                      <div className="mt-2 text-center">
                        <code className="text-sm font-mono bg-gray-100 dark:bg-gray-800 px-2 py-1 rounded">
                          {color}
                        </code>
                        {copiedItem === `color-${index}` && (
                          <CheckCircle className="w-3 h-3 text-green-600 inline ml-1" />
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Font Suggestions */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Type className="w-5 h-5 text-blue-600" />
                  Typography
                </CardTitle>
                <CardDescription>
                  Recommended fonts for your brand
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {brandingData.font_suggestions.map((font, index) => (
                    <div 
                      key={index}
                      className="p-3 bg-gray-50 dark:bg-gray-800 rounded-lg cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                      onClick={() => copyToClipboard(font, `font-${index}`)}
                    >
                      <div className="flex items-center justify-between">
                        <div>
                          <div className="font-medium text-lg" style={{ fontFamily: font }}>
                            {font}
                          </div>
                          <div className="text-sm text-gray-500">
                            The quick brown fox jumps
                          </div>
                        </div>
                        {copiedItem === `font-${index}` ? (
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
          </div>

          {/* Brand Guidelines */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Image className="w-5 h-5 text-green-600" />
                Brand Guidelines
              </CardTitle>
              <CardDescription>
                Complete branding guidelines for consistent visual identity
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div 
                className="p-4 bg-gray-50 dark:bg-gray-800 rounded-lg cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                onClick={() => copyToClipboard(brandingData.brand_guidelines, 'guidelines')}
              >
                <div className="flex items-start justify-between">
                  <pre className="text-sm whitespace-pre-wrap font-mono">
                    {brandingData.brand_guidelines}
                  </pre>
                  {copiedItem === 'guidelines' ? (
                    <CheckCircle className="w-4 h-4 text-green-600 flex-shrink-0 ml-2" />
                  ) : (
                    <Copy className="w-4 h-4 text-gray-400 flex-shrink-0 ml-2" />
                  )}
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Design Concepts */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Logo Concept */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Sparkles className="w-5 h-5 text-orange-600" />
                  Logo Concept
                </CardTitle>
                <CardDescription>
                  AI-generated logo design concept
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div 
                  className="p-4 bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-800 dark:to-gray-700 rounded-lg cursor-pointer hover:shadow-md transition-all"
                  onClick={() => copyToClipboard(brandingData.logo_concept, 'logo')}
                >
                  <div className="flex items-start justify-between">
                    <p className="text-sm leading-relaxed">
                      {brandingData.logo_concept}
                    </p>
                    {copiedItem === 'logo' ? (
                      <CheckCircle className="w-4 h-4 text-green-600 flex-shrink-0 ml-2" />
                    ) : (
                      <Copy className="w-4 h-4 text-gray-400 flex-shrink-0 ml-2" />
                    )}
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Channel Art Concept */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Image className="w-5 h-5 text-pink-600" />
                  Channel Art Concept
                </CardTitle>
                <CardDescription>
                  Banner design concept for your channel
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div 
                  className="p-4 bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-800 dark:to-gray-700 rounded-lg cursor-pointer hover:shadow-md transition-all"
                  onClick={() => copyToClipboard(brandingData.channel_art_concept, 'banner')}
                >
                  <div className="flex items-start justify-between">
                    <p className="text-sm leading-relaxed">
                      {brandingData.channel_art_concept}
                    </p>
                    {copiedItem === 'banner' ? (
                      <CheckCircle className="w-4 h-4 text-green-600 flex-shrink-0 ml-2" />
                    ) : (
                      <Copy className="w-4 h-4 text-gray-400 flex-shrink-0 ml-2" />
                    )}
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Brand Preview */}
          <Card className="border-2 border-dashed border-purple-200 dark:border-purple-700">
            <CardHeader>
              <CardTitle className="text-center text-purple-800 dark:text-purple-200">
                Brand Preview
              </CardTitle>
              <CardDescription className="text-center">
                Preview of your channel brand with selected colors and style
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div 
                className="p-8 rounded-xl text-center"
                style={{ 
                  background: `linear-gradient(135deg, ${brandingData.color_palette[0]}, ${brandingData.color_palette[1] || brandingData.color_palette[0]})`,
                  color: 'white'
                }}
              >
                <h1 
                  className="text-3xl font-bold mb-2"
                  style={{ fontFamily: brandingData.font_suggestions[0] }}
                >
                  {channelName}
                </h1>
                <p 
                  className="text-lg opacity-90"
                  style={{ fontFamily: brandingData.font_suggestions[1] || brandingData.font_suggestions[0] }}
                >
                  {selectedStyle?.description}
                </p>
                <div className="mt-4 flex justify-center gap-2">
                  {brandingData.color_palette.slice(2).map((color, index) => (
                    <div 
                      key={index}
                      className="w-4 h-4 rounded-full border-2 border-white/50"
                      style={{ backgroundColor: color }}
                    />
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      )}

      {/* Action Button */}
      {brandingData && (
        <div className="flex justify-center">
          <Button 
            onClick={handleComplete}
            size="lg"
            className="bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700"
          >
            <Wand2 className="w-4 h-4 mr-2" />
            Continue to Competitor Analysis
          </Button>
        </div>
      )}
    </div>
  )
}