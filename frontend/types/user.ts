export enum UserRole {
  ADMIN = 'ADMIN',
  MANAGER = 'MANAGER',
  USER = 'USER',
  GUEST = 'GUEST',
}

export interface User {
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

export interface CreateUserRequest {
  username: string;
  email: string;
  password: string;
  first_name?: string;
  last_name?: string;
  is_active?: boolean;
  is_staff?: boolean;
}

export interface UpdateUserRequest {
  username?: string;
  email?: string;
  first_name?: string;
  last_name?: string;
  is_active?: boolean;
  is_staff?: boolean;
}

export interface UserListResponse {
  count: number;
  next: string | null;
  previous: string | null;
  results: User[];
}
