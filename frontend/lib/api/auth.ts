import { apiClient } from './client';
import { ApiEndpoint, StorageKey } from '@/lib/constants/enums';
import {
  LoginRequest,
  RegisterRequest,
  AuthResponse,
  AuthUser,
} from '@/types/auth';

export const authApi = {
  async login(data: LoginRequest): Promise<AuthResponse> {
    const response = await apiClient.post<AuthResponse>(
      ApiEndpoint.AUTH_LOGIN,
      data
    );

    // Store tokens and user data
    if (typeof window !== 'undefined') {
      localStorage.setItem(StorageKey.ACCESS_TOKEN, response.data.tokens.access);
      localStorage.setItem(StorageKey.REFRESH_TOKEN, response.data.tokens.refresh);
      localStorage.setItem(StorageKey.USER, JSON.stringify(response.data.user));
    }

    return response.data;
  },

  async register(data: RegisterRequest): Promise<AuthResponse> {
    const response = await apiClient.post<AuthResponse>(
      ApiEndpoint.AUTH_REGISTER,
      data
    );

    // Store tokens and user data
    if (typeof window !== 'undefined') {
      localStorage.setItem(StorageKey.ACCESS_TOKEN, response.data.tokens.access);
      localStorage.setItem(StorageKey.REFRESH_TOKEN, response.data.tokens.refresh);
      localStorage.setItem(StorageKey.USER, JSON.stringify(response.data.user));
    }

    return response.data;
  },

  async logout(): Promise<void> {
    try {
      const refreshToken = localStorage.getItem(StorageKey.REFRESH_TOKEN);
      if (refreshToken) {
        await apiClient.post(ApiEndpoint.AUTH_LOGOUT, {
          refresh: refreshToken,
        });
      }
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      // Clear local storage regardless of API call success
      if (typeof window !== 'undefined') {
        localStorage.removeItem(StorageKey.ACCESS_TOKEN);
        localStorage.removeItem(StorageKey.REFRESH_TOKEN);
        localStorage.removeItem(StorageKey.USER);
      }
    }
  },

  async refreshToken(refreshToken: string): Promise<{ access: string }> {
    const response = await apiClient.post<{ access: string }>(
      ApiEndpoint.AUTH_REFRESH,
      { refresh: refreshToken }
    );

    if (typeof window !== 'undefined') {
      localStorage.setItem(StorageKey.ACCESS_TOKEN, response.data.access);
    }

    return response.data;
  },

  getCurrentUser(): AuthUser | null {
    if (typeof window !== 'undefined') {
      const userJson = localStorage.getItem(StorageKey.USER);
      if (userJson) {
        try {
          return JSON.parse(userJson);
        } catch {
          return null;
        }
      }
    }
    return null;
  },

  isAuthenticated(): boolean {
    if (typeof window !== 'undefined') {
      const token = localStorage.getItem(StorageKey.ACCESS_TOKEN);
      return !!token;
    }
    return false;
  },
};
