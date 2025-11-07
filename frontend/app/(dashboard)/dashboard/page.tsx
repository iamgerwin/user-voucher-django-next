'use client';

import { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { usersApi } from '@/lib/api/users';
import { vouchersApi } from '@/lib/api/vouchers';
import { VoucherStatus } from '@/lib/constants/enums';

export default function DashboardPage() {
  const [stats, setStats] = useState({
    totalUsers: 0,
    totalVouchers: 0,
    activeVouchers: 0,
  });
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    try {
      setIsLoading(true);

      // Fetch users and vouchers data
      const [usersResponse, vouchersResponse] = await Promise.all([
        usersApi.getUsers(),
        vouchersApi.getVouchers(),
      ]);

      // Count active vouchers
      const activeVouchers = vouchersResponse.results.filter(
        (voucher) => voucher.status === VoucherStatus.ACTIVE
      ).length;

      setStats({
        totalUsers: usersResponse.count,
        totalVouchers: vouchersResponse.count,
        activeVouchers,
      });
    } catch (error) {
      console.error('Failed to load dashboard stats:', error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Dashboard</h1>
        <p className="text-muted-foreground">
          Welcome to the Voucher Management System
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        <Card>
          <CardHeader>
            <CardTitle>Total Users</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-bold">
              {isLoading ? '...' : stats.totalUsers}
            </p>
            <p className="text-sm text-muted-foreground">Registered users</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Total Vouchers</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-bold">
              {isLoading ? '...' : stats.totalVouchers}
            </p>
            <p className="text-sm text-muted-foreground">Created vouchers</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Active Vouchers</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-bold">
              {isLoading ? '...' : stats.activeVouchers}
            </p>
            <p className="text-sm text-muted-foreground">Currently active</p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
