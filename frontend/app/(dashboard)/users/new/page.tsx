'use client';

import { useRouter } from 'next/navigation';
import { usersApi } from '@/lib/api/users';
import { UserForm } from '@/components/users/user-form';
import { CreateUserFormData } from '@/lib/validations/user';
import { AppRoute } from '@/lib/constants/routes';
import { useState } from 'react';

export default function NewUserPage() {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (data: CreateUserFormData) => {
    setIsLoading(true);
    try {
      await usersApi.createUser(data);
      router.push(AppRoute.USERS);
    } catch (error) {
      console.error('Failed to create user:', error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Create User</h1>
        <p className="text-muted-foreground">Add a new user to the system</p>
      </div>

      <div className="max-w-2xl">
        <UserForm onSubmit={handleSubmit} isLoading={isLoading} />
      </div>
    </div>
  );
}
