# Voucher Management System - Frontend

A modern Next.js 16 frontend application for managing users and discount vouchers, built with TypeScript, Tailwind CSS, and shadcn/ui.

## Tech Stack

- **Framework**: Next.js 16.0.1 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **UI Components**: shadcn/ui
- **Form Handling**: React Hook Form
- **Validation**: Zod
- **HTTP Client**: Axios
- **Date Handling**: date-fns

## Project Structure

```
frontend/
├── app/                          # Next.js App Router
│   ├── (auth)/                  # Auth route group
│   │   ├── login/               # Login page
│   │   └── register/            # Registration page
│   ├── (dashboard)/             # Dashboard route group
│   │   ├── dashboard/           # Dashboard page
│   │   ├── users/               # User management
│   │   │   ├── [id]/           # User detail page
│   │   │   ├── new/            # Create user page
│   │   │   └── page.tsx        # Users list page
│   │   └── vouchers/            # Voucher management
│   │       ├── [id]/           # Voucher detail page
│   │       ├── new/            # Create voucher page
│   │       └── page.tsx        # Vouchers list page
│   ├── layout.tsx               # Root layout
│   └── page.tsx                 # Home page
├── components/                   # React components
│   ├── ui/                      # shadcn/ui components
│   ├── auth/                    # Authentication components
│   ├── layout/                  # Layout components
│   ├── users/                   # User-related components
│   └── vouchers/                # Voucher-related components
├── lib/                          # Library code
│   ├── api/                     # API client and endpoints
│   │   ├── client.ts           # Axios client with interceptors
│   │   ├── auth.ts             # Auth API functions
│   │   ├── users.ts            # Users API functions
│   │   └── vouchers.ts         # Vouchers API functions
│   ├── validations/             # Zod validation schemas
│   ├── constants/               # Constants and enums
│   └── utils.ts                 # Utility functions
├── types/                        # TypeScript type definitions
│   ├── auth.ts                  # Auth types
│   ├── user.ts                  # User types
│   └── voucher.ts               # Voucher types
└── hooks/                        # Custom React hooks
    ├── use-auth.ts              # Authentication hook
    └── use-api.ts               # API hook
```

## Getting Started

### Prerequisites

- Node.js 18+
- npm or yarn
- Django backend running on `http://localhost:8000`

### Installation

1. Install dependencies:
```bash
npm install
```

2. Configure environment variables:
Create a `.env.local` file:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

3. Start the development server:
```bash
npm run dev
```

4. Open [http://localhost:3000](http://localhost:3000) in your browser.

## Available Scripts

- `npm run dev` - Start development server with Turbopack
- `npm run build` - Build for production
- `npm start` - Start production server
- `npm run lint` - Run ESLint

## Features

### Authentication
- User login with JWT tokens
- User registration
- Automatic token refresh
- Protected routes

### User Management
- List all users
- View user details
- Create new users
- Search users

### Voucher Management
- List all vouchers
- View voucher details
- Create new vouchers
- Track voucher usage
- Filter by status (active, used, expired)

## API Integration

The frontend communicates with the Django REST API backend. The API client (`lib/api/client.ts`) includes:

- Automatic JWT token handling
- Token refresh on expiration
- Request/response interceptors
- Error handling

## Code Standards

### Enums
Use enums from `lib/constants/enums.ts` to avoid magic strings:
```typescript
import { ApiEndpoint, VoucherStatus } from '@/lib/constants/enums';
```

### Validation
All forms use Zod schemas for validation:
```typescript
import { loginSchema } from '@/lib/validations/auth';
```

### Components
- Use Server Components by default
- Add 'use client' directive only when needed (forms, hooks, interactivity)
- Follow component composition patterns
- Keep components small and focused

### TypeScript
- Define types in `types/` directory
- Use proper type inference
- Avoid `any` type
- Export types with interfaces

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `NEXT_PUBLIC_API_URL` | Backend API URL | `http://localhost:8000/api/v1` |

## Deployment

### Build for Production

```bash
npm run build
npm start
```

### Environment Setup

Ensure the following environment variables are set in production:
- `NEXT_PUBLIC_API_URL` - Your production API URL

## Development Guidelines

### Adding New Pages
1. Create page in appropriate route group
2. Use Server Components when possible
3. Add route constant to `lib/constants/routes.ts`

### Adding New API Endpoints
1. Define types in `types/`
2. Create API functions in `lib/api/`
3. Add endpoint constant to `lib/constants/enums.ts`
4. Create validation schema in `lib/validations/`

### Adding New Components
1. Place in appropriate directory under `components/`
2. Use TypeScript for props
3. Follow existing patterns
4. Keep components reusable

## Troubleshooting

### API Connection Issues
- Ensure backend is running on `http://localhost:8000`
- Check CORS configuration in Django
- Verify `.env.local` has correct API URL

### Build Errors
- Clear `.next` folder: `rm -rf .next`
- Clear node_modules: `rm -rf node_modules && npm install`
- Check TypeScript errors: `npx tsc --noEmit`

## Learn More

- [Next.js Documentation](https://nextjs.org/docs)
- [shadcn/ui Documentation](https://ui.shadcn.com)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [React Hook Form](https://react-hook-form.com)
- [Zod](https://zod.dev)
