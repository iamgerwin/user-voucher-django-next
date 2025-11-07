'use client';

import { useRouter } from 'next/navigation';
import { vouchersApi } from '@/lib/api/vouchers';
import { VoucherForm } from '@/components/vouchers/voucher-form';
import { CreateVoucherFormData } from '@/lib/validations/voucher';
import { AppRoute } from '@/lib/constants/routes';
import { useState } from 'react';

export default function NewVoucherPage() {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (data: CreateVoucherFormData) => {
    setIsLoading(true);
    try {
      await vouchersApi.createVoucher(data);
      router.push(AppRoute.VOUCHERS);
    } catch (error) {
      console.error('Failed to create voucher:', error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Create Voucher</h1>
        <p className="text-muted-foreground">Add a new discount voucher</p>
      </div>

      <div className="max-w-2xl">
        <VoucherForm onSubmit={handleSubmit} isLoading={isLoading} />
      </div>
    </div>
  );
}
