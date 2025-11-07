'use client';

import { Voucher } from '@/types/voucher';
import { VoucherCard } from './voucher-card';

interface VoucherListProps {
  vouchers: Voucher[];
}

export function VoucherList({ vouchers }: VoucherListProps) {
  if (vouchers.length === 0) {
    return (
      <div className="text-center py-8 text-muted-foreground">
        No vouchers found
      </div>
    );
  }

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
      {vouchers.map((voucher) => (
        <VoucherCard key={voucher.id} voucher={voucher} />
      ))}
    </div>
  );
}
