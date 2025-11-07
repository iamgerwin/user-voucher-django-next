'use client';

import { use, useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { usersApi } from '@/lib/api/users';
import { User } from '@/types/user';
import { UpdateUserFormData } from '@/lib/validations/user';
import { UserForm } from '@/components/users/user-form';
import { AppRoute } from '@/lib/constants/routes';

export default function EditUserPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadUser();
  }, [id]);

  const loadUser = async () => {
    try {
      setIsLoading(true);
      const userData = await usersApi.getUserById(parseInt(id));
      setUser(userData);
    } catch (err: any) {
      setError(err.message || 'Failed to load user');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmit = async (data: UpdateUserFormData) => {
    try {
      setIsSaving(true);
      await usersApi.updateUser(parseInt(id), data);
      router.push(`${AppRoute.USER_DETAIL}/${id}`);
    } catch (err: any) {
      setError(err.message || 'Failed to update user');
      throw err;
    } finally {
      setIsSaving(false);
    }
  };

  if (isLoading) {
    return <div className="text-center py-8">Loading user...</div>;
  }

  if (error || !user) {
    return (
      <div className="text-center py-8 text-destructive">
        {error || 'User not found'}
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Edit User</h1>
        <p className="text-muted-foreground">
          Update user information for {user.username}
        </p>
      </div>

      <UserForm
        mode="edit"
        initialData={user}
        onSubmit={handleSubmit}
        isLoading={isSaving}
      />
    </div>
  );
}
