"use client"

import React, { useState, useEffect } from 'react'
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Sheet, SheetContent, SheetTrigger } from "@/components/ui/sheet"
import { 
  Video, 
  Wand2, 
  Share2, 
  BarChart3, 
  Target, 
  DollarSign,
  Users,
  Globe,
  PlayCircle,
  TrendingUp,
  CheckCircle,
  Clock,
  Zap,
  Youtube,
  Settings,
  Building2,
  Menu,
  Home,
  FileVideo,
  Sparkles,
  Network,
  MessageSquare,
  Database,
  Shield,
  MonitorSpeaker,
  Palette,
  Bot,
  Workflow
} from 'lucide-react'
import Link from 'next/link'
import { useTheme } from 'next-themes'

interface SidebarProps {
  className?: string
}

const sidebarItems = [
  {
    title: "Dashboard",
    icon: Home,
    href: "/",
    description: "Overview and analytics"
  },
  {
    title: "Video Generation",
    icon: Video,
    href: "/videos",
    description: "Create and manage videos",
    subItems: [
      { title: "VEO3 Generator", href: "/videos/generate", icon: Sparkles },
      { title: "Video Library", href: "/videos/library", icon: FileVideo },
      { title: "Processing Queue", href: "/videos/queue", icon: Clock }
    ]
  },
  {
    title: "AI Channel Wizard",
    icon: Wand2,
    href: "/wizard",
    description: "Automated channel setup",
    subItems: [
      { title: "Channel Setup", href: "/wizard/setup", icon: Settings },
      { title: "Content Strategy", href: "/wizard/strategy", icon: Target },
      { title: "Branding Generator", href: "/wizard/branding", icon: Palette }
    ]
  },
  {
    title: "Multi-Platform Publisher",
    icon: Share2,
    href: "/publisher",
    description: "Publish across platforms",
    subItems: [
      { title: "YouTube", href: "/publisher/youtube", icon: Youtube },
      { title: "Social Media", href: "/publisher/social", icon: MessageSquare },
      { title: "Scheduling", href: "/publisher/schedule", icon: Clock }
    ]
  },
  {
    title: "Analytics",
    icon: BarChart3,
    href: "/analytics",
    description: "Performance metrics",
    subItems: [
      { title: "Video Analytics", href: "/analytics/videos", icon: TrendingUp },
      { title: "Revenue Tracking", href: "/analytics/revenue", icon: DollarSign },
      { title: "A/B Testing", href: "/analytics/ab-testing", icon: Target }
    ]
  },
  {
    title: "Channel Management",
    icon: Users,
    href: "/channels",
    description: "Manage connected channels",
    subItems: [
      { title: "Connected Channels", href: "/channels/connected", icon: Network },
      { title: "Authentication", href: "/channels/auth", icon: Shield },
      { title: "Channel Settings", href: "/channels/settings", icon: Settings }
    ]
  },
  {
    title: "Integrations",
    icon: Globe,
    href: "/integrations",
    description: "Third-party connections",
    subItems: [
      { title: "API Integrations", href: "/integrations/api", icon: Database },
      { title: "Webhooks", href: "/integrations/webhooks", icon: Workflow },
      { title: "Social Platforms", href: "/integrations/social", icon: Network }
    ]
  },
  {
    title: "Enterprise",
    icon: Building2,
    href: "/enterprise",
    description: "Enterprise features",
    subItems: [
      { title: "Team Management", href: "/enterprise/team", icon: Users },
      { title: "White Labeling", href: "/enterprise/branding", icon: Palette },
      { title: "Advanced Analytics", href: "/enterprise/analytics", icon: BarChart3 }
    ]
  },
  {
    title: "System Monitoring",
    icon: MonitorSpeaker,
    href: "/system",
    description: "System health and logs"
  },
  {
    title: "Settings",
    icon: Settings,
    href: "/settings",
    description: "Application settings"
  }
]

