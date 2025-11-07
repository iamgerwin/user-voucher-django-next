'use client';

import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { useRouter } from 'next/navigation';
import { toast } from 'sonner';
import {
  createUserSchema,
  updateUserSchema,
  CreateUserFormData,
  UpdateUserFormData,
} from '@/lib/validations/user';
import { User } from '@/types/user';
import { Button } from '@/components/ui/button';
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
  FormDescription,
} from '@/components/ui/form';
import { Input } from '@/components/ui/input';
import { AppRoute } from '@/lib/constants/routes';

interface UserFormProps {
  mode?: 'create' | 'edit';
  initialData?: User;
  onSubmit: (data: CreateUserFormData | UpdateUserFormData) => Promise<void>;
  isLoading?: boolean;
}

export function UserForm({
  mode = 'create',
  initialData,
  onSubmit,
  isLoading = false,
}: UserFormProps) {
  const router = useRouter();

  const form = useForm<CreateUserFormData | UpdateUserFormData>({
    resolver: zodResolver(mode === 'edit' ? updateUserSchema : createUserSchema),
    defaultValues:
      mode === 'edit' && initialData
        ? {
            username: initialData.username,
            email: initialData.email,
            first_name: initialData.first_name || '',
            last_name: initialData.last_name || '',
            is_active: initialData.is_active,
            is_staff: initialData.is_staff,
          }
        : {
            username: '',
            email: '',
            password: '',
            first_name: '',
            last_name: '',
            is_active: true,
            is_staff: false,
          },
  });

  const handleSubmit = async (data: CreateUserFormData | UpdateUserFormData) => {
    try {
      await onSubmit(data);
      toast.success(
        mode === 'edit'
          ? 'User updated successfully'
          : 'User created successfully'
      );
    } catch (err: any) {
      toast.error(err.message || `Failed to ${mode} user`);
      throw err;
    }
  };

  return (
    <div className="space-y-6">
      <Form {...form}>
        <form onSubmit={form.handleSubmit(handleSubmit)} className="space-y-4">
          <FormField
            control={form.control}
            name="username"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Username</FormLabel>
                <FormControl>
                  <Input placeholder="Enter username" {...field} />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />

          <FormField
            control={form.control}
            name="email"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Email</FormLabel>
                <FormControl>
                  <Input type="email" placeholder="Enter email" {...field} />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />

          <div className="grid grid-cols-2 gap-4">
            <FormField
              control={form.control}
              name="first_name"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>First Name</FormLabel>
                  <FormControl>
                    <Input placeholder="First name" {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="last_name"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Last Name</FormLabel>
                  <FormControl>
                    <Input placeholder="Last name" {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
          </div>

          {mode === 'create' && (
            <FormField
              control={form.control}
              name="password"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Password</FormLabel>
                  <FormControl>
                    <Input
                      type="password"
                      placeholder="Enter password"
                      {...field}
                    />
                  </FormControl>
                  <FormDescription>
                    Must be at least 8 characters with uppercase, lowercase, and number
                  </FormDescription>
                  <FormMessage />
                </FormItem>
              )}
            />
          )}

          <div className="flex gap-4">
            <Button type="submit" disabled={isLoading}>
              {isLoading
                ? mode === 'edit'
                  ? 'Updating...'
                  : 'Creating...'
                : mode === 'edit'
                ? 'Update User'
                : 'Create User'}
            </Button>
            <Button
              type="button"
              variant="outline"
              onClick={() =>
                router.push(
                  mode === 'edit' && initialData
                    ? `${AppRoute.USER_DETAIL}/${initialData.id}`
                    : AppRoute.USERS
                )
              }
              disabled={isLoading}
            >
              Cancel
            </Button>
          </div>
        </form>
      </Form>
    </div>
  );
}
