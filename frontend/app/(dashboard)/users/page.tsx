'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { usersApi } from '@/lib/api/users';
import { User } from '@/types/user';
import { UserList } from '@/components/users/user-list';
import { Button } from '@/components/ui/button';
import { AppRoute } from '@/lib/constants/routes';

export default function UsersPage() {
  const [users, setUsers] = useState<User[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadUsers();
  }, []);

  const loadUsers = async () => {
    try {
      setIsLoading(true);
      const response = await usersApi.getUsers();
      setUsers(response.results);
    } catch (err: any) {
      setError(err.message || 'Failed to load users');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Users</h1>
          <p className="text-muted-foreground">Manage system users</p>
        </div>
        <Link href={AppRoute.USER_NEW}>
          <Button>Create User</Button>
        </Link>
      </div>

      {isLoading ? (
        <div className="text-center py-8">Loading users...</div>
      ) : error ? (
        <div className="text-center py-8 text-destructive">{error}</div>
      ) : (
        <UserList users={users} />
      )}
    </div>
  );
}
