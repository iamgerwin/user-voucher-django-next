'use client';

import { useState, useEffect } from 'react';
import { authApi } from '@/lib/api/auth';
import { AuthUser, LoginRequest, RegisterRequest } from '@/types/auth';
import { AppRoute } from '@/lib/constants/routes';
import { useRouter } from 'next/navigation';

export function useAuth() {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const router = useRouter();

  useEffect(() => {
    const currentUser = authApi.getCurrentUser();
    const authenticated = authApi.isAuthenticated();

    setUser(currentUser);
    setIsAuthenticated(authenticated);
    setIsLoading(false);
  }, []);

  const login = async (credentials: LoginRequest) => {
    try {
      const response = await authApi.login(credentials);
      setUser(response.user);
      setIsAuthenticated(true);
      router.push(AppRoute.DASHBOARD);
      return { success: true, data: response };
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.message || 'Login failed',
      };
    }
  };

  const register = async (data: RegisterRequest) => {
    try {
      const response = await authApi.register(data);
      setUser(response.user);
      setIsAuthenticated(true);
      router.push(AppRoute.DASHBOARD);
      return { success: true, data: response };
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.message || 'Registration failed',
      };
    }
  };

  const logout = async () => {
    try {
      await authApi.logout();
      setUser(null);
      setIsAuthenticated(false);
      router.push(AppRoute.LOGIN);
    } catch (error) {
      console.error('Logout error:', error);
    }
  };

  return {
    user,
    isLoading,
    isAuthenticated,
    login,
    register,
    logout,
  };
}
