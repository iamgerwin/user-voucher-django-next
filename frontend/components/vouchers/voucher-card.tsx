'use client';

import Link from 'next/link';
import { Voucher } from '@/types/voucher';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { AppRoute } from '@/lib/constants/routes';
import { format } from 'date-fns';

interface VoucherCardProps {
  voucher: Voucher;
}

const statusVariant = {
  active: 'default' as const,
  used: 'secondary' as const,
  expired: 'destructive' as const,
};

export function VoucherCard({ voucher }: VoucherCardProps) {
  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg font-mono">{voucher.code}</CardTitle>
          <Badge variant={statusVariant[voucher.status]}>
            {voucher.status.toUpperCase()}
          </Badge>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-2">
          <p className="text-2xl font-bold">${voucher.discount_amount}</p>
          <p className="text-sm">
            <span className="font-medium">Usage:</span> {voucher.used_count} / {voucher.max_uses}
          </p>
          <p className="text-sm">
            <span className="font-medium">Valid From:</span>{' '}
            {format(new Date(voucher.valid_from), 'MMM dd, yyyy')}
          </p>
          <p className="text-sm">
            <span className="font-medium">Valid Until:</span>{' '}
            {format(new Date(voucher.valid_until), 'MMM dd, yyyy')}
          </p>
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
