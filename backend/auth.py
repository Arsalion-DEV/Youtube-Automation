"""
YouTube Automation Platform - Advanced Authentication System
Includes Google OAuth2, user registration, role-based access control, and license management
"""

import os
import secrets
import sqlite3
import hashlib
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from pydantic import BaseModel, EmailStr

import bcrypt
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build

logger = logging.getLogger(__name__)

# Security configurations
SECRET_KEY = os.getenv("SECRET_KEY", secrets.token_hex(32))
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 30

# Google OAuth2 Configuration
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI", "http://13.60.77.139:8001/api/auth/google/callback")

# Password encryption
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

# Pydantic Models
class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    license_key: Optional[str] = None
    invitation_code: Optional[str] = None

class GoogleOAuthRequest(BaseModel):
    auth_code: str
    state: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int
    user: Dict[str, Any]

class UserResponse(BaseModel):
    user_id: int
    email: str
    role: str
    subscription_plan: str
    created_at: datetime
    is_active: bool

@dataclass
class License:
    license_key: str
    max_users: int
    plan_type: str
    features: List[str]
    status: str
    expires_at: Optional[datetime] = None

class DatabaseConnection:
    """Enhanced database connection with user management tables"""
    
    def __init__(self, db_path: str = "../youtube_automation.db"):
        self.db_path = db_path
        self.init_auth_tables()
    
    def get_connection(self):
        return sqlite3.connect(self.db_path)
    
    def init_auth_tables(self):
        """Initialize authentication and user management tables"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Users table with enhanced features
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT,
                    google_id TEXT UNIQUE,
                    license_key TEXT,
                    subscription_plan TEXT DEFAULT 'trial',
                    role TEXT DEFAULT 'user',
                    is_active BOOLEAN DEFAULT 1,
                    email_verified BOOLEAN DEFAULT 0,
                    google_oauth_tokens TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP,
                    last_login TIMESTAMP
                )
            ''')
            
            # User sessions for token management
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    session_token TEXT UNIQUE NOT NULL,
                    refresh_token TEXT UNIQUE,
                    expires_at TIMESTAMP NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    user_agent TEXT,
                    ip_address TEXT,
                    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
                )
            ''')
            
            # License keys management
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS licenses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    license_key TEXT UNIQUE NOT NULL,
                    max_users INTEGER DEFAULT 1,
                    current_users INTEGER DEFAULT 0,
                    plan_type TEXT NOT NULL,
                    features TEXT,
                    status TEXT DEFAULT 'active',
                    created_by INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP,
                    FOREIGN KEY (created_by) REFERENCES users (id)
                )
            ''')
            
            # User channels association with OAuth data
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_channels (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    channel_id TEXT NOT NULL,
                    channel_name TEXT,
                    google_channel_id TEXT,
                    oauth_credentials TEXT,
                    permissions TEXT DEFAULT 'read,write',
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
                    UNIQUE(user_id, channel_id)
                )
            ''')
            
            # Invitation codes for controlled access
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS invitation_codes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    code TEXT UNIQUE NOT NULL,
                    uses_remaining INTEGER DEFAULT 1,
                    created_by INTEGER,
                    expires_at TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (created_by) REFERENCES users (id)
                )
            ''')
            
            # OAuth states for security
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS oauth_states (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    state TEXT UNIQUE NOT NULL,
                    user_ip TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP NOT NULL
                )
            ''')
            
            conn.commit()
            logger.info("Authentication tables initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing auth tables: {str(e)}")
            raise
        finally:
            conn.close()

class GoogleOAuthManager:
    """Manages Google OAuth2 flow and YouTube API integration"""
    
    def __init__(self):
        self.client_id = GOOGLE_CLIENT_ID
        self.client_secret = GOOGLE_CLIENT_SECRET
        self.redirect_uri = GOOGLE_REDIRECT_URI
        self.scopes = [
            'openid',
            'email',
            'profile',
            'https://www.googleapis.com/auth/youtube.readonly',
            'https://www.googleapis.com/auth/youtube.channel-memberships.creator',
            'https://www.googleapis.com/auth/youtube.force-ssl'
        ]
    
    def create_authorization_url(self, state: str) -> str:
        """Create Google OAuth2 authorization URL"""
        if not self.client_id or not self.client_secret:
            raise HTTPException(
                status_code=500,
                detail="Google OAuth2 not configured. Please set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET"
            )
        
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [self.redirect_uri]
                }
            },
            scopes=self.scopes
        )
        flow.redirect_uri = self.redirect_uri
        
        authorization_url, _ = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            state=state,
            prompt='consent'
        )
        
        return authorization_url
    
    def exchange_code_for_tokens(self, auth_code: str) -> Dict[str, Any]:
        """Exchange authorization code for access tokens"""
        try:
            flow = Flow.from_client_config(
                {
                    "web": {
                        "client_id": self.client_id,
                        "client_secret": self.client_secret,
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                        "redirect_uris": [self.redirect_uri]
                    }
                },
                scopes=self.scopes
            )
            flow.redirect_uri = self.redirect_uri
            
            # Exchange code for tokens
            flow.fetch_token(code=auth_code)
            credentials = flow.credentials
            
            # Get user info
            user_info = self.get_user_info(credentials)
            
            # Get YouTube channels
            youtube_channels = self.get_user_youtube_channels(credentials)
            
            return {
                'credentials': {
                    'token': credentials.token,
                    'refresh_token': credentials.refresh_token,
                    'token_uri': credentials.token_uri,
                    'client_id': credentials.client_id,
                    'client_secret': credentials.client_secret,
                    'scopes': credentials.scopes
                },
                'user_info': user_info,
                'youtube_channels': youtube_channels
            }
            
        except Exception as e:
            logger.error(f"Error exchanging OAuth code: {str(e)}")
            raise HTTPException(status_code=400, detail="Invalid authorization code")
    
    def get_user_info(self, credentials: Credentials) -> Dict[str, Any]:
        """Get user information from Google API"""
        try:
            service = build('oauth2', 'v2', credentials=credentials)
            user_info = service.userinfo().get().execute()
            return user_info
        except Exception as e:
            logger.error(f"Error getting user info: {str(e)}")
            return {}
    
    def get_user_youtube_channels(self, credentials: Credentials) -> List[Dict[str, Any]]:
        """Get user's YouTube channels"""
        try:
            youtube = build('youtube', 'v3', credentials=credentials)
            channels_response = youtube.channels().list(
                part='snippet,statistics,contentDetails',
                mine=True
            ).execute()
            
            channels = []
            for channel in channels_response.get('items', []):
                channels.append({
                    'id': channel['id'],
                    'title': channel['snippet']['title'],
                    'description': channel['snippet']['description'],
                    'thumbnail': channel['snippet']['thumbnails'].get('default', {}).get('url'),
                    'subscriber_count': channel['statistics'].get('subscriberCount', 0),
                    'video_count': channel['statistics'].get('videoCount', 0),
                    'view_count': channel['statistics'].get('viewCount', 0)
                })
            
            return channels
            
        except Exception as e:
            logger.error(f"Error getting YouTube channels: {str(e)}")
            return []

