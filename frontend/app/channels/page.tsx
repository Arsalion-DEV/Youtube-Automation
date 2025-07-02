"use client";

import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  Plus, Youtube, Users, TrendingUp, Settings, 
  Play, Pause, MoreVertical, ExternalLink,
  Search, Filter, Grid, List
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';

interface Channel {
  id: string;
  name: string;
  handle: string;
  subscribers: number;
  totalViews: number;
  totalVideos: number;
  status: 'active' | 'paused' | 'setup';
  thumbnail: string;
  platform: 'youtube' | 'tiktok' | 'instagram';
  lastActivity: string;
  monthlyGrowth: number;
}

export default function ChannelsPage() {
  const [channels, setChannels] = useState<Channel[]>([]);
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState<'all' | 'active' | 'paused' | 'setup'>('all');
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadChannels();
  }, []);

  const loadChannels = async () => {
    setIsLoading(true);
    try {
      // Mock data - replace with actual API call
      const mockChannels: Channel[] = [
        {
          id: '1',
          name: 'Tech Reviews Pro',
          handle: '@techreviews',
          subscribers: 125000,
          totalViews: 2500000,
          totalVideos: 89,
          status: 'active',
          thumbnail: '/api/placeholder/120/120',
          platform: 'youtube',
          lastActivity: '2 hours ago',
          monthlyGrowth: 12.5
        },
        {
          id: '2',
          name: 'Cooking Adventures',
          handle: '@cookingfun',
          subscribers: 89000,
          totalViews: 1800000,
          totalVideos: 156,
          status: 'active',
          thumbnail: '/api/placeholder/120/120',
          platform: 'youtube',
          lastActivity: '5 hours ago',
          monthlyGrowth: 8.3
        },
        {
          id: '3',
          name: 'Travel Vlogs',
          handle: '@travelworld',
          subscribers: 45000,
          totalViews: 900000,
          totalVideos: 67,
          status: 'paused',
          thumbnail: '/api/placeholder/120/120',
          platform: 'youtube',
          lastActivity: '2 days ago',
          monthlyGrowth: -2.1
        }
      ];
      setChannels(mockChannels);
    } catch (error) {
      console.error('Error loading channels:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const filteredChannels = channels.filter(channel => {
    const matchesSearch = channel.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         channel.handle.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesFilter = filterStatus === 'all' || channel.status === filterStatus;
    return matchesSearch && matchesFilter;
  });

  const formatNumber = (num: number) => {
    if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
    if (num >= 1000) return (num / 1000).toFixed(1) + 'K';
    return num.toString();
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'bg-green-100 text-green-800';
      case 'paused': return 'bg-yellow-100 text-yellow-800';
      case 'setup': return 'bg-blue-100 text-blue-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const ChannelCard = ({ channel }: { channel: Channel }) => (
    <motion.div
      layout
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className="group"
    >
      <Card className="hover:shadow-lg transition-all duration-200 group-hover:shadow-xl">
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-12 h-12 bg-gradient-to-r from-red-500 to-orange-500 rounded-lg flex items-center justify-center">
                <Youtube className="w-6 h-6 text-white" />
              </div>
              <div>
                <CardTitle className="text-lg">{channel.name}</CardTitle>
                <CardDescription>{channel.handle}</CardDescription>
              </div>
            </div>
            <Button variant="ghost" size="sm">
              <MoreVertical className="w-4 h-4" />
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <Badge className={getStatusColor(channel.status)}>
                {channel.status.charAt(0).toUpperCase() + channel.status.slice(1)}
              </Badge>
              <span className="text-sm text-gray-500">{channel.lastActivity}</span>
            </div>

            <div className="grid grid-cols-3 gap-4 text-center">
              <div>
                <p className="text-2xl font-bold text-gray-900">
                  {formatNumber(channel.subscribers)}
                </p>
                <p className="text-xs text-gray-500">Subscribers</p>
              </div>
              <div>
                <p className="text-2xl font-bold text-gray-900">
                  {formatNumber(channel.totalViews)}
                </p>
                <p className="text-xs text-gray-500">Total Views</p>
              </div>
              <div>
                <p className="text-2xl font-bold text-gray-900">
                  {channel.totalVideos}
                </p>
                <p className="text-xs text-gray-500">Videos</p>
              </div>
            </div>

            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-1">
                <TrendingUp className={`w-4 h-4 ${channel.monthlyGrowth >= 0 ? 'text-green-500' : 'text-red-500'}`} />
                <span className={`text-sm font-medium ${channel.monthlyGrowth >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                  {channel.monthlyGrowth >= 0 ? '+' : ''}{channel.monthlyGrowth}%
                </span>
                <span className="text-sm text-gray-500">this month</span>
              </div>
            </div>

            <div className="flex space-x-2">
              <Button variant="outline" size="sm" className="flex-1">
                <Settings className="w-4 h-4 mr-2" />
                Manage
              </Button>
              <Button variant="outline" size="sm" className="flex-1">
                <ExternalLink className="w-4 h-4 mr-2" />
                View
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <h1 className="text-3xl font-bold text-gray-900">Channels</h1>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[1, 2, 3].map((i) => (
            <div key={i} className="animate-pulse">
              <div className="bg-white rounded-lg shadow p-6 space-y-4">
                <div className="flex items-center space-x-3">
                  <div className="w-12 h-12 bg-gray-200 rounded-lg"></div>
                  <div className="space-y-2">
                    <div className="h-4 bg-gray-200 rounded w-24"></div>
                    <div className="h-3 bg-gray-200 rounded w-16"></div>
                  </div>
                </div>
                <div className="grid grid-cols-3 gap-4">
                  <div className="h-12 bg-gray-200 rounded"></div>
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

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Channels</h1>
          <p className="text-gray-600 mt-1">Manage your YouTube channels and track performance</p>
        </div>
        <Button className="bg-blue-600 hover:bg-blue-700">
          <Plus className="w-4 h-4 mr-2" />
          Add Channel
        </Button>
      </div>

      {/* Filters and Search */}
      <div className="flex flex-col sm:flex-row gap-4 bg-white p-4 rounded-lg shadow-sm border">
        <div className="flex-1">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
            <Input
              placeholder="Search channels..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10"
            />
          </div>
        </div>
        <div className="flex items-center space-x-2">
          <select
            value={filterStatus}
            onChange={(e) => setFilterStatus(e.target.value as any)}
            className="px-3 py-2 border rounded-md text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="all">All Statuses</option>
            <option value="active">Active</option>
            <option value="paused">Paused</option>
            <option value="setup">Setup</option>
          </select>
          <div className="flex border rounded-md">
            <Button
              variant={viewMode === 'grid' ? 'default' : 'ghost'}
              size="sm"
              onClick={() => setViewMode('grid')}
              className="rounded-r-none"
            >
              <Grid className="w-4 h-4" />
            </Button>
            <Button
              variant={viewMode === 'list' ? 'default' : 'ghost'}
              size="sm"
              onClick={() => setViewMode('list')}
              className="rounded-l-none"
            >
              <List className="w-4 h-4" />
            </Button>
          </div>
        </div>
      </div>

      {/* Channels Grid */}
      {filteredChannels.length === 0 ? (
        <div className="text-center py-12">
          <Youtube className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-semibold text-gray-900">No channels found</h3>
          <p className="mt-1 text-sm text-gray-500">
            {searchTerm ? 'Try adjusting your search criteria.' : 'Get started by adding your first channel.'}
          </p>
          {!searchTerm && (
            <div className="mt-6">
              <Button className="bg-blue-600 hover:bg-blue-700">
                <Plus className="w-4 h-4 mr-2" />
                Add Channel
              </Button>
            </div>
          )}
        </div>
      ) : (
        <motion.div
          layout
          className={`grid gap-6 ${
            viewMode === 'grid' 
              ? 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3' 
              : 'grid-cols-1'
          }`}
        >
          {filteredChannels.map((channel) => (
            <ChannelCard key={channel.id} channel={channel} />
          ))}
        </motion.div>
      )}
    </div>
  );
}