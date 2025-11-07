'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { toast } from 'sonner';
import { vouchersApi } from '@/lib/api/vouchers';
import { Voucher } from '@/types/voucher';
import { VoucherList } from '@/components/vouchers/voucher-list';
import { Button } from '@/components/ui/button';
import { AppRoute } from '@/lib/constants/routes';
import { useAuth } from '@/hooks/use-auth';
import { UserRole } from '@/types/user';

export default function VouchersPage() {
  const { user } = useAuth();
  const [vouchers, setVouchers] = useState<Voucher[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Check if user can create vouchers
  const canCreateVouchers = user && (user.role === UserRole.ADMIN || user.role === UserRole.MANAGER);

  useEffect(() => {
    loadVouchers();
  }, []);

  const loadVouchers = async () => {
    try {
      setIsLoading(true);
      const response = await vouchersApi.getVouchers();
      setVouchers(response.results);
    } catch (err: any) {
      setError(err.message || 'Failed to load vouchers');
    } finally {
      setIsLoading(false);
    }
  };

  const handleBulkDelete = async (ids: number[]) => {
    try {
      // Optimistically remove from UI
      const previousVouchers = vouchers;
      setVouchers(vouchers.filter((v) => !ids.includes(v.id)));

      await vouchersApi.bulkDeleteVouchers(ids);
      toast.success(`Successfully deleted ${ids.length} voucher${ids.length > 1 ? 's' : ''}`);

      // Reload to ensure consistency
      await loadVouchers();
    } catch (err: any) {
      toast.error(err.message || 'Failed to delete vouchers');
      // Reload on error to restore correct state
      await loadVouchers();
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Vouchers</h1>
          <p className="text-muted-foreground">Manage discount vouchers</p>
        </div>
        {canCreateVouchers && (
          <Link href={AppRoute.VOUCHER_NEW}>
            <Button>Create Voucher</Button>
          </Link>
        )}
      </div>

      {isLoading ? (
        <div className="text-center py-8">Loading vouchers...</div>
      ) : error ? (
        <div className="text-center py-8 text-destructive">{error}</div>
      ) : (
        <VoucherList vouchers={vouchers} onBulkDelete={handleBulkDelete} />
      )}
    </div>
  );
}
