"use client";

import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  BarChart3, TrendingUp, TrendingDown, Eye, Users, 
  Heart, MessageCircle, Share2, Play, Calendar,
  Download, Filter, RefreshCw, Target, Clock,
  DollarSign, Zap, Award, Globe
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';

interface AnalyticsData {
  totalViews: number;
  totalSubscribers: number;
  totalVideos: number;
  avgWatchTime: string;
  engagement: number;
  revenue: number;
  growth: {
    views: number;
    subscribers: number;
    engagement: number;
    revenue: number;
  };
}

interface ChannelAnalytics {
  channelName: string;
  views: number;
  subscribers: number;
  engagement: number;
  topVideo: string;
  growth: number;
}

interface VideoPerformance {
  id: string;
  title: string;
  views: number;
  likes: number;
  comments: number;
  watchTime: string;
  engagement: number;
  publishedAt: string;
  thumbnail: string;
}

export default function AnalyticsPage() {
  const [analyticsData, setAnalyticsData] = useState<AnalyticsData | null>(null);
  const [channelAnalytics, setChannelAnalytics] = useState<ChannelAnalytics[]>([]);
  const [topVideos, setTopVideos] = useState<VideoPerformance[]>([]);
  const [timeRange, setTimeRange] = useState<'7d' | '30d' | '90d' | '1y'>('30d');
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadAnalyticsData();
  }, [timeRange]);

  const loadAnalyticsData = async () => {
    setIsLoading(true);
    try {
      // Mock data - replace with actual API calls
      const mockAnalytics: AnalyticsData = {
        totalViews: 2847560,
        totalSubscribers: 189500,
        totalVideos: 245,
        avgWatchTime: '4:32',
        engagement: 94.2,
        revenue: 8940,
        growth: {
          views: 15.8,
          subscribers: 12.4,
          engagement: 8.7,
          revenue: 23.5
        }
      };

      const mockChannelAnalytics: ChannelAnalytics[] = [
        {
          channelName: 'Tech Reviews Pro',
          views: 1250000,
          subscribers: 125000,
          engagement: 94.2,
          topVideo: 'Building the Future of AI',
          growth: 15.8
        },
        {
          channelName: 'Cooking Adventures',
          views: 890000,
          subscribers: 89000,
          engagement: 87.5,
          topVideo: '5-Minute Pasta Recipe',
          growth: 8.3
        },
        {
          channelName: 'Travel Vlogs',
          views: 450000,
          subscribers: 45000,
          engagement: 76.8,
          topVideo: 'Hidden Gems in Tokyo',
          growth: -2.1
        }
      ];

      const mockTopVideos: VideoPerformance[] = [
        {
          id: '1',
          title: 'Building the Future of AI - Complete Guide 2024',
          views: 189500,
          likes: 8400,
          comments: 567,
          watchTime: '8:45',
          engagement: 96.8,
          publishedAt: '2024-06-25',
          thumbnail: '/api/placeholder/120/67'
        },
        {
          id: '2',
          title: 'Quick Recipe: 5-Minute Pasta That Will Blow Your Mind',
          views: 156700,
          likes: 7200,
          comments: 432,
          watchTime: '6:30',
          engagement: 94.2,
          publishedAt: '2024-06-24',
          thumbnail: '/api/placeholder/120/67'
        },
        {
          id: '3',
          title: 'The Ultimate Productivity Setup for 2024',
          views: 134500,
          likes: 6800,
          comments: 389,
          watchTime: '7:15',
          engagement: 92.1,
          publishedAt: '2024-06-23',
          thumbnail: '/api/placeholder/120/67'
        }
      ];

      setAnalyticsData(mockAnalytics);
      setChannelAnalytics(mockChannelAnalytics);
      setTopVideos(mockTopVideos);
    } catch (error) {
      console.error('Error loading analytics:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const formatNumber = (num: number) => {
    if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
    if (num >= 1000) return (num / 1000).toFixed(1) + 'K';
    return num.toString();
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount);
  };

  const getGrowthIcon = (growth: number) => {
    return growth >= 0 ? (
      <TrendingUp className="w-4 h-4 text-green-500" />
    ) : (
      <TrendingDown className="w-4 h-4 text-red-500" />
    );
  };

  const getGrowthColor = (growth: number) => {
    return growth >= 0 ? 'text-green-600' : 'text-red-600';
  };

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <h1 className="text-3xl font-bold text-gray-900">Analytics</h1>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="animate-pulse">
              <div className="bg-white rounded-lg shadow p-6 space-y-4">
                <div className="h-4 bg-gray-200 rounded w-1/2"></div>
                <div className="h-8 bg-gray-200 rounded w-3/4"></div>
                <div className="h-3 bg-gray-200 rounded w-1/3"></div>
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  if (!analyticsData) {
    return (
      <div className="text-center py-12">
        <BarChart3 className="mx-auto h-12 w-12 text-gray-400" />
        <h3 className="mt-2 text-sm font-semibold text-gray-900">No analytics data</h3>
        <p className="mt-1 text-sm text-gray-500">Analytics data will appear here once you have content.</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Analytics</h1>
          <p className="text-gray-600 mt-1">Track your performance across all platforms</p>
        </div>
        <div className="flex items-center space-x-2">
          <select
            value={timeRange}
            onChange={(e) => setTimeRange(e.target.value as any)}
            className="px-3 py-2 border rounded-md text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="7d">Last 7 days</option>
            <option value="30d">Last 30 days</option>
            <option value="90d">Last 90 days</option>
            <option value="1y">Last year</option>
          </select>
          <Button variant="outline" size="sm">
            <RefreshCw className="w-4 h-4 mr-2" />
            Refresh
          </Button>
          <Button variant="outline" size="sm">
            <Download className="w-4 h-4 mr-2" />
            Export
          </Button>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0 }}
        >
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Total Views</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {formatNumber(analyticsData.totalViews)}
                  </p>
                  <div className="flex items-center space-x-1 mt-1">
                    {getGrowthIcon(analyticsData.growth.views)}
                    <span className={`text-sm ${getGrowthColor(analyticsData.growth.views)}`}>
                      {analyticsData.growth.views >= 0 ? '+' : ''}{analyticsData.growth.views}%
                    </span>
                  </div>
                </div>
                <Eye className="h-8 w-8 text-blue-600" />
              </div>
            </CardContent>
          </Card>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
        >
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Subscribers</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {formatNumber(analyticsData.totalSubscribers)}
                  </p>
                  <div className="flex items-center space-x-1 mt-1">
                    {getGrowthIcon(analyticsData.growth.subscribers)}
                    <span className={`text-sm ${getGrowthColor(analyticsData.growth.subscribers)}`}>
                      {analyticsData.growth.subscribers >= 0 ? '+' : ''}{analyticsData.growth.subscribers}%
                    </span>
                  </div>
                </div>
                <Users className="h-8 w-8 text-green-600" />
              </div>
            </CardContent>
          </Card>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
        >
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Engagement Rate</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {analyticsData.engagement}%
                  </p>
                  <div className="flex items-center space-x-1 mt-1">
                    {getGrowthIcon(analyticsData.growth.engagement)}
                    <span className={`text-sm ${getGrowthColor(analyticsData.growth.engagement)}`}>
                      {analyticsData.growth.engagement >= 0 ? '+' : ''}{analyticsData.growth.engagement}%
                    </span>
                  </div>
                </div>
                <Heart className="h-8 w-8 text-red-600" />
              </div>
            </CardContent>
          </Card>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
        >
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Revenue</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {formatCurrency(analyticsData.revenue)}
                  </p>
                  <div className="flex items-center space-x-1 mt-1">
                    {getGrowthIcon(analyticsData.growth.revenue)}
                    <span className={`text-sm ${getGrowthColor(analyticsData.growth.revenue)}`}>
                      {analyticsData.growth.revenue >= 0 ? '+' : ''}{analyticsData.growth.revenue}%
                    </span>
                  </div>
                </div>
                <DollarSign className="h-8 w-8 text-yellow-600" />
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </div>

      {/* Tabs */}
      <Tabs defaultValue="overview" className="space-y-6">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="channels">Channels</TabsTrigger>
          <TabsTrigger value="videos">Top Videos</TabsTrigger>
          <TabsTrigger value="realtime">Real-time</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Performance Chart Placeholder */}
            <Card>
              <CardHeader>
                <CardTitle>Performance Over Time</CardTitle>
                <CardDescription>Views, subscribers, and engagement trends</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="h-64 flex items-center justify-center bg-gray-50 rounded-lg">
                  <div className="text-center">
                    <BarChart3 className="mx-auto h-8 w-8 text-gray-400 mb-2" />
                    <p className="text-sm text-gray-500">Chart visualization would go here</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Additional Stats */}
            <Card>
              <CardHeader>
                <CardTitle>Additional Metrics</CardTitle>
                <CardDescription>More detailed performance insights</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Average Watch Time</span>
                  <span className="font-semibold">{analyticsData.avgWatchTime}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Total Videos</span>
                  <span className="font-semibold">{analyticsData.totalVideos}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Views per Video</span>
                  <span className="font-semibold">
                    {formatNumber(Math.round(analyticsData.totalViews / analyticsData.totalVideos))}
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Subscriber Conversion</span>
                  <span className="font-semibold">
                    {((analyticsData.totalSubscribers / analyticsData.totalViews) * 100).toFixed(2)}%
                  </span>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="channels" className="space-y-6">
          <div className="grid gap-6">
            {channelAnalytics.map((channel, index) => (
              <motion.div
                key={channel.channelName}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.1 }}
              >
                <Card>
                  <CardContent className="p-6">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-4">
                        <div className="w-12 h-12 bg-gradient-to-r from-blue-500 to-purple-500 rounded-lg flex items-center justify-center">
                          <span className="text-white font-bold">
                            {channel.channelName.charAt(0)}
                          </span>
                        </div>
                        <div>
                          <h3 className="font-semibold text-lg">{channel.channelName}</h3>
                          <p className="text-sm text-gray-500">Top video: {channel.topVideo}</p>
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="flex items-center space-x-1">
                          {getGrowthIcon(channel.growth)}
                          <span className={`text-sm font-medium ${getGrowthColor(channel.growth)}`}>
                            {channel.growth >= 0 ? '+' : ''}{channel.growth}%
                          </span>
                        </div>
                      </div>
                    </div>
                    <div className="grid grid-cols-3 gap-4 mt-4">
                      <div className="text-center">
                        <p className="text-2xl font-bold text-gray-900">{formatNumber(channel.views)}</p>
                        <p className="text-xs text-gray-500">Views</p>
                      </div>
                      <div className="text-center">
                        <p className="text-2xl font-bold text-gray-900">{formatNumber(channel.subscribers)}</p>
                        <p className="text-xs text-gray-500">Subscribers</p>
                      </div>
                      <div className="text-center">
                        <p className="text-2xl font-bold text-gray-900">{channel.engagement}%</p>
                        <p className="text-xs text-gray-500">Engagement</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="videos" className="space-y-6">
          <div className="space-y-4">
            {topVideos.map((video, index) => (
              <motion.div
                key={video.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
              >
                <Card>
                  <CardContent className="p-6">
                    <div className="flex items-center space-x-4">
                      <div className="w-20 h-12 bg-gray-200 rounded flex items-center justify-center">
                        <Play className="w-6 h-6 text-gray-400" />
                      </div>
                      <div className="flex-1">
                        <h3 className="font-semibold">{video.title}</h3>
                        <p className="text-sm text-gray-500">Published {video.publishedAt}</p>
                      </div>
                      <div className="grid grid-cols-4 gap-6 text-center">
                        <div>
                          <p className="font-bold text-gray-900">{formatNumber(video.views)}</p>
                          <p className="text-xs text-gray-500">Views</p>
                        </div>
                        <div>
                          <p className="font-bold text-gray-900">{formatNumber(video.likes)}</p>
                          <p className="text-xs text-gray-500">Likes</p>
                        </div>
                        <div>
                          <p className="font-bold text-gray-900">{video.comments}</p>
                          <p className="text-xs text-gray-500">Comments</p>
                        </div>
                        <div>
                          <p className="font-bold text-gray-900">{video.engagement}%</p>
                          <p className="text-xs text-gray-500">Engagement</p>
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="realtime" className="space-y-6">
          <div className="text-center py-12">
            <Zap className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-semibold text-gray-900">Real-time Analytics</h3>
            <p className="mt-1 text-sm text-gray-500">
              Live analytics dashboard coming soon.
            </p>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}