'use client';

import { useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';
import { vouchersApi } from '@/lib/api/vouchers';
import { VoucherForm } from '@/components/vouchers/voucher-form';
import { CreateVoucherFormData } from '@/lib/validations/voucher';
import { AppRoute } from '@/lib/constants/routes';
import { useAuth } from '@/hooks/use-auth';
import { UserRole } from '@/types/user';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { AuditLogService } from '@/lib/audit-log';

export default function NewVoucherPage() {
  const router = useRouter();
  const { user, isLoading: authLoading } = useAuth();
  const [isLoading, setIsLoading] = useState(false);
  const [isAuthorized, setIsAuthorized] = useState(false);

  useEffect(() => {
    // Wait for auth to finish loading
    if (authLoading) {
      return;
    }

    // Check if user has permission to create vouchers
    if (!user) {
      router.push(AppRoute.LOGIN);
      return;
    }

    const canCreateVouchers = user.role === UserRole.ADMIN || user.role === UserRole.MANAGER;

    if (!canCreateVouchers) {
      // Redirect to vouchers list if user doesn't have permission
      router.push(AppRoute.VOUCHERS);
      return;
    }

    setIsAuthorized(true);
  }, [user, authLoading, router]);

  if (authLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-muted-foreground">Loading...</div>
      </div>
    );
  }

  if (!isAuthorized) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <Alert variant="destructive" className="max-w-md">
          <AlertDescription>
            You don't have permission to create vouchers. Only administrators and managers can create vouchers.
          </AlertDescription>
        </Alert>
      </div>
    );
  }

  const handleSubmit = async (data: CreateVoucherFormData) => {
    setIsLoading(true);
    try {
      const voucher = await vouchersApi.createVoucher(data);

      // Log the creation
      if (user) {
        AuditLogService.logVoucherCreate(
          voucher.id,
          voucher.code,
          user.username,
          user.id
        );
      }

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
