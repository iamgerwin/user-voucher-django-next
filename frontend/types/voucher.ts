export enum VoucherStatus {
  ACTIVE = 'active',
  USED = 'used',
  EXPIRED = 'expired',
}

export interface Voucher {
  id: number;
  code: string;
  discount_amount: string;
  max_uses: number;
  used_count: number;
  valid_from: string;
  valid_until: string;
  status: VoucherStatus;
  created_at: string;
  updated_at: string;
  created_by: number;
}

export interface CreateVoucherRequest {
  code: string;
  discount_amount: string;
  max_uses: number;
  valid_from: string;
  valid_until: string;
}

export interface UpdateVoucherRequest {
  code?: string;
  discount_amount?: string;
  max_uses?: number;
  valid_from?: string;
  valid_until?: string;
  status?: VoucherStatus;
}

export interface VoucherListResponse {
  count: number;
  next: string | null;
  previous: string | null;
  results: Voucher[];
}

export interface VoucherUsageRequest {
  code: string;
  user_id: number;
}

export interface VoucherUsageResponse {
  success: boolean;
  message: string;
  voucher?: Voucher;
}
