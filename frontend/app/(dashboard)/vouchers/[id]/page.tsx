'use client';

import { use, useEffect, useState, useTransition } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { toast } from 'sonner';
import { vouchersApi } from '@/lib/api/vouchers';
import { Voucher } from '@/types/voucher';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { AppRoute } from '@/lib/constants/routes';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog';
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
  const router = useRouter();
  const [voucher, setVoucher] = useState<Voucher | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);

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

  const handleDelete = async () => {
    try {
      setIsDeleting(true);
      await vouchersApi.deleteVoucher(parseInt(id));
      toast.success('Voucher deleted successfully');
      router.push(AppRoute.VOUCHERS);
    } catch (err: any) {
      toast.error(err.message || 'Failed to delete voucher');
      setIsDeleting(false);
      setIsDeleteDialogOpen(false);
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
        <div className="flex items-center gap-3">
          <Link href={`${AppRoute.VOUCHERS}/${id}/edit`}>
            <Button variant="outline">Edit Voucher</Button>
          </Link>
          <Button
            variant="destructive"
            onClick={() => setIsDeleteDialogOpen(true)}
            disabled={isDeleting}
          >
            {isDeleting ? 'Deleting...' : 'Delete Voucher'}
          </Button>
          <Badge variant={statusVariant[voucher.status]}>
            {voucher.status.toUpperCase()}
          </Badge>
        </div>
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

      <AlertDialog open={isDeleteDialogOpen} onOpenChange={setIsDeleteDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Are you sure?</AlertDialogTitle>
            <AlertDialogDescription>
              This action cannot be undone. This will permanently delete the voucher
              <span className="font-semibold font-mono"> {voucher.code}</span> and all associated data.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel disabled={isDeleting}>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={handleDelete}
              disabled={isDeleting}
              className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
            >
              {isDeleting ? 'Deleting...' : 'Delete'}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}