function SidebarContent({ className }: SidebarProps) {
  const [expandedItems, setExpandedItems] = useState<string[]>([])
  const [activeItem, setActiveItem] = useState("/")

  const toggleExpanded = (href: string) => {
    setExpandedItems(prev => 
      prev.includes(href) 
        ? prev.filter(item => item !== href)
        : [...prev, href]
    )
  }

  return (
    <div className={cn("pb-12", className)}>
      <div className="space-y-4 py-4">
        <div className="px-3 py-2">
          <div className="flex items-center space-x-2 mb-4">
            <Bot className="h-8 w-8 text-primary" />
            <div>
              <h2 className="text-lg font-semibold tracking-tight">
                VEO-3 Automation
              </h2>
              <p className="text-xs text-muted-foreground">
                YouTube Automation Platform
              </p>
            </div>
          </div>
          <div className="space-y-1">
            {sidebarItems.map((item) => (
              <div key={item.href}>
                <Button
                  variant={activeItem === item.href ? "secondary" : "ghost"}
                  className={cn(
                    "w-full justify-start",
                    activeItem === item.href && "bg-secondary"
                  )}
                  onClick={() => {
                    setActiveItem(item.href)
                    if (item.subItems) {
                      toggleExpanded(item.href)
                    }
                  }}
                >
                  <item.icon className="mr-2 h-4 w-4" />
                  {item.title}
                  {item.subItems && (
                    <ChevronRight className={cn(
                      "ml-auto h-4 w-4 transition-transform",
                      expandedItems.includes(item.href) && "rotate-90"
                    )} />
                  )}
                </Button>
                
                {item.subItems && expandedItems.includes(item.href) && (
                  <div className="ml-6 mt-1 space-y-1">
                    {item.subItems.map((subItem) => (
                      <Button
                        key={subItem.href}
                        variant="ghost"
                        className="w-full justify-start text-sm"
                        onClick={() => setActiveItem(subItem.href)}
                      >
                        <subItem.icon className="mr-2 h-3 w-3" />
                        {subItem.title}
                      </Button>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}

function ChevronRight({ className }: { className?: string }) {
  return (
    <svg
      className={className}
      width="15"
      height="15"
      viewBox="0 0 15 15"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
    >
      <path
        d="M6.1584 3.13508C6.35985 2.94621 6.67627 2.95642 6.86514 3.15788L10.6151 7.15788C10.7954 7.3502 10.7954 7.64949 10.6151 7.84182L6.86514 11.8418C6.67627 12.0433 6.35985 12.0535 6.1584 11.8646C5.95694 11.6757 5.94673 11.3593 6.1356 11.1579L9.565 7.49985L6.1356 3.84182C5.94673 3.64036 5.95694 3.32394 6.1584 3.13508Z"
        fill="currentColor"
        fillRule="evenodd"
        clipRule="evenodd"
      />
    </svg>
  )
}

export default function ComprehensiveLayout({ children }: { children: React.ReactNode }) {
  const { setTheme, theme } = useTheme()
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
  }, [])

  if (!mounted) return null

  return (
    <div className="min-h-screen bg-background">
      {/* Desktop sidebar */}
      <div className="hidden md:flex md:w-72 md:flex-col md:fixed md:inset-y-0">
        <div className="flex-1 flex flex-col min-h-0 border-r bg-card">
          <ScrollArea className="flex-1">
            <SidebarContent />
          </ScrollArea>
        </div>
      </div>

      {/* Mobile header */}
      <div className="md:hidden">
        <div className="flex items-center justify-between p-4 border-b">
          <div className="flex items-center space-x-2">
            <Bot className="h-6 w-6 text-primary" />
            <span className="font-semibold">VEO-3 Automation</span>
          </div>
          <div className="flex items-center space-x-2">
            <Button
              variant="ghost"
              size="icon"
              onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
            >
              {theme === "dark" ? "🌞" : "🌙"}
            </Button>
            <Sheet>
              <SheetTrigger asChild>
                <Button variant="ghost" size="icon">
                  <Menu className="h-5 w-5" />
                </Button>
              </SheetTrigger>
              <SheetContent side="left" className="w-72 p-0">
                <ScrollArea className="h-full">
                  <SidebarContent />
                </ScrollArea>
              </SheetContent>
            </Sheet>
          </div>
        </div>
      </div>

      {/* Main content */}
      <div className="md:pl-72">
        <div className="flex flex-col flex-1">
          {/* Top bar */}
          <header className="hidden md:flex items-center justify-between p-4 border-b bg-card">
            <div>
              <h1 className="text-2xl font-bold tracking-tight">Dashboard</h1>
              <p className="text-muted-foreground">
                Manage your YouTube automation workflow
              </p>
            </div>
            <div className="flex items-center space-x-4">
              <Button
                variant="ghost"
                size="icon"
                onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
              >
                {theme === "dark" ? "🌞" : "🌙"}
              </Button>
              <Badge variant="outline" className="text-green-600">
                <CheckCircle className="mr-1 h-3 w-3" />
                System Healthy
              </Badge>
            </div>
          </header>

          {/* Page content */}
          <main className="flex-1 p-4 md:p-6">
            {children}
          </main>
        </div>
      </div>
    </div>
  )
}