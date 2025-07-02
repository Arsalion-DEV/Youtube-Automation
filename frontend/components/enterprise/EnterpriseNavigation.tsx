"use client"

import React, { useState } from 'react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { cn } from '@/lib/utils'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import {
  BarChart3,
  Bell,
  BookOpen,
  Building2,
  Command,
  CreditCard,
  FileText,
  Globe,
  Home,
  Menu,
  Moon,
  PlusCircle,
  Search,
  Settings,
  Shield,
  Sun,
  Target,
  Users,
  Video,
  Zap,
} from 'lucide-react'
import { useTheme } from 'next-themes'

interface NavigationProps {
  isCollapsed?: boolean
  onToggle?: () => void
}

export default function EnterpriseNavigation({ isCollapsed = false, onToggle }: NavigationProps) {
  const pathname = usePathname()
  const { theme, setTheme } = useTheme()
  const [quickActionOpen, setQuickActionOpen] = useState(false)

  const mainNavItems = [
    {
      title: 'Dashboard',
      href: '/dashboard',
      icon: Home,
      description: 'Overview and key metrics',
    },
    {
      title: 'Analytics',
      href: '/analytics',
      icon: BarChart3,
      description: 'Advanced analytics and insights',
      badge: 'New',
    },
    {
      title: 'A/B Testing',
      href: '/ab-testing',
      icon: Target,
      description: 'Experiment management',
    },
    {
      title: 'Video Generation',
      href: '/videos',
      icon: Video,
      description: 'AI-powered video creation',
    },
    {
      title: 'Publisher',
      href: '/publisher',
      icon: Globe,
      description: 'Multi-platform publishing',
    },
    {
      title: 'Team Management',
      href: '/team',
      icon: Users,
      description: 'Manage team members and roles',
    },
  ]

  const enterpriseNavItems = [
    {
      title: 'White Label',
      href: '/white-label',
      icon: Building2,
      description: 'Custom branding solutions',
      badge: 'Enterprise',
    },
    {
      title: 'Monetization',
      href: '/monetization',
      icon: CreditCard,
      description: 'Revenue tracking and optimization',
    },
    {
      title: 'API & Integrations',
      href: '/integrations',
      icon: Zap,
      description: 'Third-party integrations',
    },
    {
      title: 'Security',
      href: '/security',
      icon: Shield,
      description: 'Security settings and logs',
    },
  ]

  const quickActions = [
    { title: 'Generate Video', icon: Video, action: () => console.log('Generate Video') },
    { title: 'Create A/B Test', icon: Target, action: () => console.log('Create Test') },
    { title: 'Add Team Member', icon: Users, action: () => console.log('Add Member') },
    { title: 'View Analytics', icon: BarChart3, action: () => console.log('View Analytics') },
  ]

  const NavItem = ({ item, isEnterprise = false }: { item: any; isEnterprise?: boolean }) => {
    const isActive = pathname === item.href
    
    return (
      <Link
        href={item.href}
        className={cn(
          'flex items-center space-x-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors',
          'hover:bg-accent hover:text-accent-foreground',
          isActive ? 'bg-accent text-accent-foreground' : 'text-muted-foreground',
          isCollapsed && 'justify-center px-2'
        )}
      >
        <item.icon className={cn('h-4 w-4 flex-shrink-0', isEnterprise && 'text-orange-500')} />
        {!isCollapsed && (
          <>
            <span className="flex-1">{item.title}</span>
            {item.badge && (
              <Badge variant={isEnterprise ? 'default' : 'secondary'} className="text-xs">
                {item.badge}
              </Badge>
            )}
          </>
        )}
      </Link>
    )
  }

  return (
    <div className={cn('flex flex-col h-full', isCollapsed ? 'w-16' : 'w-64')}>
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b">
        {!isCollapsed && (
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
              <Zap className="h-4 w-4 text-white" />
            </div>
            <div>
              <div className="font-semibold text-sm">Veo-3</div>
              <div className="text-xs text-muted-foreground">Enterprise</div>
            </div>
          </div>
        )}
        <Button variant="ghost" size="sm" onClick={onToggle} className="h-8 w-8 p-0">
          <Menu className="h-4 w-4" />
        </Button>
      </div>

      {/* Search */}
      {!isCollapsed && (
        <div className="p-4">
          <div className="relative">
            <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
            <Input placeholder="Search..." className="pl-8" />
          </div>
        </div>
      )}

      {/* Quick Actions */}
      {!isCollapsed && (
        <div className="px-4 pb-4">
          <Dialog open={quickActionOpen} onOpenChange={setQuickActionOpen}>
            <DialogTrigger asChild>
              <Button variant="outline" className="w-full justify-start">
                <Command className="mr-2 h-4 w-4" />
                Quick Actions
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Quick Actions</DialogTitle>
                <DialogDescription>
                  Perform common tasks quickly
                </DialogDescription>
              </DialogHeader>
              <div className="grid grid-cols-2 gap-2">
                {quickActions.map((action, index) => (
                  <Button
                    key={index}
                    variant="outline"
                    className="h-20 flex-col"
                    onClick={() => {
                      action.action()
                      setQuickActionOpen(false)
                    }}
                  >
                    <action.icon className="h-6 w-6 mb-2" />
                    <span className="text-xs">{action.title}</span>
                  </Button>
                ))}
              </div>
            </DialogContent>
          </Dialog>
        </div>
      )}

      {/* Navigation */}
      <div className="flex-1 px-4 space-y-1">
        {/* Main Navigation */}
        {!isCollapsed && (
          <div className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-2">
            Main
          </div>
        )}
        <div className="space-y-1">
          {mainNavItems.map((item) => (
            <NavItem key={item.href} item={item} />
          ))}
        </div>

        {/* Enterprise Features */}
        {!isCollapsed && (
          <div className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-2 mt-6">
            Enterprise
          </div>
        )}
        <div className="space-y-1">
          {enterpriseNavItems.map((item) => (
            <NavItem key={item.href} item={item} isEnterprise />
          ))}
        </div>
      </div>

      {/* Bottom Actions */}
      <div className="p-4 border-t space-y-2">
        {!isCollapsed && (
          <>
            <Link href="/settings">
              <Button variant="ghost" className="w-full justify-start">
                <Settings className="mr-2 h-4 w-4" />
                Settings
              </Button>
            </Link>
            <Link href="/docs">
              <Button variant="ghost" className="w-full justify-start">
                <BookOpen className="mr-2 h-4 w-4" />
                Documentation
              </Button>
            </Link>
          </>
        )}
        
        {/* Theme Toggle */}
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" className={cn('w-full', !isCollapsed && 'justify-start')}>
              {theme === 'dark' ? (
                <Moon className={cn('h-4 w-4', !isCollapsed && 'mr-2')} />
              ) : (
                <Sun className={cn('h-4 w-4', !isCollapsed && 'mr-2')} />
              )}
              {!isCollapsed && 'Theme'}
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="start">
            <DropdownMenuLabel>Theme</DropdownMenuLabel>
            <DropdownMenuSeparator />
            <DropdownMenuItem onClick={() => setTheme('light')}>
              <Sun className="mr-2 h-4 w-4" />
              Light
            </DropdownMenuItem>
            <DropdownMenuItem onClick={() => setTheme('dark')}>
              <Moon className="mr-2 h-4 w-4" />
              Dark
            </DropdownMenuItem>
            <DropdownMenuItem onClick={() => setTheme('system')}>
              <Settings className="mr-2 h-4 w-4" />
              System
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>

        {/* Notifications */}
        <Button variant="ghost" className={cn('w-full', !isCollapsed && 'justify-start')}>
          <Bell className={cn('h-4 w-4', !isCollapsed && 'mr-2')} />
          {!isCollapsed && 'Notifications'}
          {!isCollapsed && (
            <Badge variant="destructive" className="ml-auto h-5 w-5 rounded-full p-0 text-xs">
              3
            </Badge>
          )}
        </Button>
      </div>
    </div>
  )
}

// Named export for compatibility
export { EnterpriseNavigation }