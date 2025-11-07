export enum VoucherStatus {
  ACTIVE = 'active',
  USED = 'used',
  EXPIRED = 'expired',
}

export interface Voucher {
  id: number;
  code: string;
  name: string;
  description?: string;
  status: string;
  valid_from: string;
  valid_until: string;
  usage_limit: number | null;
  usage_count: number;
  usage_percentage: number | null;
  created_by: number;
  created_by_name: string;
  created_at: string;
  updated_at: string;
  voucher_type: string;
  is_valid: boolean;
  is_expired: boolean;
  // Polymorphic fields - may or may not be present depending on voucher type
  discount_amount?: string;
  min_purchase_amount?: string;
  discount_percentage?: string;
  max_discount_amount?: string;
}

export interface CreateVoucherRequest {
  code: string;
  discount_type: string;
  discount_amount: string;
  max_uses: number;
  valid_from?: string;
  valid_until?: string;
  valid_indefinitely?: boolean;
}

export interface UpdateVoucherRequest {
  name: string;
  description?: string;
  usage_limit?: number | null;
  valid_from?: string;
  valid_until?: string;
  status?: string;
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
