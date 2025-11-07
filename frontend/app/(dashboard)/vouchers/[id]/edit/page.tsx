'use client';

import { use, useEffect, useState, useOptimistic, startTransition } from 'react';
import { useRouter } from 'next/navigation';
import { vouchersApi } from '@/lib/api/vouchers';
import { Voucher } from '@/types/voucher';
import { UpdateVoucherFormData } from '@/lib/validations/voucher';
import { VoucherForm } from '@/components/vouchers/voucher-form';
import { AppRoute } from '@/lib/constants/routes';
import { useAuth } from '@/hooks/use-auth';
import { AuditLogService } from '@/lib/audit-log';

export default function EditVoucherPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);
  const router = useRouter();
  const { user } = useAuth();
  const [voucher, setVoucher] = useState<Voucher | null>(null);
  const [optimisticVoucher, setOptimisticVoucher] = useOptimistic(voucher);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadVoucher();
  }, [id]);

  const loadVoucher = async () => {
    try {
      setIsLoading(true);
      const voucherData = await vouchersApi.getVoucherById(parseInt(id));
      setVoucher(voucherData);
    } catch (err: any) {
      setError(err.message || 'Failed to load voucher');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmit = async (data: UpdateVoucherFormData) => {
    if (!voucher) return;

    try {
      setIsSaving(true);

      // Optimistically update the UI within a transition
      startTransition(() => {
        setOptimisticVoucher({
          ...voucher,
          ...data,
        });
      });

      // Perform the actual update
      const updatedVoucher = await vouchersApi.updateVoucher(parseInt(id), data);
      setVoucher(updatedVoucher);

      // Log the update
      if (user && voucher) {
        AuditLogService.logVoucherUpdate(
          updatedVoucher.id,
          updatedVoucher.code,
          user.username,
          user.id,
          data
        );
      }

      router.push(`${AppRoute.VOUCHER_DETAIL}/${id}`);
    } catch (err: any) {
      // Revert optimistic update on error
      startTransition(() => {
        setOptimisticVoucher(voucher);
      });
      setError(err.message || 'Failed to update voucher');
      throw err;
    } finally {
      setIsSaving(false);
    }
  };

  if (isLoading) {
    return <div className="text-center py-8">Loading voucher...</div>;
  }

  if (error || !voucher) {
    return (
      <div className="text-center py-8 text-destructive">
        {error || 'Voucher not found'}
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Edit Voucher</h1>
        <p className="text-muted-foreground">
          Update voucher information for {voucher.code}
        </p>
      </div>

      <VoucherForm
        mode="edit"
        initialData={optimisticVoucher || voucher}
        onSubmit={handleSubmit}
        isLoading={isSaving}
      />
    </div>
  );
}