class UserManager:
    """Enhanced user management with OAuth and license support"""
    
    def __init__(self, db: DatabaseConnection):
        self.db = db
        self.oauth_manager = GoogleOAuthManager()
    
    async def create_user(self, email: str, password: Optional[str] = None, 
                         google_id: Optional[str] = None, license_key: Optional[str] = None,
                         invitation_code: Optional[str] = None) -> int:
        """Create a new user with various registration methods"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            # Check if user already exists
            cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
            if cursor.fetchone():
                raise ValueError("User with this email already exists")
            
            # Validate license key if provided
            subscription_plan = 'trial'
            if license_key:
                license_info = self.validate_license_key(license_key)
                if not license_info:
                    raise ValueError("Invalid license key")
                subscription_plan = license_info.plan_type
            
            # Validate invitation code if provided
            if invitation_code:
                if not self.validate_invitation_code(invitation_code):
                    raise ValueError("Invalid or expired invitation code")
            
            # Hash password if provided
            password_hash = None
            if password:
                password_hash = pwd_context.hash(password)
            
            # Determine role based on subscription plan
            role = 'admin' if subscription_plan == 'enterprise' else 'user'
            
            # Set expiration for trial accounts
            expires_at = None
            if subscription_plan == 'trial':
                expires_at = datetime.utcnow() + timedelta(days=7)
            
            # Insert user
            cursor.execute("""
                INSERT INTO users 
                (email, password_hash, google_id, license_key, subscription_plan, role, expires_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (email, password_hash, google_id, license_key, subscription_plan, role, expires_at))
            
            user_id = cursor.lastrowid
            
            # Update license usage if applicable
            if license_key:
                cursor.execute("""
                    UPDATE licenses 
                    SET current_users = current_users + 1 
                    WHERE license_key = ?
                """, (license_key,))
            
            # Mark invitation code as used
            if invitation_code:
                cursor.execute("""
                    UPDATE invitation_codes 
                    SET uses_remaining = uses_remaining - 1 
                    WHERE code = ? AND uses_remaining > 0
                """, (invitation_code,))
            
            conn.commit()
            logger.info(f"User created successfully: {email} (ID: {user_id})")
            return user_id
            
        except Exception as e:
            conn.rollback()
            logger.error(f"Error creating user: {str(e)}")
            raise
        finally:
            conn.close()
    
    async def authenticate_user(self, email: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate user with email and password"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT id, email, password_hash, role, subscription_plan, is_active, expires_at
                FROM users WHERE email = ?
            """, (email,))
            
            user = cursor.fetchone()
            if not user:
                return None
            
            user_id, email, password_hash, role, subscription_plan, is_active, expires_at = user
            
            # Check if account is active
            if not is_active:
                raise HTTPException(status_code=403, detail="Account is deactivated")
            
            # Check if account has expired
            if expires_at:
                expires_at = datetime.fromisoformat(expires_at)
                if expires_at < datetime.utcnow():
                    raise HTTPException(status_code=403, detail="Account has expired")
            
            # Verify password
            if not password_hash or not pwd_context.verify(password, password_hash):
                return None
            
            # Update last login
            cursor.execute("""
                UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?
            """, (user_id,))
            conn.commit()
            
            return {
                'user_id': user_id,
                'email': email,
                'role': role,
                'subscription_plan': subscription_plan
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error authenticating user: {str(e)}")
            return None
        finally:
            conn.close()
    
    async def authenticate_google_user(self, google_auth_data: Dict[str, Any]) -> Dict[str, Any]:
        """Authenticate or create user via Google OAuth"""
        user_info = google_auth_data['user_info']
        credentials = google_auth_data['credentials']
        youtube_channels = google_auth_data['youtube_channels']
        
        email = user_info.get('email')
        google_id = user_info.get('id')
        name = user_info.get('name', '')
        
        if not email or not google_id:
            raise HTTPException(status_code=400, detail="Invalid Google user data")
        
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            # Check if user exists
            cursor.execute("""
                SELECT id, email, role, subscription_plan, is_active, expires_at
                FROM users WHERE email = ? OR google_id = ?
            """, (email, google_id))
            
            user = cursor.fetchone()
            
            if user:
                # Update existing user
                user_id, email, role, subscription_plan, is_active, expires_at = user
                
                if not is_active:
                    raise HTTPException(status_code=403, detail="Account is deactivated")
                
                # Update Google credentials
                cursor.execute("""
                    UPDATE users 
                    SET google_oauth_tokens = ?, last_login = CURRENT_TIMESTAMP 
                    WHERE id = ?
                """, (str(credentials), user_id))
                
            else:
                # Create new user
                user_id = await self.create_user(
                    email=email,
                    google_id=google_id
                )
                
                cursor.execute("""
                    UPDATE users 
                    SET google_oauth_tokens = ? 
                    WHERE id = ?
                """, (str(credentials), user_id))
                
                role = 'user'
                subscription_plan = 'trial'
            
            # Store/update YouTube channels
            for channel in youtube_channels:
                cursor.execute("""
                    INSERT OR REPLACE INTO user_channels 
                    (user_id, channel_id, channel_name, google_channel_id, oauth_credentials)
                    VALUES (?, ?, ?, ?, ?)
                """, (user_id, channel['id'], channel['title'], channel['id'], str(credentials)))
            
            conn.commit()
            
            return {
                'user_id': user_id,
                'email': email,
                'role': role,
                'subscription_plan': subscription_plan,
                'youtube_channels': youtube_channels
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error authenticating Google user: {str(e)}")
            raise HTTPException(status_code=500, detail="Google authentication failed")
        finally:
            conn.close()
    
    def validate_license_key(self, license_key: str) -> Optional[License]:
        """Validate and get license information"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT license_key, max_users, current_users, plan_type, features, status, expires_at
                FROM licenses WHERE license_key = ? AND status = 'active'
            """, (license_key,))
            
            result = cursor.fetchone()
            if not result:
                return None
            
            license_key, max_users, current_users, plan_type, features, status, expires_at = result
            
            # Check if license has expired
            if expires_at:
                expires_at = datetime.fromisoformat(expires_at)
                if expires_at < datetime.utcnow():
                    return None
            
            # Check if license has available slots
            if current_users >= max_users:
                return None
            
            return License(
                license_key=license_key,
                max_users=max_users,
                plan_type=plan_type,
                features=features.split(',') if features else [],
                status=status,
                expires_at=expires_at
            )
            
        except Exception as e:
            logger.error(f"Error validating license key: {str(e)}")
            return None
        finally:
            conn.close()
    
    def validate_invitation_code(self, code: str) -> bool:
        """Validate invitation code"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT uses_remaining, expires_at FROM invitation_codes 
                WHERE code = ? AND uses_remaining > 0
            """, (code,))
            
            result = cursor.fetchone()
            if not result:
                return False
            
            uses_remaining, expires_at = result
            
            if expires_at:
                expires_at = datetime.fromisoformat(expires_at)
                if expires_at < datetime.utcnow():
                    return False
            
            return uses_remaining > 0
            
        except Exception as e:
            logger.error(f"Error validating invitation code: {str(e)}")
            return False
        finally:
            conn.close()

class AuthSystem:
    """Main authentication system"""
    
    def __init__(self):
        self.db = DatabaseConnection()
        self.user_manager = UserManager(self.db)
        self.token_expire_minutes = ACCESS_TOKEN_EXPIRE_MINUTES
    
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None):
        """Create JWT access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    def create_refresh_token(self, data: dict):
        """Create JWT refresh token"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        to_encode.update({"exp": expire, "type": "refresh"})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    def create_user_token(self, user_id: int, email: str, role: str) -> str:
        """Create access token for user"""
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = self.create_access_token(
            data={"sub": str(user_id), "email": email, "role": role},
            expires_delta=access_token_expires
        )
        return access_token
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """Verify JWT token"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user_id: str = payload.get("sub")
            if user_id is None:
                raise JWTError("Token missing user ID")
            return payload
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    def generate_oauth_state(self) -> str:
        """Generate secure OAuth state parameter"""
        return secrets.token_urlsafe(32)
    
    def generate_license_key(self, plan_type: str = "standard") -> str:
        """Generate license key"""
        prefix = "YT"
        if plan_type == "premium":
            prefix = "YTP"
        elif plan_type == "enterprise":
            prefix = "YTE"
        
        key = f"{prefix}-{secrets.token_hex(8).upper()}-{secrets.token_hex(4).upper()}"
        return key

# Dependency functions
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """Get current authenticated user"""
    token = credentials.credentials
    payload = auth_system.verify_token(token)
    
    user_id = int(payload.get("sub"))
    email = payload.get("email")
    role = payload.get("role")
    
    return {
        "user_id": user_id,
        "email": email,
        "role": role
    }

async def get_current_admin(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """Get current admin user"""
    if current_user["role"] not in ["admin", "super_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user

# Initialize global instances
auth_system = AuthSystem()
user_manager = auth_system.user_manager