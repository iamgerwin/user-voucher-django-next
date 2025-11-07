import Link from 'next/link';
import { RegisterForm } from '@/components/auth/register-form';
import { AppRoute } from '@/lib/constants/routes';

export default function RegisterPage() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-muted/40">
      <div className="w-full max-w-md p-8">
        <RegisterForm />
        <p className="mt-6 text-center text-sm text-muted-foreground">
          Already have an account?{' '}
          <Link
            href={AppRoute.LOGIN}
            className="font-medium text-primary hover:underline"
          >
            Login here
          </Link>
        </p>
      </div>
    </div>
  );
}
