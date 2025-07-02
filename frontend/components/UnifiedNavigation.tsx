'use client'

import React, { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  Home, Youtube, Video, BarChart3, Settings, Bell, User, LogOut, 
  Wand2, Globe, Calendar, TrendingUp, Menu, X, ChevronDown,
  Crown, Shield, Zap, Sparkles, Plus, Search
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover'
import { Separator } from '@/components/ui/separator'

interface User {
  user_id: number
  email: string
  first_name: string
  last_name: string
  role: string
  subscription_plan: string
  avatar_url?: string
}

interface NavigationProps {
  user: User | null
  currentPage: string
  onPageChange: (page: string) => void
  onLogin: () => void
  onLogout: () => void
  notifications: number
}

const navigationItems = [
  {
    id: 'dashboard',
    label: 'Dashboard',
    icon: Home,
    description: 'Overview and quick actions'
  },
  {
    id: 'channels',
    label: 'Channels',
    icon: Youtube,
    description: 'Manage YouTube channels',
    badge: 'wizard'
  },
  {
    id: 'videos',
    label: 'Videos',
    icon: Video,
    description: 'Video creation and management'
  },
  {
    id: 'publisher',
    label: 'Multi-Platform',
    icon: Globe,
    description: 'Cross-platform publishing',
    badge: 'new'
  },
  {
    id: 'scheduler',
    label: 'Scheduler',
    icon: Calendar,
    description: 'Content calendar and timing'
  },
  {
    id: 'analytics',
    label: 'Analytics',
    icon: BarChart3,
    description: 'Performance insights'
  }
]

const subscriptionConfig = {
  trial: { label: 'Trial', color: 'gray', icon: Shield },
  standard: { label: 'Standard', color: 'blue', icon: Zap },
  premium: { label: 'Premium', color: 'purple', icon: Crown },
  enterprise: { label: 'Enterprise', color: 'gold', icon: Sparkles }
}

export function UnifiedNavigation({ 
  user, 
  currentPage, 
  onPageChange, 
  onLogin, 
  onLogout,
  notifications = 0 
}: NavigationProps) {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false)
  const [isUserMenuOpen, setIsUserMenuOpen] = useState(false)
  const [unreadNotifications, setUnreadNotifications] = useState(notifications)

  useEffect(() => {
    setUnreadNotifications(notifications)
  }, [notifications])

  const getUserInitials = (user: User) => {
    return `${user.first_name?.[0] || ''}${user.last_name?.[0] || ''}`.toUpperCase() || 'U'
  }

  const getSubscriptionConfig = (plan: string) => {
    return subscriptionConfig[plan as keyof typeof subscriptionConfig] || subscriptionConfig.trial
  }

  const handleNotificationClick = () => {
    setUnreadNotifications(0)
    // Handle notification logic
  }

  return (
    <>
      {/* Main Navigation Bar */}
      <nav className="bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-700 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            
            {/* Logo and Brand */}
            <div className="flex items-center">
              <div className="flex-shrink-0 flex items-center">
                <div className="p-2 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-xl">
                  <Youtube className="w-6 h-6 text-white" />
                </div>
                <div className="ml-3 hidden sm:block">
                  <h1 className="text-xl font-bold text-gray-900 dark:text-white">
                    YouTube Pro
                  </h1>
                  <p className="text-xs text-gray-500 dark:text-gray-400 -mt-1">
                    Automation Platform
                  </p>
                </div>
              </div>

              {/* Desktop Navigation */}
              <div className="hidden lg:ml-8 lg:flex lg:space-x-1">
                {navigationItems.map((item) => {
                  const isActive = currentPage === item.id
                  const Icon = item.icon
                  
                  return (
                    <button
                      key={item.id}
                      onClick={() => onPageChange(item.id)}
                      className={`px-3 py-2 rounded-lg text-sm font-medium transition-all duration-200 flex items-center gap-2 relative ${
                        isActive
                          ? 'bg-blue-100 dark:bg-blue-900/50 text-blue-700 dark:text-blue-300'
                          : 'text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 hover:text-gray-900 dark:hover:text-white'
                      }`}
                    >
                      <Icon className="w-4 h-4" />
                      <span>{item.label}</span>
                      
                      {/* Badges */}
                      {item.badge === 'new' && (
                        <Badge variant="secondary" className="bg-green-100 text-green-800 text-xs">
                          New
                        </Badge>
                      )}
                      {item.badge === 'wizard' && (
                        <Wand2 className="w-3 h-3 text-purple-600" />
                      )}
                    </button>
                  )
                })}
              </div>
            </div>

            {/* Right Side */}
            <div className="flex items-center space-x-4">
              
              {/* Search (Desktop) */}
              <div className="hidden md:block">
                <div className="relative">
                  <Search className="w-4 h-4 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
                  <input
                    type="text"
                    placeholder="Search..."
                    className="pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg text-sm bg-gray-50 dark:bg-gray-800 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
              </div>

              {/* Notifications */}
              {user && (
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={handleNotificationClick}
                  className="relative"
                >
                  <Bell className="w-5 h-5" />
                  {unreadNotifications > 0 && (
                    <Badge 
                      variant="destructive" 
                      className="absolute -top-1 -right-1 w-5 h-5 rounded-full p-0 text-xs flex items-center justify-center"
                    >
                      {unreadNotifications > 9 ? '9+' : unreadNotifications}
                    </Badge>
                  )}
                </Button>
              )}

              {/* User Menu or Login */}
              {user ? (
                <Popover open={isUserMenuOpen} onOpenChange={setIsUserMenuOpen}>
                  <PopoverTrigger asChild>
                    <Button variant="ghost" className="flex items-center gap-2 px-2">
                      <Avatar className="w-8 h-8">
                        <AvatarImage src={user.avatar_url} />
                        <AvatarFallback className="bg-blue-100 text-blue-700 text-sm font-medium">
                          {getUserInitials(user)}
                        </AvatarFallback>
                      </Avatar>
                      <div className="hidden sm:block text-left">
                        <p className="text-sm font-medium text-gray-700 dark:text-gray-200">
                          {user.first_name} {user.last_name}
                        </p>
                        <div className="flex items-center gap-1">
                          <p className="text-xs text-gray-500 capitalize">
                            {getSubscriptionConfig(user.subscription_plan).label}
                          </p>
                          {React.createElement(getSubscriptionConfig(user.subscription_plan).icon, {
                            className: `w-3 h-3 text-${getSubscriptionConfig(user.subscription_plan).color}-600`
                          })}
                        </div>
                      </div>
                      <ChevronDown className="w-4 h-4 text-gray-400" />
                    </Button>
                  </PopoverTrigger>
                  
                  <PopoverContent className="w-64 p-0" align="end">
                    <div className="p-4">
                      <div className="flex items-center gap-3">
                        <Avatar className="w-10 h-10">
                          <AvatarImage src={user.avatar_url} />
                          <AvatarFallback className="bg-blue-100 text-blue-700">
                            {getUserInitials(user)}
                          </AvatarFallback>
                        </Avatar>
                        <div>
                          <p className="font-medium text-gray-900 dark:text-white">
                            {user.first_name} {user.last_name}
                          </p>
                          <p className="text-sm text-gray-500">{user.email}</p>
                          <Badge 
                            variant="outline" 
                            className={`text-${getSubscriptionConfig(user.subscription_plan).color}-600 mt-1`}
                          >
                            {getSubscriptionConfig(user.subscription_plan).label}
                          </Badge>
                        </div>
                      </div>
                    </div>
                    
                    <Separator />
                    
                    <div className="p-2">
                      <Button
                        variant="ghost"
                        className="w-full justify-start"
                        onClick={() => {
                          onPageChange('profile')
                          setIsUserMenuOpen(false)
                        }}
                      >
                        <User className="w-4 h-4 mr-2" />
                        Profile Settings
                      </Button>
                      <Button
                        variant="ghost"
                        className="w-full justify-start"
                        onClick={() => {
                          onPageChange('settings')
                          setIsUserMenuOpen(false)
                        }}
                      >
                        <Settings className="w-4 h-4 mr-2" />
                        Account Settings
                      </Button>
                      <Button
                        variant="ghost"
                        className="w-full justify-start"
                        onClick={() => {
                          onPageChange('billing')
                          setIsUserMenuOpen(false)
                        }}
                      >
                        <Crown className="w-4 h-4 mr-2" />
                        Subscription
                      </Button>
                    </div>
                    
                    <Separator />
                    
                    <div className="p-2">
                      <Button
                        variant="ghost"
                        className="w-full justify-start text-red-600 hover:text-red-700 hover:bg-red-50"
                        onClick={() => {
                          onLogout()
                          setIsUserMenuOpen(false)
                        }}
                      >
                        <LogOut className="w-4 h-4 mr-2" />
                        Sign Out
                      </Button>
                    </div>
                  </PopoverContent>
                </Popover>
              ) : (
                <div className="flex items-center gap-2">
                  <Button variant="ghost" onClick={onLogin}>
                    Sign In
                  </Button>
                  <Button onClick={onLogin} className="bg-gradient-to-r from-blue-600 to-indigo-600">
                    Get Started
                  </Button>
                </div>
              )}

              {/* Mobile Menu Button */}
              <Button
                variant="ghost"
                size="sm"
                className="lg:hidden"
                onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
              >
                {isMobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
              </Button>
            </div>
          </div>
        </div>

        {/* Mobile Navigation Menu */}
        <AnimatePresence>
          {isMobileMenuOpen && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="lg:hidden border-t border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900"
            >
              <div className="px-4 py-2 space-y-1">
                {navigationItems.map((item) => {
                  const isActive = currentPage === item.id
                  const Icon = item.icon
                  
                  return (
                    <button
                      key={item.id}
                      onClick={() => {
                        onPageChange(item.id)
                        setIsMobileMenuOpen(false)
                      }}
                      className={`w-full flex items-center gap-3 px-3 py-3 rounded-lg text-left transition-colors ${
                        isActive
                          ? 'bg-blue-100 dark:bg-blue-900/50 text-blue-700 dark:text-blue-300'
                          : 'text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800'
                      }`}
                    >
                      <Icon className="w-5 h-5" />
                      <div className="flex-1">
                        <div className="flex items-center gap-2">
                          <span className="font-medium">{item.label}</span>
                          {item.badge === 'new' && (
                            <Badge variant="secondary" className="bg-green-100 text-green-800 text-xs">
                              New
                            </Badge>
                          )}
                          {item.badge === 'wizard' && (
                            <Wand2 className="w-3 h-3 text-purple-600" />
                          )}
                        </div>
                        <p className="text-xs text-gray-500">{item.description}</p>
                      </div>
                    </button>
                  )
                })}
              </div>
              
              {/* Mobile Search */}
              <div className="px-4 py-3 border-t border-gray-200 dark:border-gray-700">
                <div className="relative">
                  <Search className="w-4 h-4 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
                  <input
                    type="text"
                    placeholder="Search..."
                    className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg text-sm bg-gray-50 dark:bg-gray-800 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </nav>

      {/* Quick Actions Bar (when logged in) */}
      {user && (
        <div className="bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 border-b border-blue-200 dark:border-blue-700">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex items-center justify-between py-2">
              <div className="flex items-center gap-4 text-sm">
                <span className="text-blue-700 dark:text-blue-300 font-medium">
                  Quick Actions:
                </span>
                <Button variant="ghost" size="sm" onClick={() => onPageChange('channels')}>
                  <Plus className="w-4 h-4 mr-1" />
                  Add Channel
                </Button>
                <Button variant="ghost" size="sm" onClick={() => onPageChange('videos')}>
                  <Video className="w-4 h-4 mr-1" />
                  Create Video
                </Button>
                <Button variant="ghost" size="sm" onClick={() => onPageChange('publisher')}>
                  <Globe className="w-4 h-4 mr-1" />
                  Publish Multi-Platform
                </Button>
              </div>
              
              <div className="flex items-center gap-2 text-sm">
                <span className="text-blue-600 dark:text-blue-400">
                  {getSubscriptionConfig(user.subscription_plan).label} Plan
                </span>
                <Button variant="outline" size="sm" onClick={() => onPageChange('billing')}>
                  <Crown className="w-4 h-4 mr-1" />
                  Upgrade
                </Button>
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  )
}
export default UnifiedNavigation;
