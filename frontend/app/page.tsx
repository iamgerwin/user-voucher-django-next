import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { AppRoute } from '@/lib/constants/routes';

export default function Home() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-muted/40">
      <div className="max-w-3xl space-y-8 text-center">
        <div className="space-y-4">
          <h1 className="text-5xl font-bold tracking-tight">
            Voucher Management System
          </h1>
          <p className="text-xl text-muted-foreground">
            A modern system for managing users and discount vouchers
          </p>
        </div>

        <div className="flex justify-center gap-4">
          <Link href={AppRoute.LOGIN}>
            <Button size="lg">Login</Button>
          </Link>
          <Link href={AppRoute.REGISTER}>
            <Button size="lg" variant="outline">
              Register
            </Button>
          </Link>
        </div>

        <div className="pt-8 text-sm text-muted-foreground">
          <p>Built with Next.js 16 and Django REST Framework</p>
        </div>
      </div>
    </div>
  );
}
