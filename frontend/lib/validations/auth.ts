import { z } from 'zod';

export const loginSchema = z.object({
  username: z.string().min(1, 'Username is required'),
  password: z.string().min(1, 'Password is required'),
});

export const registerSchema = z.object({
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
  password2: z.string().min(1, 'Please confirm your password'),
  first_name: z.string().max(150).optional(),
  last_name: z.string().max(150).optional(),
}).refine((data) => data.password === data.password2, {
  message: 'Passwords do not match',
  path: ['password2'],
});

export type LoginFormData = z.infer<typeof loginSchema>;
export type RegisterFormData = z.infer<typeof registerSchema>;
