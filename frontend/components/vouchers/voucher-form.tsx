'use client';

import { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { useRouter } from 'next/navigation';
import {
  createVoucherSchema,
  updateVoucherSchema,
  CreateVoucherFormData,
  UpdateVoucherFormData,
} from '@/lib/validations/voucher';
import { Voucher } from '@/types/voucher';
import { DiscountType } from '@/lib/constants/enums';
import { AppRoute } from '@/lib/constants/routes';
import { Button } from '@/components/ui/button';
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
  FormDescription,
} from '@/components/ui/form';
import { Input } from '@/components/ui/input';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Checkbox } from '@/components/ui/checkbox';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';

interface VoucherFormProps {
  mode?: 'create' | 'edit';
  initialData?: Voucher;
  onSubmit: (data: CreateVoucherFormData | UpdateVoucherFormData) => Promise<void>;
  isLoading?: boolean;
}

export function VoucherForm({
  mode = 'create',
  initialData,
  onSubmit,
  isLoading = false,
}: VoucherFormProps) {
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  // Determine initial discount type from initialData
  const initialDiscountType = initialData?.discount_percentage
    ? DiscountType.PERCENTAGE
    : DiscountType.FIXED;

  const [discountType, setDiscountType] = useState<DiscountType>(
    mode === 'edit' ? initialDiscountType : DiscountType.FIXED
  );

  // Check if initial data is indefinite
  const checkIfIndefinite = (voucher?: Voucher) => {
    if (!voucher?.valid_until) return false;
    const validUntilDate = new Date(voucher.valid_until);
    const currentDate = new Date();
    const yearsDifference = validUntilDate.getFullYear() - currentDate.getFullYear();
    return yearsDifference >= 50;
  };

  const [validIndefinitely, setValidIndefinitely] = useState(
    mode === 'edit' ? checkIfIndefinite(initialData) : false
  );

  // Format dates for datetime-local input
  const formatDateForInput = (dateString?: string) => {
    if (!dateString) return '';
    const date = new Date(dateString);
    return date.toISOString().slice(0, 16);
  };

  const form = useForm<CreateVoucherFormData | UpdateVoucherFormData>({
    resolver: zodResolver(mode === 'edit' ? updateVoucherSchema : createVoucherSchema),
    defaultValues:
      mode === 'edit' && initialData
        ? {
            code: initialData.code,
            discount_amount: String(
              initialData.discount_percentage || initialData.discount_amount || ''
            ),
            max_uses: initialData.usage_limit || 1,
            valid_from: validIndefinitely ? '' : formatDateForInput(initialData.valid_from),
            valid_until: validIndefinitely ? '' : formatDateForInput(initialData.valid_until),
            status: initialData.status?.toLowerCase() as any,
          }
        : {
            code: '',
            discount_type: DiscountType.FIXED,
            discount_amount: '',
            max_uses: 1,
            valid_from: '',
            valid_until: '',
            valid_indefinitely: false,
          },
  });

  const handleSubmit = async (data: CreateVoucherFormData | UpdateVoucherFormData) => {
    try {
      setError(null);

      // Clean up the data before sending
      const cleanedData = { ...data };

      // For create mode, handle indefinite dates
      if ('valid_indefinitely' in cleanedData) {
        if (cleanedData.valid_indefinitely) {
          delete cleanedData.valid_from;
          delete cleanedData.valid_until;
        }
        delete cleanedData.valid_indefinitely;
      }

      await onSubmit(cleanedData);
    } catch (err: any) {
      setError(err.message || `Failed to ${mode} voucher`);
    }
  };

  return (
    <div className="space-y-6">
      {error && (
        <Alert variant="destructive">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      <Form {...form}>
        <form onSubmit={form.handleSubmit(handleSubmit)} className="space-y-4">
          <FormField
            control={form.control}
            name="code"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Voucher Code</FormLabel>
                <FormControl>
                  <Input
                    placeholder="SUMMER2024"
                    className="font-mono"
                    {...field}
                    onChange={(e) => field.onChange(e.target.value.toUpperCase())}
                  />
                </FormControl>
                <FormDescription>
                  Use uppercase letters, numbers, hyphens, and underscores only
                </FormDescription>
                <FormMessage />
              </FormItem>
            )}
          />

          {mode === 'create' && (
            <div className="space-y-4">
              <div>
                <FormLabel>Discount Type</FormLabel>
                <Select
                  value={discountType}
                  onValueChange={(value: DiscountType) => {
                    setDiscountType(value);
                    form.setValue('discount_type', value);
                  }}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select discount type" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value={DiscountType.FIXED}>Fixed Amount ($)</SelectItem>
                    <SelectItem value={DiscountType.PERCENTAGE}>Percentage (%)</SelectItem>
                  </SelectContent>
                </Select>
                <FormDescription>
                  Choose whether the discount is a fixed amount or a percentage
                </FormDescription>
              </div>
            </div>
          )}

          {mode === 'edit' && (
            <div className="space-y-2">
              <FormLabel>Discount Type</FormLabel>
              <div className="px-3 py-2 border rounded-md bg-muted text-muted-foreground">
                {discountType === DiscountType.PERCENTAGE
                  ? 'Percentage (%)'
                  : 'Fixed Amount ($)'}
              </div>
              <FormDescription>Discount type cannot be changed after creation</FormDescription>
            </div>
          )}

          <div className="space-y-4">

            <FormField
              control={form.control}
              name="discount_amount"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>
                    {discountType === DiscountType.PERCENTAGE ? 'Discount Percentage' : 'Discount Amount'}
                  </FormLabel>
                  <FormControl>
                    <div className="relative">
                      {discountType === DiscountType.FIXED && (
                        <span className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground">
                          $
                        </span>
                      )}
                      <Input
                        type="number"
                        step={discountType === DiscountType.PERCENTAGE ? '1' : '0.01'}
                        min="0"
                        max={discountType === DiscountType.PERCENTAGE ? '100' : undefined}
                        placeholder={discountType === DiscountType.PERCENTAGE ? '10' : '10.00'}
                        className={discountType === DiscountType.FIXED ? 'pl-7' : ''}
                        {...field}
                      />
                      {discountType === DiscountType.PERCENTAGE && (
                        <span className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground">
                          %
                        </span>
                      )}
                    </div>
                  </FormControl>
                  <FormDescription>
                    {discountType === DiscountType.PERCENTAGE
                      ? 'Enter percentage (0-100)'
                      : 'Enter the discount amount in dollars'}
                  </FormDescription>
                  <FormMessage />
                </FormItem>
              )}
            />
          </div>

          <FormField
            control={form.control}
            name="max_uses"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Maximum Uses</FormLabel>
                <FormControl>
                  <Input
                    type="number"
                    placeholder="100"
                    {...field}
                    onChange={(e) => field.onChange(parseInt(e.target.value) || 1)}
                  />
                </FormControl>
                <FormDescription>
                  Maximum number of times this voucher can be used
                </FormDescription>
                <FormMessage />
              </FormItem>
            )}
          />

          <div className="space-y-4">
            <div className="flex items-center space-x-2">
              <Checkbox
                id="valid-indefinitely"
                checked={validIndefinitely}
                onCheckedChange={(checked) => {
                  setValidIndefinitely(checked as boolean);
                  form.setValue('valid_indefinitely', checked as boolean);
                  if (checked) {
                    // Clear the date fields when checking "Valid Indefinitely"
                    form.setValue('valid_from', '');
                    form.setValue('valid_until', '');
                  }
                }}
              />
              <label
                htmlFor="valid-indefinitely"
                className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70 cursor-pointer"
              >
                Valid Indefinitely
              </label>
            </div>
            <FormDescription>
              Check this if the voucher should not have an expiration date
            </FormDescription>

            {!validIndefinitely && (
              <div className="grid grid-cols-2 gap-4">
                <FormField
                  control={form.control}
                  name="valid_from"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Valid From</FormLabel>
                      <FormControl>
                        <Input type="datetime-local" {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <FormField
                  control={form.control}
                  name="valid_until"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Valid Until</FormLabel>
                      <FormControl>
                        <Input type="datetime-local" {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
              </div>
            )}
          </div>

          {mode === 'edit' && (
            <FormField
              control={form.control}
              name="status"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Status</FormLabel>
                  <Select
                    value={field.value}
                    onValueChange={field.onChange}
                  >
                    <FormControl>
                      <SelectTrigger>
                        <SelectValue placeholder="Select status" />
                      </SelectTrigger>
                    </FormControl>
                    <SelectContent>
                      <SelectItem value="active">Active</SelectItem>
                      <SelectItem value="used">Used</SelectItem>
                      <SelectItem value="expired">Expired</SelectItem>
                    </SelectContent>
                  </Select>
                  <FormDescription>
                    Change the voucher status
                  </FormDescription>
                  <FormMessage />
                </FormItem>
              )}
            />
          )}

          <div className="flex gap-4">
            <Button type="submit" disabled={isLoading}>
              {isLoading
                ? mode === 'edit'
                  ? 'Updating...'
                  : 'Creating...'
                : mode === 'edit'
                ? 'Update Voucher'
                : 'Create Voucher'}
            </Button>
            <Button
              type="button"
              variant="outline"
              onClick={() =>
                router.push(
                  mode === 'edit' && initialData
                    ? `${AppRoute.VOUCHER_DETAIL}/${initialData.id}`
                    : AppRoute.VOUCHERS
                )
              }
              disabled={isLoading}
            >
              Cancel
            </Button>
          </div>
        </form>
      </Form>
    </div>
  );
}
