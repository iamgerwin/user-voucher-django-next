import { apiClient } from './client';
import { ApiEndpoint } from '@/lib/constants/enums';
import {
  User,
  CreateUserRequest,
  UpdateUserRequest,
  UserListResponse,
} from '@/types/user';

export const usersApi = {
  async getUsers(page = 1, limit = 10): Promise<UserListResponse> {
    const response = await apiClient.get<UserListResponse>(
      `${ApiEndpoint.USERS}?page=${page}&limit=${limit}`
    );
    return response.data;
  },

  async getUserById(id: number): Promise<User> {
    const response = await apiClient.get<User>(`${ApiEndpoint.USERS}${id}/`);
    return response.data;
  },

  async createUser(data: CreateUserRequest): Promise<User> {
    const response = await apiClient.post<User>(ApiEndpoint.USERS, data);
    return response.data;
  },

  async updateUser(id: number, data: UpdateUserRequest): Promise<User> {
    const response = await apiClient.patch<User>(
      `${ApiEndpoint.USERS}${id}/`,
      data
    );
    return response.data;
  },

  async deleteUser(id: number): Promise<void> {
    await apiClient.delete(`${ApiEndpoint.USERS}${id}/`);
  },

  async searchUsers(query: string): Promise<User[]> {
    const response = await apiClient.get<UserListResponse>(
      `${ApiEndpoint.USERS}?search=${query}`
    );
    return response.data.results;
  },
};
