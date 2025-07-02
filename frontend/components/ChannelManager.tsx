import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { 
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  Plus,
  Youtube,
  Settings,
  Trash2,
  Edit,
  Eye,
  EyeOff,
  AlertCircle,
  CheckCircle,
  Activity,
  Mail,
  Key,
  Globe,
  BarChart3,
  RefreshCw,
  Download,
  Upload
} from 'lucide-react';

interface Channel {
  id: string;
  name: string;
  gmail_account: string;
  youtube_channel_id: string;
  youtube_api_key: string;
  channel_description?: string;
  subscriber_count?: number;
  video_count?: number;
  view_count?: number;
  status: 'active' | 'inactive' | 'error';
  api_quota_used?: number;
  api_quota_limit?: number;
  last_activity?: string;
  created_at: string;
  updated_at: string;
}

interface ApiConfig {
  vidiq_api_key: string;
  socialblade_api_key: string;
  tubebuddy_api_key: string;
}

interface ChannelManagerProps {
  className?: string;
}

const ChannelManager: React.FC<ChannelManagerProps> = ({ className = '' }) => {
  const [channels, setChannels] = useState<Channel[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showAddModal, setShowAddModal] = useState(false);
  const [editingChannel, setEditingChannel] = useState<Channel | null>(null);
  const [showApiKeys, setShowApiKeys] = useState<Record<string, boolean>>({});
  const [refreshing, setRefreshing] = useState<Record<string, boolean>>({});

  // Form states
  const [formData, setFormData] = useState({
    name: '',
    gmail_account: '',
    youtube_channel_id: '',
    youtube_api_key: '',
    channel_description: '',
    vidiq_api_key: '',
    socialblade_api_key: '',
    tubebuddy_api_key: ''
  });

  useEffect(() => {
    loadChannels();
  }, []);

  const loadChannels = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/v2/channels');
      if (!response.ok) throw new Error('Failed to load channels');
      
      const data = await response.json();
      setChannels(data.channels || []);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load channels');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const url = editingChannel ? `/api/v2/channels/${editingChannel.id}` : '/api/v2/channels';
      const method = editingChannel ? 'PUT' : 'POST';
      
      const response = await fetch(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || 'Failed to save channel');
      }

      await loadChannels();
      resetForm();
      setShowAddModal(false);
      setEditingChannel(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save channel');
    }
  };

  const handleDelete = async (channelId: string) => {
    if (!confirm('Are you sure you want to delete this channel? This action cannot be undone.')) return;

    try {
      const response = await fetch(`/api/v2/channels/${channelId}`, { method: 'DELETE' });
      if (!response.ok) throw new Error('Failed to delete channel');
      
      await loadChannels();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete channel');
    }
  };

  const handleRefreshStats = async (channelId: string) => {
    try {
      setRefreshing(prev => ({ ...prev, [channelId]: true }));
      
      const response = await fetch(`/api/v2/channels/${channelId}/refresh`, { method: 'POST' });
      if (!response.ok) throw new Error('Failed to refresh channel stats');
      
      await loadChannels();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to refresh stats');
    } finally {
      setRefreshing(prev => ({ ...prev, [channelId]: false }));
    }
  };

  const resetForm = () => {
    setFormData({
      name: '',
      gmail_account: '',
      youtube_channel_id: '',
      youtube_api_key: '',
      channel_description: '',
      vidiq_api_key: '',
      socialblade_api_key: '',
      tubebuddy_api_key: ''
    });
  };

  const openEditModal = (channel: Channel) => {
    setEditingChannel(channel);
    setFormData({
      name: channel.name,
      gmail_account: channel.gmail_account,
      youtube_channel_id: channel.youtube_channel_id,
      youtube_api_key: channel.youtube_api_key,
      channel_description: channel.channel_description || '',
      vidiq_api_key: '',
      socialblade_api_key: '',
      tubebuddy_api_key: ''
    });
    setShowAddModal(true);
  };

  const formatNumber = (num?: number) => {
    if (!num) return '0';
    if (num >= 1000000) return `${(num / 1000000).toFixed(1)}M`;
    if (num >= 1000) return `${(num / 1000).toFixed(1)}K`;
    return num.toString();
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300';
      case 'inactive': return 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-300';
      case 'error': return 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'active': return <CheckCircle className="w-4 h-4" />;
      case 'inactive': return <Activity className="w-4 h-4" />;
      case 'error': return <AlertCircle className="w-4 h-4" />;
      default: return <Activity className="w-4 h-4" />;
    }
  };

  if (loading) {
    return (
      <div className={`space-y-6 ${className}`}>
        <div className="flex items-center gap-2">
          <RefreshCw className="w-5 h-5 animate-spin" />
          <span>Loading channels...</span>
        </div>
      </div>
    );
  }

  return (
    <div className={`space-y-6 ${className}`}>
      {error && (
        <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
          <div className="flex items-center gap-2 text-red-800 dark:text-red-200">
            <AlertCircle className="w-5 h-5" />
            <span>{error}</span>
            <Button 
              variant="ghost" 
              size="sm" 
              onClick={() => setError(null)}
              className="ml-auto"
            >
              ×
            </Button>
          </div>
        </div>
      )}

      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Channel Manager</h2>
          <p className="text-gray-600 dark:text-gray-400">
            Manage your YouTube channels with independent API configurations
          </p>
        </div>
        
        <Dialog open={showAddModal} onOpenChange={setShowAddModal}>
          <DialogTrigger asChild>
            <Button onClick={resetForm} className="flex items-center gap-2">
              <Plus className="w-4 h-4" />
              Add Channel
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
            <DialogHeader>
              <DialogTitle>
                {editingChannel ? 'Edit Channel' : 'Add New Channel'}
              </DialogTitle>
              <DialogDescription>
                Configure a new YouTube channel with its own API settings for independent operation.
              </DialogDescription>
            </DialogHeader>
            
            <form onSubmit={handleSubmit} className="space-y-6">
              <Tabs defaultValue="basic" className="w-full">
                <TabsList className="grid w-full grid-cols-2">
                  <TabsTrigger value="basic">Basic Info</TabsTrigger>
                  <TabsTrigger value="api">API Settings</TabsTrigger>
                </TabsList>
                
                <TabsContent value="basic" className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <Label htmlFor="name">Channel Name *</Label>
                      <Input
                        id="name"
                        value={formData.name}
                        onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
                        placeholder="My YouTube Channel"
                        required
                      />
                    </div>
                    
                    <div>
                      <Label htmlFor="gmail">Gmail Account *</Label>
                      <Input
                        id="gmail"
                        type="email"
                        value={formData.gmail_account}
                        onChange={(e) => setFormData(prev => ({ ...prev, gmail_account: e.target.value }))}
                        placeholder="channel@gmail.com"
                        required
                      />
                    </div>
                  </div>
                  
                  <div>
                    <Label htmlFor="youtube_id">YouTube Channel ID *</Label>
                    <Input
                      id="youtube_id"
                      value={formData.youtube_channel_id}
                      onChange={(e) => setFormData(prev => ({ ...prev, youtube_channel_id: e.target.value }))}
                      placeholder="UCxxxxxxxxxxxxxxxxxxxxxxx"
                      required
                    />
                  </div>
                  
                  <div>
                    <Label htmlFor="description">Channel Description</Label>
                    <Textarea
                      id="description"
                      value={formData.channel_description}
                      onChange={(e) => setFormData(prev => ({ ...prev, channel_description: e.target.value }))}
                      placeholder="Brief description of this channel..."
                      rows={3}
                    />
                  </div>
                </TabsContent>
                
                <TabsContent value="api" className="space-y-4">
                  <div>
                    <Label htmlFor="youtube_api">YouTube API Key *</Label>
                    <Input
                      id="youtube_api"
                      type="password"
                      value={formData.youtube_api_key}
                      onChange={(e) => setFormData(prev => ({ ...prev, youtube_api_key: e.target.value }))}
                      placeholder="AIxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
                      required
                    />
                  </div>
                  
                  <div className="space-y-4">
                    <h4 className="font-medium text-gray-900 dark:text-white">Third-Party Integrations</h4>
                    
                    <div>
                      <Label htmlFor="vidiq_api">VidIQ API Key</Label>
                      <Input
                        id="vidiq_api"
                        type="password"
                        value={formData.vidiq_api_key}
                        onChange={(e) => setFormData(prev => ({ ...prev, vidiq_api_key: e.target.value }))}
                        placeholder="VidIQ API key (optional)"
                      />
                    </div>
                    
                    <div>
                      <Label htmlFor="socialblade_api">Social Blade API Key</Label>
                      <Input
                        id="socialblade_api"
                        type="password"
                        value={formData.socialblade_api_key}
                        onChange={(e) => setFormData(prev => ({ ...prev, socialblade_api_key: e.target.value }))}
                        placeholder="Social Blade API key (optional)"
                      />
                    </div>
                    
                    <div>
                      <Label htmlFor="tubebuddy_api">TubeBuddy API Key</Label>
                      <Input
                        id="tubebuddy_api"
                        type="password"
                        value={formData.tubebuddy_api_key}
                        onChange={(e) => setFormData(prev => ({ ...prev, tubebuddy_api_key: e.target.value }))}
                        placeholder="TubeBuddy API key (optional)"
                      />
                    </div>
                  </div>
                </TabsContent>
              </Tabs>
              
              <div className="flex justify-end gap-2">
                <Button 
                  type="button" 
                  variant="outline" 
                  onClick={() => {
                    setShowAddModal(false);
                    setEditingChannel(null);
                    resetForm();
                  }}
                >
                  Cancel
                </Button>
                <Button type="submit">
                  {editingChannel ? 'Update Channel' : 'Add Channel'}
                </Button>
              </div>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      {/* Channels Grid */}
      {channels.length === 0 ? (
        <Card>
          <CardContent className="text-center py-12">
            <Youtube className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">No Channels Yet</h3>
            <p className="text-gray-600 dark:text-gray-400 mb-4">
              Get started by adding your first YouTube channel
            </p>
            <Button onClick={() => setShowAddModal(true)}>
              <Plus className="w-4 h-4 mr-2" />
              Add Your First Channel
            </Button>
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {channels.map((channel) => (
            <Card key={channel.id} className="hover:shadow-lg transition-shadow">
              <CardHeader className="pb-3">
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-red-100 dark:bg-red-900/20 rounded-full flex items-center justify-center">
                      <Youtube className="w-5 h-5 text-red-600 dark:text-red-400" />
                    </div>
                    <div>
                      <CardTitle className="text-lg">{channel.name}</CardTitle>
                      <div className="flex items-center gap-2 mt-1">
                        <Badge className={getStatusColor(channel.status)}>
                          {getStatusIcon(channel.status)}
                          <span className="ml-1 capitalize">{channel.status}</span>
                        </Badge>
                      </div>
                    </div>
                  </div>
                  
                  <div className="flex items-center gap-1">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleRefreshStats(channel.id)}
                      disabled={refreshing[channel.id]}
                    >
                      <RefreshCw className={`w-4 h-4 ${refreshing[channel.id] ? 'animate-spin' : ''}`} />
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => openEditModal(channel)}
                    >
                      <Edit className="w-4 h-4" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleDelete(channel.id)}
                      className="text-red-600 hover:text-red-700"
                    >
                      <Trash2 className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
              </CardHeader>
              
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
                    <Mail className="w-4 h-4" />
                    <span>{channel.gmail_account}</span>
                  </div>
                  <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
                    <Globe className="w-4 h-4" />
                    <span className="font-mono text-xs">{channel.youtube_channel_id}</span>
                  </div>
                </div>
                
                {/* Channel Stats */}
                <div className="grid grid-cols-3 gap-3 text-center">
                  <div>
                    <div className="text-lg font-bold text-gray-900 dark:text-white">
                      {formatNumber(channel.subscriber_count)}
                    </div>
                    <div className="text-xs text-gray-600 dark:text-gray-400">Subscribers</div>
                  </div>
                  <div>
                    <div className="text-lg font-bold text-gray-900 dark:text-white">
                      {formatNumber(channel.video_count)}
                    </div>
                    <div className="text-xs text-gray-600 dark:text-gray-400">Videos</div>
                  </div>
                  <div>
                    <div className="text-lg font-bold text-gray-900 dark:text-white">
                      {formatNumber(channel.view_count)}
                    </div>
                    <div className="text-xs text-gray-600 dark:text-gray-400">Views</div>
                  </div>
                </div>
                
                {/* API Quota */}
                {channel.api_quota_limit && (
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-600 dark:text-gray-400">API Quota</span>
                      <span className="font-medium">
                        {channel.api_quota_used || 0} / {channel.api_quota_limit}
                      </span>
                    </div>
                    <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                      <div 
                        className="bg-blue-600 h-2 rounded-full transition-all"
                        style={{ 
                          width: `${Math.min(((channel.api_quota_used || 0) / channel.api_quota_limit) * 100, 100)}%` 
                        }}
                      />
                    </div>
                  </div>
                )}
                
                {channel.last_activity && (
                  <div className="text-xs text-gray-500 dark:text-gray-500">
                    Last activity: {new Date(channel.last_activity).toLocaleDateString()}
                  </div>
                )}
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
};

export default ChannelManager;