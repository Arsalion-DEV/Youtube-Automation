'use client'

import React, { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  X, ArrowRight, ArrowLeft, CheckCircle, Play, Users, Zap, 
  Target, BarChart3, Settings, Upload, Calendar, Globe, 
  Sparkles, Trophy, Rocket, Clock
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { Progress } from '@/components/ui/progress'
import { Badge } from '@/components/ui/badge'

interface OnboardingStep {
  id: string
  title: string
  description: string
  icon: React.ReactNode
  targetElement?: string
  action?: () => void
  position?: 'top' | 'bottom' | 'left' | 'right'
  size?: 'small' | 'medium' | 'large'
}

interface OnboardingTourProps {
  isOpen: boolean
  onClose: () => void
  onComplete: () => void
  currentPath?: string
}

const ONBOARDING_STEPS: OnboardingStep[] = [
  {
    id: 'welcome',
    title: 'Welcome to YouTube Automation Platform!',
    description: 'Transform your content creation with AI-powered automation. Let\'s get you started with a quick tour.',
    icon: <Rocket className="h-8 w-8" />,
    size: 'large'
  },
  {
    id: 'dashboard',
    title: 'Your Command Center',
    description: 'This is your dashboard where you can see your channel analytics, recent videos, and quick actions.',
    icon: <BarChart3 className="h-6 w-6" />,
    targetElement: '[data-tour="dashboard"]',
    position: 'bottom'
  },
  {
    id: 'ai-wizard',
    title: 'AI Channel Wizard',
    description: 'Let our AI analyze your niche and create optimized content strategies tailored to your audience.',
    icon: <Sparkles className="h-6 w-6" />,
    targetElement: '[data-tour="ai-wizard"]',
    position: 'bottom'
  },
  {
    id: 'scheduler',
    title: 'Content Scheduler',
    description: 'Plan and schedule your content in advance. Our AI suggests optimal posting times for maximum engagement.',
    icon: <Calendar className="h-6 w-6" />,
    targetElement: '[data-tour="scheduler"]',
    position: 'bottom'
  },
  {
    id: 'publisher',
    title: 'Multi-Platform Publisher',
    description: 'Publish your content across multiple social media platforms simultaneously with optimized formats.',
    icon: <Globe className="h-6 w-6" />,
    targetElement: '[data-tour="publisher"]',
    position: 'bottom'
  },
  {
    id: 'analytics',
    title: 'Performance Analytics',
    description: 'Track your content performance with detailed analytics and insights to improve your strategy.',
    icon: <Target className="h-6 w-6" />,
    targetElement: '[data-tour="analytics"]',
    position: 'bottom'
  },
  {
    id: 'setup-first-channel',
    title: 'Set Up Your First Channel',
    description: 'Ready to get started? Let\'s set up your first channel with our AI wizard.',
    icon: <Play className="h-6 w-6" />,
    action: () => {
      // Navigate to AI wizard
      window.location.href = '/wizard'
    },
    size: 'medium'
  }
]

export default function OnboardingTour({ 
  isOpen, 
  onClose, 
  onComplete, 
  currentPath = '/' 
}: OnboardingTourProps) {
  const [currentStepIndex, setCurrentStepIndex] = useState(0)
  const [completedSteps, setCompletedSteps] = useState<string[]>([])
  const [highlightedElement, setHighlightedElement] = useState<Element | null>(null)

  const currentStep = ONBOARDING_STEPS[currentStepIndex]
  const isLastStep = currentStepIndex === ONBOARDING_STEPS.length - 1
  const progress = ((currentStepIndex + 1) / ONBOARDING_STEPS.length) * 100

  useEffect(() => {
    if (isOpen && currentStep?.targetElement) {
      const element = document.querySelector(currentStep.targetElement)
      if (element) {
        setHighlightedElement(element)
        element.scrollIntoView({ behavior: 'smooth', block: 'center' })
      }
    } else {
      setHighlightedElement(null)
    }
  }, [isOpen, currentStep])

  useEffect(() => {
    if (highlightedElement) {
      highlightedElement.classList.add('tour-highlight')
      return () => {
        highlightedElement.classList.remove('tour-highlight')
      }
    }
  }, [highlightedElement])

  const nextStep = () => {
    setCompletedSteps(prev => [...prev, currentStep.id])
    
    if (currentStep.action) {
      currentStep.action()
      return
    }

    if (isLastStep) {
      handleComplete()
    } else {
      setCurrentStepIndex(prev => prev + 1)
    }
  }

  const previousStep = () => {
    if (currentStepIndex > 0) {
      setCurrentStepIndex(prev => prev - 1)
    }
  }

  const skipTour = () => {
    onClose()
  }

  const handleComplete = () => {
    setCompletedSteps(prev => [...prev, currentStep.id])
    localStorage.setItem('onboarding_completed', 'true')
    onComplete()
    onClose()
  }

  const getTooltipPosition = () => {
    if (!currentStep.targetElement || !highlightedElement) {
      return { top: '50%', left: '50%', transform: 'translate(-50%, -50%)' }
    }

    const rect = highlightedElement.getBoundingClientRect()
    const position = currentStep.position || 'bottom'

    switch (position) {
      case 'top':
        return {
          top: rect.top - 10,
          left: rect.left + rect.width / 2,
          transform: 'translate(-50%, -100%)'
        }
      case 'bottom':
        return {
          top: rect.bottom + 10,
          left: rect.left + rect.width / 2,
          transform: 'translate(-50%, 0)'
        }
      case 'left':
        return {
          top: rect.top + rect.height / 2,
          left: rect.left - 10,
          transform: 'translate(-100%, -50%)'
        }
      case 'right':
        return {
          top: rect.top + rect.height / 2,
          left: rect.right + 10,
          transform: 'translate(0, -50%)'
        }
      default:
        return {
          top: rect.bottom + 10,
          left: rect.left + rect.width / 2,
          transform: 'translate(-50%, 0)'
        }
    }
  }

  const getTooltipSize = () => {
    switch (currentStep.size) {
      case 'small': return 'w-80'
      case 'large': return 'w-96'
      default: return 'w-84'
    }
  }

  if (!isOpen) return null

  return (
    <>
      {/* Overlay */}
      <div className="fixed inset-0 bg-black/50 z-40" />

      {/* Highlight overlay */}
      {highlightedElement && (
        <div
          className="fixed z-41 pointer-events-none"
          style={{
            top: highlightedElement.getBoundingClientRect().top - 4,
            left: highlightedElement.getBoundingClientRect().left - 4,
            width: highlightedElement.getBoundingClientRect().width + 8,
            height: highlightedElement.getBoundingClientRect().height + 8,
            border: '2px solid #3b82f6',
            borderRadius: '8px',
            boxShadow: '0 0 0 4px rgba(59, 130, 246, 0.3)'
          }}
        />
      )}

      {/* Tour tooltip */}
      <AnimatePresence mode="wait">
        <motion.div
          key={currentStep.id}
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          exit={{ opacity: 0, scale: 0.9 }}
          transition={{ duration: 0.2 }}
          className={`fixed z-50 ${getTooltipSize()}`}
          style={getTooltipPosition()}
        >
          <Card className="shadow-2xl border-2 border-blue-200">
            <CardContent className="p-6">
              {/* Header */}
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center space-x-3">
                  <div className="p-2 bg-blue-100 rounded-lg text-blue-600">
                    {currentStep.icon}
                  </div>
                  <div>
                    <h3 className="font-semibold text-lg">{currentStep.title}</h3>
                    <div className="flex items-center space-x-2 text-sm text-muted-foreground">
                      <span>Step {currentStepIndex + 1} of {ONBOARDING_STEPS.length}</span>
                      <Badge variant="secondary" className="text-xs">
                        {Math.round(progress)}% Complete
                      </Badge>
                    </div>
                  </div>
                </div>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={skipTour}
                  className="text-muted-foreground hover:text-foreground"
                >
                  <X className="h-4 w-4" />
                </Button>
              </div>

              {/* Progress bar */}
              <Progress value={progress} className="mb-4" />

              {/* Content */}
              <p className="text-muted-foreground mb-6 leading-relaxed">
                {currentStep.description}
              </p>

              {/* Achievement indicators */}
              <div className="flex flex-wrap gap-2 mb-6">
                {ONBOARDING_STEPS.slice(0, currentStepIndex + 1).map((step, index) => (
                  <div key={step.id} className="flex items-center space-x-1">
                    <CheckCircle className="h-4 w-4 text-green-500" />
                    <span className="text-xs text-green-600">{step.title}</span>
                  </div>
                ))}
              </div>

              {/* Actions */}
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  {currentStepIndex > 0 && (
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={previousStep}
                    >
                      <ArrowLeft className="h-4 w-4 mr-2" />
                      Back
                    </Button>
                  )}
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={skipTour}
                    className="text-muted-foreground"
                  >
                    Skip Tour
                  </Button>
                </div>

                <Button onClick={nextStep} size="sm">
                  {isLastStep ? (
                    <>
                      <Trophy className="h-4 w-4 mr-2" />
                      Get Started
                    </>
                  ) : currentStep.action ? (
                    <>
                      <Rocket className="h-4 w-4 mr-2" />
                      Let's Go
                    </>
                  ) : (
                    <>
                      Next
                      <ArrowRight className="h-4 w-4 ml-2" />
                    </>
                  )}
                </Button>
              </div>

              {/* Tips */}
              {currentStep.id === 'welcome' && (
                <div className="mt-6 p-4 bg-blue-50 rounded-lg border border-blue-200">
                  <div className="flex items-start space-x-3">
                    <Sparkles className="h-5 w-5 text-blue-600 mt-0.5" />
                    <div>
                      <h4 className="font-medium text-blue-900 mb-1">Pro Tip</h4>
                      <p className="text-sm text-blue-800">
                        Take your time with each step. You can always revisit this tour from the help menu.
                      </p>
                    </div>
                  </div>
                </div>
              )}

              {isLastStep && (
                <div className="mt-6 p-4 bg-green-50 rounded-lg border border-green-200">
                  <div className="flex items-start space-x-3">
                    <Trophy className="h-5 w-5 text-green-600 mt-0.5" />
                    <div>
                      <h4 className="font-medium text-green-900 mb-1">You're All Set!</h4>
                      <p className="text-sm text-green-800">
                        You've completed the onboarding tour. Time to create amazing content!
                      </p>
                    </div>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </motion.div>
      </AnimatePresence>

      {/* Quick stats overlay */}
      {currentStep.id === 'welcome' && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="fixed bottom-6 right-6 z-50"
        >
          <Card className="w-64 shadow-xl border-2 border-green-200 bg-green-50">
            <CardContent className="p-4">
              <div className="text-center">
                <h4 className="font-semibold text-green-900 mb-2">Platform Benefits</h4>
                <div className="space-y-2 text-sm text-green-800">
                  <div className="flex items-center justify-between">
                    <span>Time Saved</span>
                    <Badge variant="secondary">80%</Badge>
                  </div>
                  <div className="flex items-center justify-between">
                    <span>Engagement Boost</span>
                    <Badge variant="secondary">+150%</Badge>
                  </div>
                  <div className="flex items-center justify-between">
                    <span>Content Quality</span>
                    <Badge variant="secondary">Premium</Badge>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      )}
    </>
  )
}

// CSS for tour highlight effect
const tourStyles = `
  .tour-highlight {
    position: relative;
    z-index: 42 !important;
    border-radius: 8px;
    box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.3), 0 0 0 2px #3b82f6;
    transition: all 0.3s ease;
  }
  
  .tour-highlight::before {
    content: '';
    position: absolute;
    inset: -8px;
    background: rgba(59, 130, 246, 0.1);
    border-radius: 12px;
    z-index: -1;
    animation: pulse 2s infinite;
  }
  
  @keyframes pulse {
    0%, 100% { opacity: 0.1; }
    50% { opacity: 0.2; }
  }
`

// Inject styles
if (typeof window !== 'undefined') {
  const styleElement = document.createElement('style')
  styleElement.textContent = tourStyles
  document.head.appendChild(styleElement)
}