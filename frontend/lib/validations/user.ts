import { z } from 'zod';

export const createUserSchema = z.object({
  username: z
    .string()
    .min(3, 'Username must be at least 3 characters')
    .max(150, 'Username must be less than 150 characters')
    .regex(
      /^[\w.@+-]+$/,
      'Username can only contain letters, numbers, and @/./+/-/_ characters'
    ),
  email: z.string().email('Invalid email address'),
  password: z
    .string()
    .min(8, 'Password must be at least 8 characters')
    .regex(
      /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/,
      'Password must contain at least one uppercase letter, one lowercase letter, and one number'
    ),
  first_name: z.string().max(150).optional(),
  last_name: z.string().max(150).optional(),
  is_active: z.boolean().optional(),
  is_staff: z.boolean().optional(),
});

export const updateUserSchema = z.object({
  username: z
    .string()
    .min(3, 'Username must be at least 3 characters')
    .max(150, 'Username must be less than 150 characters')
    .regex(
      /^[\w.@+-]+$/,
      'Username can only contain letters, numbers, and @/./+/-/_ characters'
    )
    .optional(),
  email: z.string().email('Invalid email address').optional(),
  first_name: z.string().max(150).optional(),
  last_name: z.string().max(150).optional(),
  is_active: z.boolean().optional(),
  is_staff: z.boolean().optional(),
});

export type CreateUserFormData = z.infer<typeof createUserSchema>;
export type UpdateUserFormData = z.infer<typeof updateUserSchema>;
