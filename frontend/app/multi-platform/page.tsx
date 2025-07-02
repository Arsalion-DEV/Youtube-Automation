"use client";

import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  Globe, Youtube, Facebook, Twitter, Instagram, Linkedin,
  Play, Pause, Settings, Plus, TrendingUp, Users, Eye,
  Calendar, Clock, CheckCircle, AlertCircle, XCircle,
  BarChart3, Zap, Target, Share2
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';

interface Platform {
  id: string;
  name: string;
  icon: React.ReactNode;
  connected: boolean;
  followers: number;
  engagement: number;
  postsThisMonth: number;
  lastPost: string;
  status: 'active' | 'paused' | 'error';
  color: string;
}

interface Campaign {
  id: string;
  title: string;
  platforms: string[];
  status: 'scheduled' | 'publishing' | 'completed' | 'failed';
  scheduledTime: string;
  reach: number;
  engagement: number;
  clicks: number;
}

export default function MultiPlatformPage() {
  const [platforms, setPlatforms] = useState<Platform[]>([]);
  const [campaigns, setCampaigns] = useState<Campaign[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');

  useEffect(() => {
    loadPlatformData();
  }, []);

  const loadPlatformData = async () => {
    setIsLoading(true);
    try {
      // Mock data - replace with actual API calls
      const mockPlatforms: Platform[] = [
        {
          id: 'youtube',
          name: 'YouTube',
          icon: <Youtube className="w-6 h-6" />,
          connected: true,
          followers: 125000,
          engagement: 94.2,
          postsThisMonth: 8,
          lastPost: '2 hours ago',
          status: 'active',
          color: 'text-red-600'
        },
        {
          id: 'facebook',
          name: 'Facebook',
          icon: <Facebook className="w-6 h-6" />,
          connected: true,
          followers: 89000,
          engagement: 76.8,
          postsThisMonth: 15,
          lastPost: '4 hours ago',
          status: 'active',
          color: 'text-blue-600'
        },
        {
          id: 'twitter',
          name: 'Twitter',
          icon: <Twitter className="w-6 h-6" />,
          connected: false,
          followers: 0,
          engagement: 0,
          postsThisMonth: 0,
          lastPost: 'Never',
          status: 'paused',
          color: 'text-sky-500'
        },
        {
          id: 'instagram',
          name: 'Instagram',
          icon: <Instagram className="w-6 h-6" />,
          connected: true,
          followers: 45000,
          engagement: 82.5,
          postsThisMonth: 12,
          lastPost: '1 day ago',
          status: 'active',
          color: 'text-pink-600'
        },
        {
          id: 'linkedin',
          name: 'LinkedIn',
          icon: <Linkedin className="w-6 h-6" />,
          connected: false,
          followers: 0,
          engagement: 0,
          postsThisMonth: 0,
          lastPost: 'Never',
          status: 'paused',
          color: 'text-blue-700'
        }
      ];

      const mockCampaigns: Campaign[] = [
        {
          id: '1',
          title: 'AI Technology Series - Episode 3',
          platforms: ['youtube', 'facebook', 'instagram'],
          status: 'scheduled',
          scheduledTime: '2024-07-01T15:00:00Z',
          reach: 0,
          engagement: 0,
          clicks: 0
        },
        {
          id: '2',
          title: 'Quick Cooking Tips - Monday Special',
          platforms: ['facebook', 'instagram'],
          status: 'completed',
          scheduledTime: '2024-06-30T12:00:00Z',
          reach: 15400,
          engagement: 8.5,
          clicks: 234
        },
        {
          id: '3',
          title: 'Travel Guide - Tokyo Highlights',
          platforms: ['youtube', 'instagram'],
          status: 'publishing',
          scheduledTime: '2024-06-30T18:00:00Z',
          reach: 2500,
          engagement: 12.3,
          clicks: 89
        }
      ];

      setPlatforms(mockPlatforms);
      setCampaigns(mockCampaigns);
    } catch (error) {
      console.error('Error loading platform data:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const formatNumber = (num: number) => {
    if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
    if (num >= 1000) return (num / 1000).toFixed(1) + 'K';
    return num.toString();
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'bg-green-100 text-green-800';
      case 'paused': return 'bg-gray-100 text-gray-800';
      case 'error': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getCampaignStatusIcon = (status: string) => {
    switch (status) {
      case 'scheduled': return <Clock className="w-4 h-4 text-blue-500" />;
      case 'publishing': return <Play className="w-4 h-4 text-orange-500" />;
      case 'completed': return <CheckCircle className="w-4 h-4 text-green-500" />;
      case 'failed': return <XCircle className="w-4 h-4 text-red-500" />;
      default: return <Clock className="w-4 h-4 text-gray-500" />;
    }
  };

  const PlatformCard = ({ platform }: { platform: Platform }) => (
    <Card className="hover:shadow-lg transition-all duration-200">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className={`${platform.color}`}>
              {platform.icon}
            </div>
            <div>
              <CardTitle className="text-lg">{platform.name}</CardTitle>
              <Badge className={getStatusColor(platform.status)}>
                {platform.status.charAt(0).toUpperCase() + platform.status.slice(1)}
              </Badge>
            </div>
          </div>
          <Button variant="ghost" size="sm">
            <Settings className="w-4 h-4" />
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {platform.connected ? (
            <>
              <div className="grid grid-cols-2 gap-4 text-center">
                <div>
                  <p className="text-2xl font-bold text-gray-900">
                    {formatNumber(platform.followers)}
                  </p>
                  <p className="text-xs text-gray-500">Followers</p>
                </div>
                <div>
                  <p className="text-2xl font-bold text-gray-900">
                    {platform.engagement}%
                  </p>
                  <p className="text-xs text-gray-500">Engagement</p>
                </div>
              </div>

              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">Posts this month</span>
                  <span className="font-medium">{platform.postsThisMonth}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">Last post</span>
                  <span className="font-medium">{platform.lastPost}</span>
                </div>
              </div>

              <div className="flex space-x-2">
                <Button variant="outline" size="sm" className="flex-1">
                  <BarChart3 className="w-4 h-4 mr-2" />
                  Analytics
                </Button>
                <Button variant="outline" size="sm" className="flex-1">
                  <Share2 className="w-4 h-4 mr-2" />
                  Post
                </Button>
              </div>
            </>
          ) : (
            <div className="text-center py-4">
              <Globe className="mx-auto h-8 w-8 text-gray-400 mb-2" />
              <p className="text-sm text-gray-500 mb-4">Not connected</p>
              <Button size="sm" className="w-full">
                Connect {platform.name}
              </Button>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <h1 className="text-3xl font-bold text-gray-900">Multi-Platform</h1>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[1, 2, 3, 4, 5].map((i) => (
            <div key={i} className="animate-pulse">
              <div className="bg-white rounded-lg shadow p-6 space-y-4">
                <div className="flex items-center space-x-3">
                  <div className="w-6 h-6 bg-gray-200 rounded"></div>
                  <div className="space-y-2">
                    <div className="h-4 bg-gray-200 rounded w-20"></div>
                    <div className="h-3 bg-gray-200 rounded w-16"></div>
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div className="h-12 bg-gray-200 rounded"></div>
                  <div className="h-12 bg-gray-200 rounded"></div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  const connectedPlatforms = platforms.filter(p => p.connected);
  const totalFollowers = connectedPlatforms.reduce((sum, p) => sum + p.followers, 0);
  const avgEngagement = connectedPlatforms.length > 0 
    ? connectedPlatforms.reduce((sum, p) => sum + p.engagement, 0) / connectedPlatforms.length 
    : 0;
  const totalPosts = connectedPlatforms.reduce((sum, p) => sum + p.postsThisMonth, 0);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Multi-Platform</h1>
          <p className="text-gray-600 mt-1">Manage all your social media platforms in one place</p>
        </div>
        <Button className="bg-blue-600 hover:bg-blue-700">
          <Plus className="w-4 h-4 mr-2" />
          Create Campaign
        </Button>
      </div>

      {/* Summary Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Connected Platforms</p>
                <p className="text-2xl font-bold text-gray-900">{connectedPlatforms.length}</p>
              </div>
              <Globe className="h-8 w-8 text-blue-600" />
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Followers</p>
                <p className="text-2xl font-bold text-gray-900">{formatNumber(totalFollowers)}</p>
              </div>
              <Users className="h-8 w-8 text-green-600" />
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Avg. Engagement</p>
                <p className="text-2xl font-bold text-gray-900">{avgEngagement.toFixed(1)}%</p>
              </div>
              <TrendingUp className="h-8 w-8 text-purple-600" />
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Posts This Month</p>
                <p className="text-2xl font-bold text-gray-900">{totalPosts}</p>
              </div>
              <Target className="h-8 w-8 text-orange-600" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="campaigns">Campaigns</TabsTrigger>
          <TabsTrigger value="analytics">Analytics</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-6">
          {/* Platforms Grid */}
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Connected Platforms</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {platforms.map((platform) => (
                <PlatformCard key={platform.id} platform={platform} />
              ))}
            </div>
          </div>
        </TabsContent>

        <TabsContent value="campaigns" className="space-y-6">
          <div className="flex justify-between items-center">
            <h3 className="text-lg font-semibold text-gray-900">Recent Campaigns</h3>
            <Button variant="outline">
              <Plus className="w-4 h-4 mr-2" />
              New Campaign
            </Button>
          </div>

          <div className="space-y-4">
            {campaigns.map((campaign) => (
              <Card key={campaign.id}>
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-4">
                      {getCampaignStatusIcon(campaign.status)}
                      <div>
                        <h4 className="font-semibold text-gray-900">{campaign.title}</h4>
                        <div className="flex items-center space-x-2 mt-1">
                          {campaign.platforms.map((platformId) => {
                            const platform = platforms.find(p => p.id === platformId);
                            return platform ? (
                              <div key={platformId} className={`${platform.color}`}>
                                {platform.icon}
                              </div>
                            ) : null;
                          })}
                        </div>
                      </div>
                    </div>
                    <div className="text-right">
                      <Badge className={`${
                        campaign.status === 'completed' ? 'bg-green-100 text-green-800' :
                        campaign.status === 'publishing' ? 'bg-orange-100 text-orange-800' :
                        campaign.status === 'scheduled' ? 'bg-blue-100 text-blue-800' :
                        'bg-red-100 text-red-800'
                      }`}>
                        {campaign.status.charAt(0).toUpperCase() + campaign.status.slice(1)}
                      </Badge>
                      {campaign.status === 'completed' && (
                        <div className="text-sm text-gray-500 mt-1">
                          {formatNumber(campaign.reach)} reach • {campaign.engagement}% engagement
                        </div>
                      )}
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="analytics" className="space-y-6">
          <div className="text-center py-12">
            <BarChart3 className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-semibold text-gray-900">Analytics Dashboard</h3>
            <p className="mt-1 text-sm text-gray-500">
              Detailed analytics and insights coming soon.
            </p>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}