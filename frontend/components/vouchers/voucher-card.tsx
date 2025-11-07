'use client';

import Link from 'next/link';
import { Voucher } from '@/types/voucher';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { AppRoute } from '@/lib/constants/routes';
import { VoucherStatus } from '@/lib/constants/enums';
import { format } from 'date-fns';

interface VoucherCardProps {
  voucher: Voucher;
}

const statusVariant: Record<string, 'default' | 'secondary' | 'destructive'> = {
  [VoucherStatus.ACTIVE]: 'default',
  [VoucherStatus.USED]: 'secondary',
  [VoucherStatus.EXPIRED]: 'destructive',
  [VoucherStatus.CANCELLED]: 'destructive',
};

export function VoucherCard({ voucher }: VoucherCardProps) {
  // Determine discount display
  const discountDisplay = voucher.discount_percentage
    ? `${voucher.discount_percentage}%`
    : voucher.discount_amount
    ? `$${voucher.discount_amount}`
    : 'N/A';

  // Determine usage display
  const usageDisplay = voucher.usage_limit
    ? `${voucher.usage_count} / ${voucher.usage_limit}`
    : `${voucher.usage_count} (Unlimited)`;

  // Check if voucher is valid indefinitely (100 years in the future indicates indefinite)
  const validUntilDate = new Date(voucher.valid_until);
  const currentDate = new Date();
  const yearsDifference = validUntilDate.getFullYear() - currentDate.getFullYear();
  const isIndefinite = yearsDifference >= 50; // Consider 50+ years as indefinite

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg font-mono">{voucher.code}</CardTitle>
          <Badge variant={statusVariant[voucher.status] || 'default'}>
            {voucher.status.toUpperCase()}
          </Badge>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-2">
          <p className="text-2xl font-bold">{discountDisplay}</p>
          <p className="text-sm">
            <span className="font-medium">Usage:</span> {usageDisplay}
          </p>
          <div className="min-h-[2.5rem]">
            {isIndefinite ? (
              <p className="text-sm">
                <span className="font-medium">Validity:</span> Indefinite
              </p>
            ) : (
              <>
                <p className="text-sm">
                  <span className="font-medium">Valid From:</span>{' '}
                  {format(new Date(voucher.valid_from), 'MMM dd, yyyy')}
                </p>
                <p className="text-sm">
                  <span className="font-medium">Valid Until:</span>{' '}
                  {format(new Date(voucher.valid_until), 'MMM dd, yyyy')}
                </p>
              </>
            )}
          </div>
          <Link href={`${AppRoute.VOUCHER_DETAIL}/${voucher.id}`}>
            <Button variant="outline" size="sm" className="w-full mt-4">
              View Details
            </Button>
          </Link>
        </div>
      </CardContent>
    </Card>
  );
}
