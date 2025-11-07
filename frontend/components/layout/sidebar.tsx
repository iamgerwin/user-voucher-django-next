'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { cn } from '@/lib/utils';
import { AppRoute } from '@/lib/constants/routes';

const navItems = [
  {
    title: 'Dashboard',
    href: AppRoute.DASHBOARD,
  },
  {
    title: 'Users',
    href: AppRoute.USERS,
  },
  {
    title: 'Vouchers',
    href: AppRoute.VOUCHERS,
  },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-64 border-r bg-background">
      <nav className="space-y-2 p-4">
        {navItems.map((item) => (
          <Link
            key={item.href}
            href={item.href}
            className={cn(
              'block rounded-lg px-4 py-2 text-sm font-medium transition-colors hover:bg-accent hover:text-accent-foreground',
              pathname === item.href
                ? 'bg-accent text-accent-foreground'
                : 'text-muted-foreground'
            )}
          >
            {item.title}
          </Link>
        ))}
      </nav>
    </aside>
  );
}
