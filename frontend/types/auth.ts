export interface LoginRequest {
  username: string;
  password: string;
}

export interface RegisterRequest {
  username: string;
  email: string;
  password: string;
  password2: string;
  first_name?: string;
  last_name?: string;
}

export interface AuthTokens {
  access: string;
  refresh: string;
}

import { UserRole } from './user';

export interface AuthUser {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  role: UserRole;
  is_active: boolean;
  is_staff: boolean;
  date_joined: string;
}

export interface AuthResponse {
  tokens: AuthTokens;
  user: AuthUser;
}
