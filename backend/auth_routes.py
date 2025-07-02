"""
Enhanced Authentication Routes for YouTube Automation Platform
Includes Google OAuth2, license management, and channel discovery
"""

import json
import logging
import secrets
from typing import Dict, Any, Optional
from fastapi import HTTPException, Depends, status, APIRouter, Request, Response
from fastapi.responses import RedirectResponse

from auth import (
    auth_system, user_manager, get_current_user, get_current_admin,
    LoginRequest, RegisterRequest, GoogleOAuthRequest, TokenResponse, UserResponse
)

logger = logging.getLogger(__name__)

# Create enhanced router
auth_router = APIRouter(tags=["authentication"])

@auth_router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest):
    """Enhanced user login with comprehensive error handling"""
    try:
        user = await user_manager.authenticate_user(request.email, request.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )
        
        # Create tokens
        access_token = auth_system.create_user_token(
            user["user_id"], user["email"], user["role"]
        )
        
        refresh_token = auth_system.create_refresh_token({
            "sub": str(user["user_id"]),
            "email": user["email"],
            "role": user["role"]
        })
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": auth_system.token_expire_minutes * 60,
            "user": user
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        raise HTTPException(status_code=500, detail="Login failed")

@auth_router.post("/register", response_model=TokenResponse)
async def register(request: RegisterRequest):
    """Enhanced user registration with license key and invitation code support"""
    try:
        user_id = await user_manager.create_user(
            email=request.email,
            password=request.password,
            license_key=request.license_key,
            invitation_code=request.invitation_code
        )
        
        # Get created user info
        user = {
            "user_id": user_id,
            "email": request.email,
            "role": "user",  # Default role, will be updated based on license
            "subscription_plan": "trial"  # Default plan
        }
        
        access_token = auth_system.create_user_token(
            user["user_id"], user["email"], user["role"]
        )
        
        refresh_token = auth_system.create_refresh_token({
            "sub": str(user["user_id"]),
            "email": user["email"],
            "role": user["role"]
        })
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": auth_system.token_expire_minutes * 60,
            "user": user
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        raise HTTPException(status_code=500, detail="Registration failed")

@auth_router.get("/google/authorize")
async def google_authorize(request: Request):
    """Initiate Google OAuth2 flow"""
    try:
        # Generate secure state parameter
        state = auth_system.generate_oauth_state()
        
        # Store state in database for validation
        conn = auth_system.db.get_connection()
        cursor = conn.cursor()
        
        # Get client IP
        client_ip = request.client.host
        
        # Store OAuth state
        cursor.execute("""
            INSERT INTO oauth_states (state, user_ip, expires_at)
            VALUES (?, ?, datetime('now', '+10 minutes'))
        """, (state, client_ip))
        conn.commit()
        conn.close()
        
        # Create authorization URL
        auth_url = user_manager.oauth_manager.create_authorization_url(state)
        
        return {"authorization_url": auth_url, "state": state}
        
    except Exception as e:
        logger.error(f"Google authorization error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to initiate Google OAuth")

