"""
Advanced Team Management System
Enhanced collaboration, role-based permissions, and team analytics
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional, Set
from datetime import datetime, timedelta
from enum import Enum
import uuid
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)

class TeamRole(Enum):
    """Team roles with hierarchical permissions"""
    OWNER = "owner"
    ADMIN = "admin"
    MANAGER = "manager"
    EDITOR = "editor"
    VIEWER = "viewer"
    GUEST = "guest"

class Permission(Enum):
    """Granular permissions for team members"""
    # Content permissions
    CREATE_VIDEOS = "create_videos"
    EDIT_VIDEOS = "edit_videos"
    DELETE_VIDEOS = "delete_videos"
    PUBLISH_VIDEOS = "publish_videos"
    
    # Channel permissions
    MANAGE_CHANNELS = "manage_channels"
    VIEW_ANALYTICS = "view_analytics"
    EXPORT_DATA = "export_data"
    
    # Team permissions
    INVITE_MEMBERS = "invite_members"
    REMOVE_MEMBERS = "remove_members"
    MANAGE_ROLES = "manage_roles"
    VIEW_TEAM_ANALYTICS = "view_team_analytics"
    
    # Admin permissions
    MANAGE_BILLING = "manage_billing"
    MANAGE_INTEGRATIONS = "manage_integrations"
    ACCESS_LOGS = "access_logs"
    MANAGE_SETTINGS = "manage_settings"
    
    # A/B Testing permissions
    CREATE_AB_TESTS = "create_ab_tests"
    VIEW_AB_RESULTS = "view_ab_results"
    MANAGE_AB_TESTS = "manage_ab_tests"
    
    # White Label permissions
    MANAGE_BRANDING = "manage_branding"
    CONFIGURE_WHITE_LABEL = "configure_white_label"

@dataclass
class TeamMember:
    """Team member data structure"""
    id: str
    user_id: str
    team_id: str
    email: str
    full_name: str
    role: TeamRole
    permissions: Set[Permission]
    joined_at: datetime
    last_activity: datetime
    is_active: bool
    invitation_token: Optional[str] = None
    notes: Optional[str] = None

@dataclass
class Team:
    """Team data structure"""
    id: str
    name: str
    description: str
    organization_id: str
    owner_id: str
    created_at: datetime
    updated_at: datetime
    settings: Dict[str, Any]
    member_count: int
    is_active: bool

@dataclass
class TeamInvitation:
    """Team invitation data structure"""
    id: str
    team_id: str
    email: str
    role: TeamRole
    permissions: Set[Permission]
    invited_by: str
    created_at: datetime
    expires_at: datetime
    token: str
    is_used: bool
    message: Optional[str] = None

class TeamPermissionManager:
    """Manages role-based permissions"""
    
    # Default permission sets for each role
    ROLE_PERMISSIONS = {
        TeamRole.OWNER: {
            Permission.CREATE_VIDEOS, Permission.EDIT_VIDEOS, Permission.DELETE_VIDEOS, Permission.PUBLISH_VIDEOS,
            Permission.MANAGE_CHANNELS, Permission.VIEW_ANALYTICS, Permission.EXPORT_DATA,
            Permission.INVITE_MEMBERS, Permission.REMOVE_MEMBERS, Permission.MANAGE_ROLES, Permission.VIEW_TEAM_ANALYTICS,
            Permission.MANAGE_BILLING, Permission.MANAGE_INTEGRATIONS, Permission.ACCESS_LOGS, Permission.MANAGE_SETTINGS,
            Permission.CREATE_AB_TESTS, Permission.VIEW_AB_RESULTS, Permission.MANAGE_AB_TESTS,
            Permission.MANAGE_BRANDING, Permission.CONFIGURE_WHITE_LABEL
        },
        TeamRole.ADMIN: {
            Permission.CREATE_VIDEOS, Permission.EDIT_VIDEOS, Permission.DELETE_VIDEOS, Permission.PUBLISH_VIDEOS,
            Permission.MANAGE_CHANNELS, Permission.VIEW_ANALYTICS, Permission.EXPORT_DATA,
            Permission.INVITE_MEMBERS, Permission.REMOVE_MEMBERS, Permission.MANAGE_ROLES, Permission.VIEW_TEAM_ANALYTICS,
            Permission.MANAGE_INTEGRATIONS, Permission.ACCESS_LOGS, Permission.MANAGE_SETTINGS,
            Permission.CREATE_AB_TESTS, Permission.VIEW_AB_RESULTS, Permission.MANAGE_AB_TESTS
        },
        TeamRole.MANAGER: {
            Permission.CREATE_VIDEOS, Permission.EDIT_VIDEOS, Permission.DELETE_VIDEOS, Permission.PUBLISH_VIDEOS,
            Permission.MANAGE_CHANNELS, Permission.VIEW_ANALYTICS, Permission.EXPORT_DATA,
            Permission.INVITE_MEMBERS, Permission.VIEW_TEAM_ANALYTICS,
            Permission.CREATE_AB_TESTS, Permission.VIEW_AB_RESULTS
        },
        TeamRole.EDITOR: {
            Permission.CREATE_VIDEOS, Permission.EDIT_VIDEOS, Permission.PUBLISH_VIDEOS,
            Permission.VIEW_ANALYTICS, Permission.EXPORT_DATA,
            Permission.VIEW_AB_RESULTS
        },
        TeamRole.VIEWER: {
            Permission.VIEW_ANALYTICS
        },
        TeamRole.GUEST: set()  # No default permissions
    }
    
    @classmethod
    def get_default_permissions(cls, role: TeamRole) -> Set[Permission]:
        """Get default permissions for a role"""
        return cls.ROLE_PERMISSIONS.get(role, set()).copy()
    
    @classmethod
    def can_manage_member(cls, manager_role: TeamRole, target_role: TeamRole) -> bool:
        """Check if a role can manage another role"""
        role_hierarchy = {
            TeamRole.OWNER: 5,
            TeamRole.ADMIN: 4,
            TeamRole.MANAGER: 3,
            TeamRole.EDITOR: 2,
            TeamRole.VIEWER: 1,
            TeamRole.GUEST: 0
        }
        
        return role_hierarchy.get(manager_role, 0) > role_hierarchy.get(target_role, 0)
    
    @classmethod
    def validate_permissions(cls, role: TeamRole, permissions: Set[Permission]) -> Set[Permission]:
        """Validate and filter permissions based on role"""
        allowed_permissions = cls.get_default_permissions(role)
        return permissions.intersection(allowed_permissions)

class TeamAnalytics:
    """Team performance and collaboration analytics"""
    
    async def get_team_performance(self, team_id: str, period: str = "30d") -> Dict[str, Any]:
        """Get comprehensive team performance metrics"""
        try:
            # Mock analytics data - in real implementation, query from database
            return {
                "team_id": team_id,
                "period": period,
                "overview": {
                    "total_videos_created": 156,
                    "total_views": 2450000,
                    "total_revenue": 8750.50,
                    "average_engagement_rate": 7.8,
                    "team_productivity_score": 87.5
                },
                "member_performance": [
                    {
                        "user_id": "user1",
                        "name": "Sarah Johnson",
                        "role": "editor",
                        "videos_created": 45,
                        "total_views": 850000,
                        "avg_engagement": 8.2,
                        "productivity_score": 92.1
                    },
                    {
                        "user_id": "user2", 
                        "name": "Mike Chen",
                        "role": "manager",
                        "videos_created": 38,
                        "total_views": 720000,
                        "avg_engagement": 7.5,
                        "productivity_score": 88.3
                    }
                ],
                "collaboration_metrics": {
                    "shared_projects": 23,
                    "cross_team_reviews": 67,
                    "knowledge_sharing_sessions": 12,
                    "team_communication_score": 91.2
                },
                "content_performance": {
                    "top_performing_categories": ["Tech Reviews", "Tutorials", "Gaming"],
                    "best_publishing_times": ["Tuesday 2PM", "Thursday 10AM", "Sunday 7PM"],
                    "content_diversity_score": 78.5
                },
                "growth_trends": {
                    "subscriber_growth": 15.2,  # percentage
                    "view_growth": 23.1,
                    "engagement_growth": 8.7,
                    "revenue_growth": 18.9
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting team performance: {e}")
            return {}
    
    async def get_collaboration_insights(self, team_id: str) -> Dict[str, Any]:
        """Get team collaboration insights"""
        try:
            return {
                "team_id": team_id,
                "collaboration_score": 89.4,
                "communication_patterns": {
                    "most_active_hours": ["9-11 AM", "2-4 PM"],
                    "avg_response_time": "2.3 hours",
                    "message_volume": 1247,
                    "video_calls": 23
                },
                "knowledge_sharing": {
                    "documents_shared": 156,
                    "templates_created": 34,
                    "best_practices_documented": 78,
                    "training_sessions": 12
                },
                "workflow_efficiency": {
                    "avg_project_completion_time": "4.2 days",
                    "bottleneck_identification": [
                        "Video review process",
                        "Asset approval"
                    ],
                    "automation_opportunities": [
                        "Thumbnail generation",
                        "Description templates"
                    ]
                },
                "team_health": {
                    "satisfaction_score": 8.6,
                    "workload_balance": 85.2,
                    "skill_development": 91.7,
                    "burnout_risk": "low"
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting collaboration insights: {e}")
            return {}

class TeamManagementSystem:
    """Advanced team management with enterprise features"""
    
    def __init__(self):
        self.permission_manager = TeamPermissionManager()
        self.analytics = TeamAnalytics()
        
        # In-memory storage for demo - replace with database
        self.teams: Dict[str, Team] = {}
        self.members: Dict[str, TeamMember] = {}
        self.invitations: Dict[str, TeamInvitation] = {}
    
    async def create_team(
        self,
        name: str,
        description: str,
        organization_id: str,
        owner_id: str,
        settings: Optional[Dict[str, Any]] = None
    ) -> str:
        """Create a new team"""
        try:
            team_id = str(uuid.uuid4())
            
            team = Team(
                id=team_id,
                name=name,
                description=description,
                organization_id=organization_id,
                owner_id=owner_id,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                settings=settings or self._get_default_team_settings(),
                member_count=1,
                is_active=True
            )
            
            self.teams[team_id] = team
            
            # Add owner as first team member
            await self.add_team_member(
                team_id=team_id,
                user_id=owner_id,
                email="owner@example.com",  # In real implementation, get from user data
                full_name="Team Owner",
                role=TeamRole.OWNER,
                invited_by=owner_id
            )
            
            logger.info(f"Team created: {team_id} - {name}")
            return team_id
            
        except Exception as e:
            logger.error(f"Error creating team: {e}")
            raise e
    
    async def add_team_member(
        self,
        team_id: str,
        user_id: str,
        email: str,
        full_name: str,
        role: TeamRole,
        invited_by: str,
        custom_permissions: Optional[Set[Permission]] = None
    ) -> str:
        """Add a member to the team"""
        try:
            member_id = str(uuid.uuid4())
            
            # Get permissions
            if custom_permissions:
                permissions = self.permission_manager.validate_permissions(role, custom_permissions)
            else:
                permissions = self.permission_manager.get_default_permissions(role)
            
            member = TeamMember(
                id=member_id,
                user_id=user_id,
                team_id=team_id,
                email=email,
                full_name=full_name,
                role=role,
                permissions=permissions,
                joined_at=datetime.utcnow(),
                last_activity=datetime.utcnow(),
                is_active=True
            )
            
            self.members[member_id] = member
            
            # Update team member count
            if team_id in self.teams:
                self.teams[team_id].member_count += 1
                self.teams[team_id].updated_at = datetime.utcnow()
            
            logger.info(f"Team member added: {member_id} to team {team_id}")
            return member_id
            
        except Exception as e:
            logger.error(f"Error adding team member: {e}")
            raise e
    
    async def invite_team_member(
        self,
        team_id: str,
        email: str,
        role: TeamRole,
        invited_by: str,
        message: Optional[str] = None,
        custom_permissions: Optional[Set[Permission]] = None
    ) -> str:
        """Invite a new member to the team"""
        try:
            invitation_id = str(uuid.uuid4())
            token = str(uuid.uuid4())
            
            permissions = custom_permissions or self.permission_manager.get_default_permissions(role)
            
            invitation = TeamInvitation(
                id=invitation_id,
                team_id=team_id,
                email=email,
                role=role,
                permissions=permissions,
                invited_by=invited_by,
                created_at=datetime.utcnow(),
                expires_at=datetime.utcnow() + timedelta(days=7),  # 7 days to accept
                token=token,
                is_used=False,
                message=message
            )
            
            self.invitations[invitation_id] = invitation
            
            # In real implementation, send invitation email here
            await self._send_invitation_email(invitation)
            
            logger.info(f"Team invitation sent: {invitation_id} to {email}")
            return invitation_id
            
        except Exception as e:
            logger.error(f"Error sending team invitation: {e}")
            raise e
    
    async def accept_invitation(self, token: str, user_id: str, full_name: str) -> str:
        """Accept a team invitation"""
        try:
            # Find invitation by token
            invitation = None
            for inv in self.invitations.values():
                if inv.token == token and not inv.is_used:
                    invitation = inv
                    break
            
            if not invitation:
                raise ValueError("Invalid or expired invitation token")
            
            if datetime.utcnow() > invitation.expires_at:
                raise ValueError("Invitation has expired")
            
            # Add user to team
            member_id = await self.add_team_member(
                team_id=invitation.team_id,
                user_id=user_id,
                email=invitation.email,
                full_name=full_name,
                role=invitation.role,
                invited_by=invitation.invited_by,
                custom_permissions=invitation.permissions
            )
            
            # Mark invitation as used
            invitation.is_used = True
            
            logger.info(f"Team invitation accepted: {invitation.id} by {user_id}")
            return member_id
            
        except Exception as e:
            logger.error(f"Error accepting team invitation: {e}")
            raise e
    
    async def update_member_role(
        self,
        team_id: str,
        member_id: str,
        new_role: TeamRole,
        updated_by: str,
        custom_permissions: Optional[Set[Permission]] = None
    ) -> bool:
        """Update a team member's role and permissions"""
        try:
            if member_id not in self.members:
                return False
            
            member = self.members[member_id]
            updater = await self.get_team_member_by_user_id(team_id, updated_by)
            
            if not updater:
                raise ValueError("Updater not found in team")
            
            # Check if updater can manage this member
            if not self.permission_manager.can_manage_member(updater.role, member.role):
                raise ValueError("Insufficient permissions to update this member")
            
            # Update role and permissions
            member.role = new_role
            if custom_permissions:
                member.permissions = self.permission_manager.validate_permissions(new_role, custom_permissions)
            else:
                member.permissions = self.permission_manager.get_default_permissions(new_role)
            
            logger.info(f"Member role updated: {member_id} to {new_role.value}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating member role: {e}")
            raise e
    
    async def remove_team_member(
        self,
        team_id: str,
        member_id: str,
        removed_by: str
    ) -> bool:
        """Remove a member from the team"""
        try:
            if member_id not in self.members:
                return False
            
            member = self.members[member_id]
            remover = await self.get_team_member_by_user_id(team_id, removed_by)
            
            if not remover:
                raise ValueError("Remover not found in team")
            
            # Check permissions
            if not self.permission_manager.can_manage_member(remover.role, member.role):
                raise ValueError("Insufficient permissions to remove this member")
            
            # Cannot remove team owner
            if member.role == TeamRole.OWNER:
                raise ValueError("Cannot remove team owner")
            
            # Remove member
            del self.members[member_id]
            
            # Update team member count
            if team_id in self.teams:
                self.teams[team_id].member_count -= 1
                self.teams[team_id].updated_at = datetime.utcnow()
            
            logger.info(f"Team member removed: {member_id} from team {team_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error removing team member: {e}")
            raise e
    
    async def get_team_members(self, team_id: str) -> List[Dict[str, Any]]:
        """Get all team members"""
        try:
            members = []
            for member in self.members.values():
                if member.team_id == team_id and member.is_active:
                    member_data = asdict(member)
                    member_data['role'] = member.role.value
                    member_data['permissions'] = [p.value for p in member.permissions]
                    member_data['joined_at'] = member.joined_at.isoformat()
                    member_data['last_activity'] = member.last_activity.isoformat()
                    members.append(member_data)
            
            return sorted(members, key=lambda x: x['joined_at'])
            
        except Exception as e:
            logger.error(f"Error getting team members: {e}")
            return []
    
    async def get_team_member_by_user_id(self, team_id: str, user_id: str) -> Optional[TeamMember]:
        """Get team member by user ID"""
        for member in self.members.values():
            if member.team_id == team_id and member.user_id == user_id and member.is_active:
                return member
        return None
    
    async def check_permission(self, team_id: str, user_id: str, permission: Permission) -> bool:
        """Check if a user has a specific permission in the team"""
        try:
            member = await self.get_team_member_by_user_id(team_id, user_id)
            if not member:
                return False
            
            return permission in member.permissions
            
        except Exception as e:
            logger.error(f"Error checking permission: {e}")
            return False
    
    async def get_user_teams(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all teams for a user"""
        try:
            user_teams = []
            
            for member in self.members.values():
                if member.user_id == user_id and member.is_active:
                    team = self.teams.get(member.team_id)
                    if team:
                        team_data = {
                            "team_id": team.id,
                            "name": team.name,
                            "description": team.description,
                            "role": member.role.value,
                            "permissions": [p.value for p in member.permissions],
                            "member_count": team.member_count,
                            "joined_at": member.joined_at.isoformat()
                        }
                        user_teams.append(team_data)
            
            return sorted(user_teams, key=lambda x: x['joined_at'], reverse=True)
            
        except Exception as e:
            logger.error(f"Error getting user teams: {e}")
            return []
    
    async def get_team_activity_feed(self, team_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get team activity feed"""
        try:
            # Mock activity data - in real implementation, query from activity log
            activities = [
                {
                    "id": str(uuid.uuid4()),
                    "type": "video_created",
                    "user_name": "Sarah Johnson",
                    "description": "Created new video: 'AI in 2024: Complete Guide'",
                    "timestamp": (datetime.utcnow() - timedelta(hours=2)).isoformat(),
                    "metadata": {"video_id": "vid123", "platform": "youtube"}
                },
                {
                    "id": str(uuid.uuid4()),
                    "type": "member_joined",
                    "user_name": "Mike Chen",
                    "description": "Joined the team as Editor",
                    "timestamp": (datetime.utcnow() - timedelta(hours=6)).isoformat(),
                    "metadata": {"role": "editor"}
                },
                {
                    "id": str(uuid.uuid4()),
                    "type": "analytics_milestone",
                    "user_name": "System",
                    "description": "Team reached 1M total views milestone!",
                    "timestamp": (datetime.utcnow() - timedelta(days=1)).isoformat(),
                    "metadata": {"milestone": "1M_views"}
                }
            ]
            
            return activities[:limit]
            
        except Exception as e:
            logger.error(f"Error getting team activity feed: {e}")
            return []
    
    async def _send_invitation_email(self, invitation: TeamInvitation):
        """Send invitation email (mock implementation)"""
        try:
            # In real implementation, use email service
            team = self.teams.get(invitation.team_id)
            team_name = team.name if team else "Team"
            
            email_content = {
                "to": invitation.email,
                "subject": f"You're invited to join {team_name}",
                "body": f"You've been invited to join {team_name} as a {invitation.role.value}.",
                "invitation_token": invitation.token,
                "expires_at": invitation.expires_at.isoformat()
            }
            
            logger.info(f"Invitation email sent to {invitation.email}")
            
        except Exception as e:
            logger.error(f"Error sending invitation email: {e}")
    
    def _get_default_team_settings(self) -> Dict[str, Any]:
        """Get default team settings"""
        return {
            "collaboration": {
                "allow_external_sharing": False,
                "require_approval_for_publishing": True,
                "enable_real_time_collaboration": True,
                "notification_preferences": {
                    "email_notifications": True,
                    "slack_integration": False,
                    "discord_integration": False
                }
            },
            "content": {
                "default_video_settings": {
                    "quality": "1080p",
                    "format": "mp4",
                    "thumbnail_style": "auto"
                },
                "content_guidelines": {
                    "require_brand_consistency": True,
                    "auto_apply_watermark": False,
                    "enforce_naming_convention": True
                }
            },
            "analytics": {
                "share_performance_data": True,
                "weekly_reports": True,
                "performance_alerts": True
            },
            "security": {
                "two_factor_required": False,
                "ip_restrictions": [],
                "session_timeout_minutes": 480
            }
        }
    
    async def update_team_settings(
        self,
        team_id: str,
        settings: Dict[str, Any],
        updated_by: str
    ) -> bool:
        """Update team settings"""
        try:
            if team_id not in self.teams:
                return False
            
            # Check permissions
            member = await self.get_team_member_by_user_id(team_id, updated_by)
            if not member or not await self.check_permission(team_id, updated_by, Permission.MANAGE_SETTINGS):
                raise ValueError("Insufficient permissions to update team settings")
            
            # Update settings
            self.teams[team_id].settings.update(settings)
            self.teams[team_id].updated_at = datetime.utcnow()
            
            logger.info(f"Team settings updated: {team_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating team settings: {e}")
            raise e
    
    async def get_team_insights(self, team_id: str) -> Dict[str, Any]:
        """Get comprehensive team insights"""
        try:
            performance = await self.analytics.get_team_performance(team_id)
            collaboration = await self.analytics.get_collaboration_insights(team_id)
            
            return {
                "team_id": team_id,
                "performance": performance,
                "collaboration": collaboration,
                "recommendations": await self._generate_team_recommendations(team_id),
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting team insights: {e}")
            return {}
    
    async def _generate_team_recommendations(self, team_id: str) -> List[Dict[str, Any]]:
        """Generate AI-powered team recommendations"""
        try:
            # Mock recommendations - in real implementation, use ML models
            return [
                {
                    "type": "productivity",
                    "title": "Optimize Video Review Process",
                    "description": "Your team spends 40% more time on video reviews than average. Consider implementing automated review workflows.",
                    "impact": "high",
                    "effort": "medium",
                    "estimated_time_savings": "8 hours/week"
                },
                {
                    "type": "collaboration",
                    "title": "Improve Cross-Team Communication",
                    "description": "Enable Slack integration to reduce email overhead and improve real-time collaboration.",
                    "impact": "medium",
                    "effort": "low",
                    "estimated_productivity_boost": "15%"
                },
                {
                    "type": "content",
                    "title": "Diversify Content Strategy",
                    "description": "Your team excels at tutorials but could benefit from exploring trending topics in gaming and tech reviews.",
                    "impact": "high",
                    "effort": "low",
                    "estimated_view_increase": "25%"
                }
            ]
            
        except Exception as e:
            logger.error(f"Error generating team recommendations: {e}")
            return []