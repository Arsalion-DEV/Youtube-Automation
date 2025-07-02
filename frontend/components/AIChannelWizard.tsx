"use client"

import React, { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { 
  Wand2, 
  Target, 
  Calendar, 
  DollarSign, 
  Lightbulb, 
  Hash,
  Image,
  Clock,
  Users,
  TrendingUp,
  CheckCircle,
  Sparkles
} from 'lucide-react'

interface ChannelSetup {
  channel_name: string
  niche: string
  target_audience: string
  content_strategy: string
  posting_schedule: string
  monetization_goals: string
}

interface ChannelConfig {
  id: string
  name: string
  niche: string
  target_audience: string
  content_strategy: string
  posting_schedule: string
  monetization_goals: string
  ai_recommendations: {
    optimal_posting_times: string[]
    content_ideas: string[]
    seo_keywords: string[]
    thumbnail_style: string
    video_length: string
    engagement_strategy: string
  }
  created_at: string
}

export default function AIChannelWizard() {
  const [currentStep, setCurrentStep] = useState(1)
  const [setup, setSetup] = useState<ChannelSetup>({
    channel_name: '',
    niche: '',
    target_audience: '',
    content_strategy: '',
    posting_schedule: '',
    monetization_goals: ''
  })
  
  const [channels, setChannels] = useState<ChannelConfig[]>([])
  const [isCreating, setIsCreating] = useState(false)
  const [activeConfig, setActiveConfig] = useState<ChannelConfig | null>(null)

  useEffect(() => {
    fetchChannels()
  }, [])

  const fetchChannels = async () => {
    try {
      const response = await fetch('/api/v1/wizard/channels')
      if (response.ok) {
        const data = await response.json()
        setChannels(data.channels || [])
      }
    } catch (error) {
      console.error('Failed to fetch channels:', error)
    }
  }

  const setupChannel = async () => {
    setIsCreating(true)
    
    try {
      const response = await fetch('/api/v1/wizard/setup-channel', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ...setup,
          user_id: 'current_user' // Replace with actual user ID
        }),
      })

      if (response.ok) {
        const result = await response.json()
        console.log('Channel setup completed:', result)
        
        // Reset form and refresh channels
        setSetup({
          channel_name: '',
          niche: '',
          target_audience: '',
          content_strategy: '',
          posting_schedule: '',
          monetization_goals: ''
        })
        setCurrentStep(1)
        
        fetchChannels()
      } else {
        const error = await response.json()
        alert(`Error: ${error.detail || 'Failed to setup channel'}`)
      }
    } catch (error) {
      console.error('Error setting up channel:', error)
      alert('Failed to connect to channel setup service')
    } finally {
      setIsCreating(false)
    }
  }

  const nextStep = () => {
    if (currentStep < 6) {
      setCurrentStep(currentStep + 1)
    }
  }

  const prevStep = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1)
    }
  }

  const canProceed = () => {
    switch (currentStep) {
      case 1: return setup.channel_name.trim() !== ''
      case 2: return setup.niche.trim() !== ''
      case 3: return setup.target_audience.trim() !== ''
      case 4: return setup.content_strategy.trim() !== ''
      case 5: return setup.posting_schedule.trim() !== ''
      case 6: return setup.monetization_goals.trim() !== ''
      default: return false
    }
  }

  const renderStep = () => {
    switch (currentStep) {
      case 1:
        return (
          <div className="space-y-4">
            <div className="text-center">
              <Sparkles className="h-12 w-12 text-purple-500 mx-auto mb-4" />
              <h2 className="text-2xl font-bold">Welcome to AI Channel Wizard</h2>
              <p className="text-muted-foreground">
                Let's create your perfect YouTube channel with AI-powered recommendations
              </p>
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium">Channel Name *</label>
              <Input
                placeholder="Enter your channel name (e.g., 'Tech Tutorials Pro')"
                value={setup.channel_name}
                onChange={(e) => setSetup({...setup, channel_name: e.target.value})}
              />
            </div>
          </div>
        )

      case 2:
        return (
          <div className="space-y-4">
            <div className="text-center">
              <Target className="h-12 w-12 text-blue-500 mx-auto mb-4" />
              <h2 className="text-2xl font-bold">Choose Your Niche</h2>
              <p className="text-muted-foreground">
                What topic will your channel focus on?
              </p>
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium">Channel Niche *</label>
              <Input
                placeholder="e.g., Technology, Cooking, Fitness, Education, Gaming"
                value={setup.niche}
                onChange={(e) => setSetup({...setup, niche: e.target.value})}
              />
            </div>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
              {['Technology', 'Cooking', 'Fitness', 'Education', 'Gaming', 'Lifestyle'].map((niche) => (
                <Button
                  key={niche}
                  variant="outline"
                  size="sm"
                  onClick={() => setSetup({...setup, niche})}
                  className={setup.niche === niche ? 'bg-blue-100' : ''}
                >
                  {niche}
                </Button>
              ))}
            </div>
          </div>
        )

      case 3:
        return (
          <div className="space-y-4">
            <div className="text-center">
              <Users className="h-12 w-12 text-green-500 mx-auto mb-4" />
              <h2 className="text-2xl font-bold">Define Your Audience</h2>
              <p className="text-muted-foreground">
                Who are you creating content for?
              </p>
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium">Target Audience *</label>
              <Textarea
                placeholder="Describe your ideal viewers (age, interests, experience level, etc.)"
                value={setup.target_audience}
                onChange={(e) => setSetup({...setup, target_audience: e.target.value})}
                rows={3}
              />
            </div>
          </div>
        )

      case 4:
        return (
          <div className="space-y-4">
            <div className="text-center">
              <Lightbulb className="h-12 w-12 text-yellow-500 mx-auto mb-4" />
              <h2 className="text-2xl font-bold">Content Strategy</h2>
              <p className="text-muted-foreground">
                What type of content will you create?
              </p>
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium">Content Strategy *</label>
              <Textarea
                placeholder="Describe your content approach (tutorials, reviews, entertainment, etc.)"
                value={setup.content_strategy}
                onChange={(e) => setSetup({...setup, content_strategy: e.target.value})}
                rows={3}
              />
            </div>
          </div>
        )

      case 5:
        return (
          <div className="space-y-4">
            <div className="text-center">
              <Calendar className="h-12 w-12 text-indigo-500 mx-auto mb-4" />
              <h2 className="text-2xl font-bold">Posting Schedule</h2>
              <p className="text-muted-foreground">
                How often will you upload content?
              </p>
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium">Posting Schedule *</label>
              <Input
                placeholder="e.g., 'Daily', '3 times per week', 'Weekly on Tuesdays'"
                value={setup.posting_schedule}
                onChange={(e) => setSetup({...setup, posting_schedule: e.target.value})}
              />
            </div>
            <div className="grid grid-cols-2 gap-2">
              {['Daily', '3x per week', 'Weekly', 'Bi-weekly'].map((schedule) => (
                <Button
                  key={schedule}
                  variant="outline"
                  size="sm"
                  onClick={() => setSetup({...setup, posting_schedule: schedule})}
                  className={setup.posting_schedule === schedule ? 'bg-indigo-100' : ''}
                >
                  {schedule}
                </Button>
              ))}
            </div>
          </div>
        )

      case 6:
        return (
          <div className="space-y-4">
            <div className="text-center">
              <DollarSign className="h-12 w-12 text-emerald-500 mx-auto mb-4" />
              <h2 className="text-2xl font-bold">Monetization Goals</h2>
              <p className="text-muted-foreground">
                How do you plan to monetize your channel?
              </p>
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium">Monetization Strategy *</label>
              <Textarea
                placeholder="e.g., 'YouTube ads, sponsorships, affiliate marketing, course sales'"
                value={setup.monetization_goals}
                onChange={(e) => setSetup({...setup, monetization_goals: e.target.value})}
                rows={3}
              />
            </div>
          </div>
        )

      default:
        return null
    }
  }

  return (
    <div className="space-y-6 p-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight flex items-center">
            <Wand2 className="h-8 w-8 mr-3" />
            AI Channel Wizard
          </h1>
          <p className="text-muted-foreground">
            Get AI-powered recommendations for your YouTube channel
          </p>
        </div>
        <Badge variant="default" className="bg-gradient-to-r from-purple-500 to-blue-600">
          <Sparkles className="h-3 w-3 mr-1" />
          AI-Powered
        </Badge>
      </div>

      <Tabs defaultValue="wizard" className="space-y-4">
        <TabsList>
          <TabsTrigger value="wizard">Setup Wizard</TabsTrigger>
          <TabsTrigger value="channels">My Channels ({channels.length})</TabsTrigger>
        </TabsList>

        <TabsContent value="wizard" className="space-y-4">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>Step {currentStep} of 6</CardTitle>
                  <CardDescription>
                    Complete the setup to get personalized recommendations
                  </CardDescription>
                </div>
                <div className="w-32 bg-gray-200 rounded-full h-2">
                  <div 
                    className="bg-purple-600 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${(currentStep / 6) * 100}%` }}
                  ></div>
                </div>
              </div>
            </CardHeader>
            <CardContent className="space-y-6">
              {renderStep()}

              <div className="flex justify-between">
                <Button 
                  variant="outline" 
                  onClick={prevStep}
                  disabled={currentStep === 1}
                >
                  Previous
                </Button>
                
                {currentStep < 6 ? (
                  <Button 
                    onClick={nextStep}
                    disabled={!canProceed()}
                  >
                    Next
                  </Button>
                ) : (
                  <Button 
                    onClick={setupChannel}
                    disabled={!canProceed() || isCreating}
                  >
                    {isCreating ? 'Creating...' : 'Create Channel'}
                  </Button>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="channels" className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold">Your Channels</h2>
            <Button variant="outline" onClick={fetchChannels}>
              Refresh
            </Button>
          </div>

          {channels.length === 0 ? (
            <Card>
              <CardContent className="flex flex-col items-center justify-center py-8">
                <Wand2 className="h-12 w-12 text-muted-foreground mb-4" />
                <p className="text-muted-foreground text-center">
                  No channels configured yet. Use the wizard to create your first channel!
                </p>
              </CardContent>
            </Card>
          ) : (
            <div className="space-y-4">
              {channels.map((channel) => (
                <Card key={channel.id} className="cursor-pointer hover:shadow-md transition-shadow">
                  <CardContent className="p-6">
                    <div className="flex items-start justify-between mb-4">
                      <div>
                        <h3 className="text-xl font-semibold">{channel.name}</h3>
                        <p className="text-muted-foreground">{channel.niche}</p>
                        <p className="text-sm text-muted-foreground mt-1">
                          Created: {new Date(channel.created_at).toLocaleDateString()}
                        </p>
                      </div>
                      <Button 
                        variant="outline" 
                        size="sm"
                        onClick={() => setActiveConfig(activeConfig?.id === channel.id ? null : channel)}
                      >
                        {activeConfig?.id === channel.id ? 'Hide Details' : 'View Recommendations'}
                      </Button>
                    </div>

                    {activeConfig?.id === channel.id && (
                      <div className="space-y-4 border-t pt-4">
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                          <div>
                            <h4 className="font-semibold flex items-center mb-2">
                              <Clock className="h-4 w-4 mr-2" />
                              Optimal Posting Times
                            </h4>
                            <div className="flex flex-wrap gap-1">
                              {channel.ai_recommendations.optimal_posting_times.map((time, index) => (
                                <Badge key={index} variant="outline">{time}</Badge>
                              ))}
                            </div>
                          </div>

                          <div>
                            <h4 className="font-semibold flex items-center mb-2">
                              <Hash className="h-4 w-4 mr-2" />
                              SEO Keywords
                            </h4>
                            <div className="flex flex-wrap gap-1">
                              {channel.ai_recommendations.seo_keywords.map((keyword, index) => (
                                <Badge key={index} variant="secondary">{keyword}</Badge>
                              ))}
                            </div>
                          </div>
                        </div>

                        <div>
                          <h4 className="font-semibold flex items-center mb-2">
                            <Lightbulb className="h-4 w-4 mr-2" />
                            Content Ideas
                          </h4>
                          <ul className="space-y-1">
                            {channel.ai_recommendations.content_ideas.map((idea, index) => (
                              <li key={index} className="text-sm flex items-start">
                                <CheckCircle className="h-3 w-3 mr-2 mt-0.5 text-green-500 flex-shrink-0" />
                                {idea}
                              </li>
                            ))}
                          </ul>
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                          <div>
                            <h4 className="font-semibold flex items-center mb-2">
                              <Image className="h-4 w-4 mr-2" />
                              Thumbnail Style
                            </h4>
                            <p className="text-sm text-muted-foreground">
                              {channel.ai_recommendations.thumbnail_style}
                            </p>
                          </div>

                          <div>
                            <h4 className="font-semibold flex items-center mb-2">
                              <Clock className="h-4 w-4 mr-2" />
                              Video Length
                            </h4>
                            <p className="text-sm text-muted-foreground">
                              {channel.ai_recommendations.video_length}
                            </p>
                          </div>
                        </div>

                        <div>
                          <h4 className="font-semibold flex items-center mb-2">
                            <TrendingUp className="h-4 w-4 mr-2" />
                            Engagement Strategy
                          </h4>
                          <p className="text-sm text-muted-foreground">
                            {channel.ai_recommendations.engagement_strategy}
                          </p>
                        </div>
                      </div>
                    )}
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