@auth_router.get("/google/callback")
async def google_callback(code: str, state: str, request: Request):
    """Handle Google OAuth2 callback"""
    try:
        # Validate state parameter
        conn = auth_system.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id FROM oauth_states 
            WHERE state = ? AND expires_at > datetime('now')
        """, (state,))
        
        if not cursor.fetchone():
            conn.close()
            raise HTTPException(status_code=400, detail="Invalid or expired OAuth state")
        
        # Remove used state
        cursor.execute("DELETE FROM oauth_states WHERE state = ?", (state,))
        conn.commit()
        conn.close()
        
        # Exchange code for tokens and user data
        google_auth_data = user_manager.oauth_manager.exchange_code_for_tokens(code)
        
        # Authenticate or create user
        user_data = await user_manager.authenticate_google_user(google_auth_data)
        
        # Create access tokens
        access_token = auth_system.create_user_token(
            user_data["user_id"], user_data["email"], user_data["role"]
        )
        
        refresh_token = auth_system.create_refresh_token({
            "sub": str(user_data["user_id"]),
            "email": user_data["email"],
            "role": user_data["role"]
        })
        
        # Redirect to frontend with tokens (in production, use secure cookies)
        redirect_url = f"http://13.60.77.139:3000/auth/callback?access_token={access_token}&user={json.dumps(user_data)}"
        return RedirectResponse(url=redirect_url)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Google callback error: {str(e)}")
        raise HTTPException(status_code=500, detail="Google OAuth callback failed")

@auth_router.post("/google/token")
async def google_token_exchange(request: GoogleOAuthRequest):
    """Direct token exchange for frontend-initiated OAuth"""
    try:
        # Validate state
        conn = auth_system.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id FROM oauth_states 
            WHERE state = ? AND expires_at > datetime('now')
        """, (request.state,))
        
        if not cursor.fetchone():
            conn.close()
            raise HTTPException(status_code=400, detail="Invalid or expired OAuth state")
        
        # Remove used state
        cursor.execute("DELETE FROM oauth_states WHERE state = ?", (request.state,))
        conn.commit()
        conn.close()
        
        # Exchange code for tokens
        google_auth_data = user_manager.oauth_manager.exchange_code_for_tokens(request.auth_code)
        user_data = await user_manager.authenticate_google_user(google_auth_data)
        
        # Create tokens
        access_token = auth_system.create_user_token(
            user_data["user_id"], user_data["email"], user_data["role"]
        )
        
        refresh_token = auth_system.create_refresh_token({
            "sub": str(user_data["user_id"]),
            "email": user_data["email"],
            "role": user_data["role"]
        })
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": auth_system.token_expire_minutes * 60,
            "user": user_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Google token exchange error: {str(e)}")
        raise HTTPException(status_code=500, detail="Token exchange failed")

