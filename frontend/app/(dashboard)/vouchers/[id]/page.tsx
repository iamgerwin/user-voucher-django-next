'use client';

import { use, useEffect, useState } from 'react';
import { vouchersApi } from '@/lib/api/vouchers';
import { Voucher } from '@/types/voucher';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { format } from 'date-fns';
import { VoucherStatus } from '@/lib/constants/enums';

const statusVariant: Record<string, 'default' | 'secondary' | 'destructive'> = {
  [VoucherStatus.ACTIVE]: 'default',
  [VoucherStatus.USED]: 'secondary',
  [VoucherStatus.EXPIRED]: 'destructive',
  [VoucherStatus.CANCELLED]: 'destructive',
};

export default function VoucherDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);
  const [voucher, setVoucher] = useState<Voucher | null>(null);
  const [isLoading, setIsLoading] = useState(true);
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

  // Check if voucher is valid indefinitely (100 years in the future indicates indefinite)
  const validUntilDate = new Date(voucher.valid_until);
  const currentDate = new Date();
  const yearsDifference = validUntilDate.getFullYear() - currentDate.getFullYear();
  const isIndefinite = yearsDifference >= 50; // Consider 50+ years as indefinite

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold font-mono">{voucher.code}</h1>
          <p className="text-muted-foreground">Voucher details and information</p>
        </div>
        <Badge variant={statusVariant[voucher.status]}>
          {voucher.status.toUpperCase()}
        </Badge>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Voucher Information</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <p className="text-sm font-medium text-muted-foreground">Code</p>
              <p className="text-lg font-mono">{voucher.code}</p>
            </div>
            <div>
              <p className="text-sm font-medium text-muted-foreground">Voucher Type</p>
              <p className="text-lg capitalize">{voucher.voucher_type?.replace('_', ' ')}</p>
            </div>
            <div>
              <p className="text-sm font-medium text-muted-foreground">Discount</p>
              <p className="text-lg font-bold">
                {voucher.discount_percentage
                  ? `${voucher.discount_percentage}%`
                  : voucher.discount_amount
                  ? `$${voucher.discount_amount}`
                  : 'N/A'}
              </p>
            </div>
            <div>
              <p className="text-sm font-medium text-muted-foreground">Usage</p>
              <p className="text-lg">
                {voucher.usage_limit
                  ? `${voucher.usage_count} / ${voucher.usage_limit}`
                  : `${voucher.usage_count} (Unlimited)`}
              </p>
            </div>
            <div>
              <p className="text-sm font-medium text-muted-foreground">Status</p>
              <Badge variant={statusVariant[voucher.status] || 'default'}>
                {voucher.status.toUpperCase()}
              </Badge>
            </div>
            <div>
              <p className="text-sm font-medium text-muted-foreground">Created By</p>
              <p className="text-lg">{voucher.created_by_name || 'Unknown'}</p>
            </div>
            {isIndefinite ? (
              <div className="col-span-2">
                <p className="text-sm font-medium text-muted-foreground">Validity Period</p>
                <p className="text-lg font-semibold">Indefinite</p>
              </div>
            ) : (
              <>
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Valid From</p>
                  <p className="text-lg">
                    {format(new Date(voucher.valid_from), 'PPP')}
                  </p>
                </div>
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Valid Until</p>
                  <p className="text-lg">
                    {format(new Date(voucher.valid_until), 'PPP')}
                  </p>
                </div>
              </>
            )}
            <div>
              <p className="text-sm font-medium text-muted-foreground">Created At</p>
              <p className="text-lg">
                {format(new Date(voucher.created_at), 'PPP')}
              </p>
            </div>
            <div>
              <p className="text-sm font-medium text-muted-foreground">Last Updated</p>
              <p className="text-lg">
                {format(new Date(voucher.updated_at), 'PPP')}
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
