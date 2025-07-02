'use client';

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import Cookies from 'js-cookie';

interface User {
  user_id: number;
  email: string;
  role: string;
  subscription_plan: string;
  is_active: boolean;
  created_at: string;
  youtube_channels?: any[];
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  login: (email: string, password: string) => Promise<boolean>;
  register: (email: string, password: string, licenseKey?: string, invitationCode?: string) => Promise<boolean>;
  logout: () => void;
  googleLogin: () => Promise<void>;
  isLoading: boolean;
  error: string | null;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://13.60.77.139:8001';

  useEffect(() => {
    // Check for existing token on mount
    const savedToken = Cookies.get('auth_token');
    if (savedToken) {
      setToken(savedToken);
      fetchUserInfo(savedToken);
    } else {
      setIsLoading(false);
    }
  }, []);

  const fetchUserInfo = async (authToken: string) => {
    try {
      const response = await fetch(`${API_BASE}/api/auth/me`, {
        headers: {
          'Authorization': `Bearer ${authToken}`
        }
      });

      if (response.ok) {
        const userData = await response.json();
        setUser(userData);
      } else {
        // Token is invalid, remove it
        Cookies.remove('auth_token');
        setToken(null);
      }
    } catch (error) {
      console.error('Error fetching user info:', error);
      Cookies.remove('auth_token');
      setToken(null);
    } finally {
      setIsLoading(false);
    }
  };

  const login = async (email: string, password: string): Promise<boolean> => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch(`${API_BASE}/api/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password }),
      });

      if (response.ok) {
        const data = await response.json();
        const authToken = data.access_token;
        
        // Store token and user data
        Cookies.set('auth_token', authToken, { expires: 1 }); // 1 day
        Cookies.set('refresh_token', data.refresh_token, { expires: 30 }); // 30 days
        setToken(authToken);
        setUser(data.user);
        
        return true;
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Login failed');
        return false;
      }
    } catch (error) {
      setError('Network error. Please try again.');
      console.error('Login error:', error);
      return false;
    } finally {
      setIsLoading(false);
    }
  };

  const register = async (
    email: string, 
    password: string, 
    licenseKey?: string, 
    invitationCode?: string
  ): Promise<boolean> => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch(`${API_BASE}/api/auth/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          email, 
          password, 
          license_key: licenseKey,
          invitation_code: invitationCode
        }),
      });

      if (response.ok) {
        const data = await response.json();
        const authToken = data.access_token;
        
        // Store token and user data
        Cookies.set('auth_token', authToken, { expires: 1 });
        Cookies.set('refresh_token', data.refresh_token, { expires: 30 });
        setToken(authToken);
        setUser(data.user);
        
        return true;
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Registration failed');
        return false;
      }
    } catch (error) {
      setError('Network error. Please try again.');
      console.error('Registration error:', error);
      return false;
    } finally {
      setIsLoading(false);
    }
  };

  const googleLogin = async (): Promise<void> => {
    setIsLoading(true);
    setError(null);

    try {
      // Get authorization URL from backend
      const response = await fetch(`${API_BASE}/api/auth/google/authorize`);
      
      if (response.ok) {
        const data = await response.json();
        
        // Store state for validation
        Cookies.set('oauth_state', data.state, { expires: 1/24 }); // 1 hour
        
        // Redirect to Google OAuth
        window.location.href = data.authorization_url;
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Google OAuth initialization failed');
      }
    } catch (error) {
      setError('Network error. Please try again.');
      console.error('Google login error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const logout = () => {
    Cookies.remove('auth_token');
    Cookies.remove('refresh_token');
    Cookies.remove('oauth_state');
    setToken(null);
    setUser(null);
    setError(null);
  };

  const refreshToken = async () => {
    const refreshTokenValue = Cookies.get('refresh_token');
    
    if (!refreshTokenValue) {
      logout();
      return;
    }

    try {
      const response = await fetch(`${API_BASE}/api/auth/refresh`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ refresh_token: refreshTokenValue }),
      });

      if (response.ok) {
        const data = await response.json();
        Cookies.set('auth_token', data.access_token, { expires: 1 });
        setToken(data.access_token);
      } else {
        logout();
      }
    } catch (error) {
      console.error('Token refresh error:', error);
      logout();
    }
  };

  // Set up automatic token refresh
  useEffect(() => {
    if (token) {
      const interval = setInterval(() => {
        refreshToken();
      }, 25 * 60 * 1000); // Refresh every 25 minutes

      return () => clearInterval(interval);
    }
  }, [token]);

  const value: AuthContextType = {
    user,
    token,
    login,
    register,
    logout,
    googleLogin,
    isLoading,
    error
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};