@auth_router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Get comprehensive current user information"""
    try:
        conn = auth_system.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, email, role, subscription_plan, is_active, created_at, expires_at, last_login
            FROM users WHERE id = ?
        """, (current_user["user_id"],))
        
        user_data = cursor.fetchone()
        if not user_data:
            raise HTTPException(status_code=404, detail="User not found")
        
        user_id, email, role, subscription_plan, is_active, created_at, expires_at, last_login = user_data
        
        # Get user's YouTube channels
        cursor.execute("""
            SELECT channel_id, channel_name, google_channel_id, is_active
            FROM user_channels WHERE user_id = ? AND is_active = 1
        """, (current_user["user_id"],))
        
        channels = []
        for channel_data in cursor.fetchall():
            channel_id, channel_name, google_channel_id, is_active = channel_data
            channels.append({
                "channel_id": channel_id,
                "channel_name": channel_name,
                "google_channel_id": google_channel_id,
                "is_active": bool(is_active)
            })
        
        conn.close()
        
        return {
            "user_id": user_id,
            "email": email,
            "role": role,
            "subscription_plan": subscription_plan,
            "is_active": bool(is_active),
            "created_at": created_at,
            "expires_at": expires_at,
            "last_login": last_login,
            "youtube_channels": channels
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get user info error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get user info")

@auth_router.get("/channels")
async def get_user_channels(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Get user's YouTube channels with OAuth integration"""
    try:
        conn = auth_system.db.get_connection()
        cursor = conn.cursor()
        
        # Get user's OAuth credentials
        cursor.execute("""
            SELECT google_oauth_tokens FROM users WHERE id = ?
        """, (current_user["user_id"],))
        
        result = cursor.fetchone()
        if not result or not result[0]:
            return {"channels": [], "message": "No Google OAuth connection found"}
        
        # Get channels from database
        cursor.execute("""
            SELECT channel_id, channel_name, google_channel_id, oauth_credentials, is_active, created_at
            FROM user_channels WHERE user_id = ?
        """, (current_user["user_id"],))
        
        channels = []
        for channel_data in cursor.fetchall():
            channel_id, channel_name, google_channel_id, oauth_creds, is_active, created_at = channel_data
            channels.append({
                "channel_id": channel_id,
                "channel_name": channel_name,
                "google_channel_id": google_channel_id,
                "is_active": bool(is_active),
                "created_at": created_at,
                "has_oauth": bool(oauth_creds)
            })
        
        conn.close()
        
        return {
            "channels": channels,
            "total_channels": len(channels),
            "active_channels": len([c for c in channels if c["is_active"]])
        }
        
    except Exception as e:
        logger.error(f"Get channels error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get channels")

@auth_router.post("/refresh")
async def refresh_access_token(refresh_token: str):
    """Refresh access token using refresh token"""
    try:
        # Verify refresh token
        payload = auth_system.verify_token(refresh_token)
        
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid refresh token")
        
        user_id = int(payload.get("sub"))
        email = payload.get("email")
        role = payload.get("role")
        
        # Create new access token
        access_token = auth_system.create_user_token(user_id, email, role)
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": auth_system.token_expire_minutes * 60
        }
        
    except Exception as e:
        logger.error(f"Token refresh error: {str(e)}")
        raise HTTPException(status_code=401, detail="Token refresh failed")

@auth_router.post("/logout")
async def logout():
    """User logout (client-side token removal)"""
    return {"message": "Logged out successfully"}

# Admin routes for license and user management
@auth_router.post("/admin/license/generate")
async def generate_license(
    plan_type: str = "standard",
    max_users: int = 1,
    expires_days: Optional[int] = None,
    current_admin: Dict[str, Any] = Depends(get_current_admin)
):
    """Generate new license key (Admin only)"""
    try:
        license_key = auth_system.generate_license_key(plan_type)
        
        # Determine features based on plan type
        features = []
        if plan_type == "premium":
            features = ["multi_channel", "advanced_analytics", "api_access"]
        elif plan_type == "enterprise":
            features = ["multi_channel", "advanced_analytics", "api_access", "white_label", "priority_support"]
        else:
            features = ["basic_features"]
        
        # Calculate expiration
        expires_at = None
        if expires_days:
            from datetime import datetime, timedelta
            expires_at = datetime.utcnow() + timedelta(days=expires_days)
        
        # Store license in database
        conn = auth_system.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO licenses 
            (license_key, max_users, plan_type, features, created_by, expires_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (license_key, max_users, plan_type, ",".join(features), current_admin["user_id"], expires_at))
        
        conn.commit()
        conn.close()
        
        return {
            "license_key": license_key,
            "plan_type": plan_type,
            "max_users": max_users,
            "features": features,
            "expires_at": expires_at
        }
        
    except Exception as e:
        logger.error(f"License generation error: {str(e)}")
        raise HTTPException(status_code=500, detail="License generation failed")

@auth_router.get("/admin/users")
async def list_users(
    skip: int = 0,
    limit: int = 50,
    current_admin: Dict[str, Any] = Depends(get_current_admin)
):
    """List all users (Admin only)"""
    try:
        conn = auth_system.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, email, role, subscription_plan, is_active, created_at, last_login
            FROM users 
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
        """, (limit, skip))
        
        users = []
        for user_data in cursor.fetchall():
            user_id, email, role, subscription_plan, is_active, created_at, last_login = user_data
            users.append({
                "user_id": user_id,
                "email": email,
                "role": role,
                "subscription_plan": subscription_plan,
                "is_active": bool(is_active),
                "created_at": created_at,
                "last_login": last_login
            })
        
        # Get total count
        cursor.execute("SELECT COUNT(*) FROM users")
        total_users = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            "users": users,
            "total": total_users,
            "skip": skip,
            "limit": limit
        }
        
    except Exception as e:
        logger.error(f"List users error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to list users")

@auth_router.get("/validate-license/{license_key}")
async def validate_license_key(license_key: str):
    """Validate license key (public endpoint for registration)"""
    try:
        license_info = user_manager.validate_license_key(license_key)
        
        if not license_info:
            return {"valid": False, "message": "Invalid or expired license key"}
        
        return {
            "valid": True,
            "plan_type": license_info.plan_type,
            "features": license_info.features,
            "available_slots": license_info.max_users - user_manager.get_license_usage(license_key)
        }
        
    except Exception as e:
        logger.error(f"License validation error: {str(e)}")
        raise HTTPException(status_code=500, detail="License validation failed")

@auth_router.get("/validate-invitation/{code}")
async def validate_invitation_code(code: str):
    """Validate invitation code (public endpoint for registration)"""
    try:
        is_valid = user_manager.validate_invitation_code(code)
        
        return {"valid": is_valid}
        
    except Exception as e:
        logger.error(f"Invitation validation error: {str(e)}")
        raise HTTPException(status_code=500, detail="Invitation validation failed")