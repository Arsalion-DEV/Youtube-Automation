"""
Advanced Team Management Dashboard
React component for comprehensive team collaboration and management
"""

import React, { useState, useEffect } from 'react';
import { 
  Users, 
  UserPlus, 
  Settings, 
  Crown, 
  Shield, 
  Eye, 
  Edit3, 
  Trash2,
  Mail,
  Activity,
  TrendingUp,
  MessageSquare,
  MoreHorizontal,
  CheckCircle,
  Clock,
  AlertTriangle
} from 'lucide-react';

interface TeamMember {
  id: string;
  user_id: string;
  email: string;
  full_name: string;
  role: string;
  permissions: string[];
  joined_at: string;
  last_activity: string;
  is_active: boolean;
}

interface TeamInvitation {
  id: string;
  email: string;
  role: string;
  invited_by: string;
  created_at: string;
  expires_at: string;
  status: 'pending' | 'accepted' | 'expired';
}

interface TeamAnalytics {
  overview: {
    total_videos_created: number;
    total_views: number;
    total_revenue: number;
    team_productivity_score: number;
  };
  member_performance: Array<{
    user_id: string;
    name: string;
    role: string;
    videos_created: number;
    total_views: number;
    productivity_score: number;
  }>;
  collaboration_metrics: {
    shared_projects: number;
    team_communication_score: number;
  };
}

interface Activity {
  id: string;
  type: string;
  user_name: string;
  description: string;
  timestamp: string;
  metadata?: any;
}

