'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Avatar, AvatarFallback } from './ui/avatar';
import { Separator } from './ui/separator';
import { Alert, AlertDescription } from './ui/alert';
import { 
  User, 
  Mail, 
  Crown, 
  Calendar, 
  Youtube, 
  ExternalLink,
  Shield,
  Clock,
  CheckCircle,
  XCircle,
  Plus
} from 'lucide-react';
import { useAuth } from './AuthContext';

interface UserProfileProps {
  onClose?: () => void;
}

interface Channel {
  channel_id: string;
  channel_name: string;
  google_channel_id: string;
  is_active: boolean;
}

export const UserProfile: React.FC<UserProfileProps> = ({ onClose }) => {
  const { user, token, logout } = useAuth();
  const [channels, setChannels] = useState<Channel[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://13.60.77.139:8001';

  useEffect(() => {
    if (user && token) {
      fetchChannels();
    }
  }, [user, token]);

  const fetchChannels = async () => {
    setIsLoading(true);
    try {
      const response = await fetch(`${API_BASE}/api/auth/channels`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        setChannels(data.channels || []);
      } else {
        setError('Failed to load channels');
      }
    } catch (error) {
      setError('Network error while loading channels');
    } finally {
      setIsLoading(false);
    }
  };

  const connectGoogleAccount = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/auth/google/authorize`);
      
      if (response.ok) {
        const data = await response.json();
        window.location.href = data.authorization_url;
      } else {
        setError('Failed to initiate Google connection');
      }
    } catch (error) {
      setError('Network error');
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  const getSubscriptionColor = (plan: string) => {
    switch (plan) {
      case 'trial':
        return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300';
      case 'premium':
        return 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300';
      case 'enterprise':
        return 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-300';
      default:
        return 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-300';
    }
  };

  const getRoleIcon = (role: string) => {
    switch (role) {
      case 'admin':
      case 'super_admin':
        return <Shield className="h-4 w-4" />;
      default:
        return <User className="h-4 w-4" />;
    }
  };

  if (!user) {
    return (
      <Card className="w-full max-w-2xl mx-auto">
        <CardContent className="p-6 text-center">
          <p className="text-gray-500">Please log in to view your profile.</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="w-full max-w-4xl mx-auto space-y-6">
      {/* Profile Header */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Avatar className="h-16 w-16">
                <AvatarFallback className="text-lg font-semibold">
                  {user.email.charAt(0).toUpperCase()}
                </AvatarFallback>
              </Avatar>
              <div>
                <CardTitle className="text-2xl">{user.email}</CardTitle>
                <div className="flex items-center space-x-2 mt-2">
                  <Badge className={getSubscriptionColor(user.subscription_plan)}>
                    <Crown className="h-3 w-3 mr-1" />
                    {user.subscription_plan}
                  </Badge>
                  <Badge variant="outline">
                    {getRoleIcon(user.role)}
                    <span className="ml-1 capitalize">{user.role}</span>
                  </Badge>
                </div>
              </div>
            </div>
            {onClose && (
              <Button variant="outline" onClick={onClose}>
                Close
              </Button>
            )}
          </div>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="flex items-center space-x-2">
              <Mail className="h-4 w-4 text-gray-500" />
              <span className="text-sm">{user.email}</span>
            </div>
            <div className="flex items-center space-x-2">
              <Calendar className="h-4 w-4 text-gray-500" />
              <span className="text-sm">Joined {formatDate(user.created_at)}</span>
            </div>
            <div className="flex items-center space-x-2">
              {user.is_active ? (
                <CheckCircle className="h-4 w-4 text-green-500" />
              ) : (
                <XCircle className="h-4 w-4 text-red-500" />
              )}
              <span className="text-sm">
                {user.is_active ? 'Active' : 'Inactive'}
              </span>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* YouTube Channels */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center space-x-2">
              <Youtube className="h-5 w-5 text-red-500" />
              <span>YouTube Channels</span>
            </CardTitle>
            <Button 
              variant="outline" 
              size="sm"
              onClick={connectGoogleAccount}
              disabled={isLoading}
            >
              <Plus className="h-4 w-4 mr-2" />
              Connect Google Account
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          {error && (
            <Alert variant="destructive" className="mb-4">
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          {isLoading ? (
            <div className="text-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
              <p className="text-sm text-gray-500 mt-2">Loading channels...</p>
            </div>
          ) : channels.length > 0 ? (
            <div className="space-y-4">
              {channels.map((channel) => (
                <div 
                  key={channel.channel_id}
                  className="flex items-center justify-between p-4 border rounded-lg"
                >
                  <div className="flex items-center space-x-3">
                    <Youtube className="h-6 w-6 text-red-500" />
                    <div>
                      <h4 className="font-medium">{channel.channel_name || 'Unnamed Channel'}</h4>
                      <p className="text-sm text-gray-500">ID: {channel.channel_id}</p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Badge variant={channel.is_active ? "default" : "secondary"}>
                      {channel.is_active ? 'Active' : 'Inactive'}
                    </Badge>
                    <Button variant="ghost" size="sm">
                      <ExternalLink className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8">
              <Youtube className="h-12 w-12 text-gray-300 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
                No YouTube Channels Connected
              </h3>
              <p className="text-gray-500 mb-4">
                Connect your Google account to access your YouTube channels
              </p>
              <Button onClick={connectGoogleAccount}>
                <Plus className="h-4 w-4 mr-2" />
                Connect Google Account
              </Button>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Account Actions */}
      <Card>
        <CardHeader>
          <CardTitle>Account Actions</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <Button 
              variant="destructive" 
              className="w-full md:w-auto"
              onClick={logout}
            >
              Sign Out
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};