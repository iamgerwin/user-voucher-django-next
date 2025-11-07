import { z } from 'zod';
import { DiscountType } from '@/lib/constants/enums';

export const createVoucherSchema = z.object({
  code: z
    .string()
    .min(4, 'Code must be at least 4 characters')
    .max(50, 'Code must be less than 50 characters')
    .regex(/^[A-Z0-9-_]+$/, 'Code can only contain uppercase letters, numbers, hyphens, and underscores'),
  discount_type: z.enum([DiscountType.FIXED, DiscountType.PERCENTAGE], {
    required_error: 'Discount type is required',
  }),
  discount_amount: z
    .string()
    .regex(/^\d+(\.\d{1,2})?$/, 'Invalid amount format')
    .refine((val) => parseFloat(val) > 0, 'Discount amount must be greater than 0'),
  max_uses: z
    .number()
    .int('Max uses must be a whole number')
    .min(1, 'Max uses must be at least 1'),
  valid_from: z.string().optional(),
  valid_until: z.string().optional(),
  valid_indefinitely: z.boolean().optional(),
}).refine((data) => {
  // If discount type is percentage, validate it's between 0 and 100
  if (data.discount_type === DiscountType.PERCENTAGE) {
    const amount = parseFloat(data.discount_amount);
    return amount > 0 && amount <= 100;
  }
  return true;
}, {
  message: 'Percentage must be between 0 and 100',
  path: ['discount_amount'],
}).refine((data) => {
  // If not valid indefinitely, dates are required
  if (!data.valid_indefinitely && (!data.valid_from || !data.valid_until)) {
    return false;
  }
  return true;
}, {
  message: 'Valid from and until dates are required when not valid indefinitely',
  path: ['valid_from'],
}).refine((data) => {
  // If dates are provided, valid_until must be after valid_from
  if (data.valid_from && data.valid_until) {
    const from = new Date(data.valid_from);
    const until = new Date(data.valid_until);
    return until > from;
  }
  return true;
}, {
  message: 'Valid until date must be after valid from date',
  path: ['valid_until'],
});

export const updateVoucherSchema = z.object({
  code: z
    .string()
    .min(4, 'Code must be at least 4 characters')
    .max(50, 'Code must be less than 50 characters')
    .regex(/^[A-Z0-9-_]+$/, 'Code can only contain uppercase letters, numbers, hyphens, and underscores')
    .optional(),
  discount_amount: z
    .string()
    .regex(/^\d+(\.\d{1,2})?$/, 'Invalid amount format')
    .refine((val) => parseFloat(val) > 0, 'Discount amount must be greater than 0')
    .optional(),
  max_uses: z
    .number()
    .int('Max uses must be a whole number')
    .min(1, 'Max uses must be at least 1')
    .optional(),
  valid_from: z.string().optional(),
  valid_until: z.string().optional(),
  status: z.enum(['active', 'used', 'expired']).optional(),
});

export const useVoucherSchema = z.object({
  code: z.string().min(1, 'Voucher code is required'),
  user_id: z.number().int().positive('Invalid user ID'),
});

export type CreateVoucherFormData = z.infer<typeof createVoucherSchema>;
export type UpdateVoucherFormData = z.infer<typeof updateVoucherSchema>;
export type UseVoucherFormData = z.infer<typeof useVoucherSchema>;
