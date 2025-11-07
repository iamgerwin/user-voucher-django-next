import { apiClient } from './client';
import { ApiEndpoint } from '@/lib/constants/enums';
import {
  Voucher,
  CreateVoucherRequest,
  UpdateVoucherRequest,
  VoucherListResponse,
  VoucherUsageRequest,
  VoucherUsageResponse,
} from '@/types/voucher';

export const vouchersApi = {
  async getVouchers(page = 1, limit = 10): Promise<VoucherListResponse> {
    const response = await apiClient.get<VoucherListResponse>(
      `${ApiEndpoint.VOUCHERS}?page=${page}&limit=${limit}`
    );
    return response.data;
  },

  async getVoucherById(id: number): Promise<Voucher> {
    const response = await apiClient.get<Voucher>(`${ApiEndpoint.VOUCHERS}${id}/`);
    return response.data;
  },

  async createVoucher(data: CreateVoucherRequest): Promise<Voucher> {
    const response = await apiClient.post<Voucher>(ApiEndpoint.VOUCHERS, data);
    return response.data;
  },

  async updateVoucher(id: number, data: UpdateVoucherRequest): Promise<Voucher> {
    const response = await apiClient.patch<Voucher>(
      `${ApiEndpoint.VOUCHERS}${id}/`,
      data
    );
    return response.data;
  },

  async deleteVoucher(id: number): Promise<void> {
    await apiClient.delete(`${ApiEndpoint.VOUCHERS}${id}/`);
  },

  async useVoucher(data: VoucherUsageRequest): Promise<VoucherUsageResponse> {
    const response = await apiClient.post<VoucherUsageResponse>(
      ApiEndpoint.VOUCHER_USE,
      data
    );
    return response.data;
  },

  async searchVouchers(query: string): Promise<Voucher[]> {
    const response = await apiClient.get<VoucherListResponse>(
      `${ApiEndpoint.VOUCHERS}?search=${query}`
    );
    return response.data.results;
  },

  async getActiveVouchers(): Promise<Voucher[]> {
    const response = await apiClient.get<VoucherListResponse>(
      `${ApiEndpoint.VOUCHERS}?status=active`
    );
    return response.data.results;
  },
};