const TeamManagementDashboard: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'overview' | 'members' | 'invitations' | 'analytics' | 'settings'>('overview');
  const [members, setMembers] = useState<TeamMember[]>([]);
  const [invitations, setInvitations] = useState<TeamInvitation[]>([]);
  const [analytics, setAnalytics] = useState<TeamAnalytics | null>(null);
  const [activities, setActivities] = useState<Activity[]>([]);
  const [showInviteModal, setShowInviteModal] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadTeamData();
  }, []);

  const loadTeamData = async () => {
    try {
      setLoading(true);
      
      // Load team members, analytics, and activities
      const [membersResponse, analyticsResponse, activitiesResponse] = await Promise.all([
        fetch('/api/v3/teams/team-123/members'),
        fetch('/api/v3/teams/team-123/analytics'),
        fetch('/api/v3/teams/team-123/activity')
      ]);

      const membersData = await membersResponse.json();
      const analyticsData = await analyticsResponse.json();
      const activitiesData = await activitiesResponse.json();

      setMembers(membersData.members || []);
      setAnalytics(analyticsData.insights || null);
      setActivities(activitiesData.activity || []);
    } catch (error) {
      console.error('Error loading team data:', error);
    } finally {
      setLoading(false);
    }
  };

  const getRoleIcon = (role: string) => {
    switch (role.toLowerCase()) {
      case 'owner': return <Crown className="w-4 h-4 text-yellow-500" />;
      case 'admin': return <Shield className="w-4 h-4 text-red-500" />;
      case 'manager': return <Settings className="w-4 h-4 text-blue-500" />;
      case 'editor': return <Edit3 className="w-4 h-4 text-green-500" />;
      case 'viewer': return <Eye className="w-4 h-4 text-gray-500" />;
      default: return <Users className="w-4 h-4 text-gray-400" />;
    }
  };

  const getRoleBadgeColor = (role: string) => {
    switch (role.toLowerCase()) {
      case 'owner': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'admin': return 'bg-red-100 text-red-800 border-red-200';
      case 'manager': return 'bg-blue-100 text-blue-800 border-blue-200';
      case 'editor': return 'bg-green-100 text-green-800 border-green-200';
      case 'viewer': return 'bg-gray-100 text-gray-800 border-gray-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const InviteMemberModal: React.FC = () => {
    const [email, setEmail] = useState('');
    const [role, setRole] = useState('editor');
    const [message, setMessage] = useState('');
    const [sending, setSending] = useState(false);

    const handleInvite = async () => {
      try {
        setSending(true);
        
        const response = await fetch('/api/v3/teams/team-123/invitations', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            email,
            role,
            message: message || undefined
          })
        });

        if (response.ok) {
          setShowInviteModal(false);
          setEmail('');
          setRole('editor');
          setMessage('');
          loadTeamData(); // Refresh data
        }
      } catch (error) {
        console.error('Error sending invitation:', error);
      } finally {
        setSending(false);
      }
    };

    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white rounded-lg p-6 w-full max-w-md">
          <h3 className="text-lg font-semibold mb-4">Invite Team Member</h3>
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Email Address
              </label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="colleague@company.com"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Role
              </label>
              <select
                value={role}
                onChange={(e) => setRole(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="viewer">Viewer</option>
                <option value="editor">Editor</option>
                <option value="manager">Manager</option>
                <option value="admin">Admin</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Personal Message (Optional)
              </label>
              <textarea
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                rows={3}
                placeholder="Welcome to our team! Looking forward to collaborating with you."
              />
            </div>
          </div>

          <div className="flex gap-3 mt-6">
            <button
              onClick={() => setShowInviteModal(false)}
              className="flex-1 px-4 py-2 text-gray-700 border border-gray-300 rounded-md hover:bg-gray-50"
              disabled={sending}
            >
              Cancel
            </button>
            <button
              onClick={handleInvite}
              disabled={!email || sending}
              className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 flex items-center justify-center gap-2"
            >
              {sending ? (
                <>
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  Sending...
                </>
              ) : (
                <>
                  <Mail className="w-4 h-4" />
                  Send Invitation
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    );
  };

  const OverviewTab: React.FC = () => (
    <div className="space-y-6">
      {/* Team Stats */}
      {analytics && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <div className="bg-white p-6 rounded-lg border border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Videos</p>
                <p className="text-2xl font-bold text-gray-900">
                  {analytics.overview.total_videos_created.toLocaleString()}
                </p>
              </div>
              <div className="p-3 bg-blue-50 rounded-lg">
                <Activity className="w-6 h-6 text-blue-600" />
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg border border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Views</p>
                <p className="text-2xl font-bold text-gray-900">
                  {(analytics.overview.total_views / 1000000).toFixed(1)}M
                </p>
              </div>
              <div className="p-3 bg-green-50 rounded-lg">
                <TrendingUp className="w-6 h-6 text-green-600" />
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg border border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Team Revenue</p>
                <p className="text-2xl font-bold text-gray-900">
                  ${analytics.overview.total_revenue.toLocaleString()}
                </p>
              </div>
              <div className="p-3 bg-yellow-50 rounded-lg">
                <TrendingUp className="w-6 h-6 text-yellow-600" />
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg border border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Productivity</p>
                <p className="text-2xl font-bold text-gray-900">
                  {analytics.overview.team_productivity_score.toFixed(1)}%
                </p>
              </div>
              <div className="p-3 bg-purple-50 rounded-lg">
                <Users className="w-6 h-6 text-purple-600" />
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Recent Activity */}
      <div className="bg-white rounded-lg border border-gray-200">
        <div className="p-6 border-b border-gray-200">
          <h3 className="text-lg font-semibold">Recent Activity</h3>
        </div>
        <div className="p-6">
          <div className="space-y-4">
            {activities.slice(0, 5).map((activity) => (
              <div key={activity.id} className="flex items-start gap-3">
                <div className="p-2 bg-gray-100 rounded-lg">
                  <Activity className="w-4 h-4 text-gray-600" />
                </div>
                <div className="flex-1">
                  <p className="text-sm font-medium text-gray-900">{activity.user_name}</p>
                  <p className="text-sm text-gray-600">{activity.description}</p>
                  <p className="text-xs text-gray-500 mt-1">
                    {new Date(activity.timestamp).toLocaleDateString()} at{' '}
                    {new Date(activity.timestamp).toLocaleTimeString()}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );

  const MembersTab: React.FC = () => (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h3 className="text-lg font-semibold">Team Members ({members.length})</h3>
        <button
          onClick={() => setShowInviteModal(true)}
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          <UserPlus className="w-4 h-4" />
          Invite Member
        </button>
      </div>

      <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr>
                <th className="text-left px-6 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Member
                </th>
                <th className="text-left px-6 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Role
                </th>
                <th className="text-left px-6 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Last Activity
                </th>
                <th className="text-left px-6 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="text-right px-6 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {members.map((member) => (
                <tr key={member.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4">
                    <div className="flex items-center">
                      <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
                        <span className="text-sm font-medium text-blue-600">
                          {member.full_name.split(' ').map(n => n[0]).join('').toUpperCase()}
                        </span>
                      </div>
                      <div className="ml-4">
                        <div className="text-sm font-medium text-gray-900">{member.full_name}</div>
                        <div className="text-sm text-gray-500">{member.email}</div>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-2">
                      {getRoleIcon(member.role)}
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${getRoleBadgeColor(member.role)}`}>
                        {member.role}
                      </span>
                    </div>
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-500">
                    {new Date(member.last_activity).toLocaleDateString()}
                  </td>
                  <td className="px-6 py-4">
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                      member.is_active 
                        ? 'bg-green-100 text-green-800 border border-green-200' 
                        : 'bg-gray-100 text-gray-800 border border-gray-200'
                    }`}>
                      {member.is_active ? 'Active' : 'Inactive'}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-right">
                    <button className="p-2 text-gray-400 hover:text-gray-600">
                      <MoreHorizontal className="w-4 h-4" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );

  const AnalyticsTab: React.FC = () => (
    <div className="space-y-6">
      {analytics && (
        <>
          {/* Member Performance */}
          <div className="bg-white rounded-lg border border-gray-200">
            <div className="p-6 border-b border-gray-200">
              <h3 className="text-lg font-semibold">Member Performance</h3>
            </div>
            <div className="p-6">
              <div className="grid gap-4">
                {analytics.member_performance.map((member) => (
                  <div key={member.user_id} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
                        <span className="text-sm font-medium text-blue-600">
                          {member.name.split(' ').map(n => n[0]).join('').toUpperCase()}
                        </span>
                      </div>
                      <div>
                        <div className="font-medium text-gray-900">{member.name}</div>
                        <div className="text-sm text-gray-500">{member.role}</div>
                      </div>
                    </div>
                    <div className="flex gap-6 text-sm">
                      <div className="text-center">
                        <div className="font-medium text-gray-900">{member.videos_created}</div>
                        <div className="text-gray-500">Videos</div>
                      </div>
                      <div className="text-center">
                        <div className="font-medium text-gray-900">{(member.total_views / 1000).toFixed(0)}K</div>
                        <div className="text-gray-500">Views</div>
                      </div>
                      <div className="text-center">
                        <div className="font-medium text-gray-900">{member.productivity_score.toFixed(1)}%</div>
                        <div className="text-gray-500">Score</div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Collaboration Metrics */}
          <div className="bg-white rounded-lg border border-gray-200">
            <div className="p-6 border-b border-gray-200">
              <h3 className="text-lg font-semibold">Collaboration Metrics</h3>
            </div>
            <div className="p-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="text-center">
                  <div className="text-3xl font-bold text-blue-600 mb-2">
                    {analytics.collaboration_metrics.shared_projects}
                  </div>
                  <div className="text-sm text-gray-600">Shared Projects</div>
                </div>
                <div className="text-center">
                  <div className="text-3xl font-bold text-green-600 mb-2">
                    {analytics.collaboration_metrics.team_communication_score.toFixed(1)}%
                  </div>
                  <div className="text-sm text-gray-600">Communication Score</div>
                </div>
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Team Management</h1>
          <p className="text-gray-600">Manage your team members, roles, and collaboration</p>
        </div>
        <div className="flex items-center gap-3">
          <button className="flex items-center gap-2 px-4 py-2 text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50">
            <Settings className="w-4 h-4" />
            Settings
          </button>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          {[
            { id: 'overview', label: 'Overview', icon: Activity },
            { id: 'members', label: 'Members', icon: Users },
            { id: 'analytics', label: 'Analytics', icon: TrendingUp },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`flex items-center gap-2 py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === tab.id
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <tab.icon className="w-4 h-4" />
              {tab.label}
            </button>
          ))}
        </nav>
      </div>

      {/* Tab Content */}
      {activeTab === 'overview' && <OverviewTab />}
      {activeTab === 'members' && <MembersTab />}
      {activeTab === 'analytics' && <AnalyticsTab />}

      {/* Invite Modal */}
      {showInviteModal && <InviteMemberModal />}
    </div>
  );
};

export default TeamManagementDashboard;