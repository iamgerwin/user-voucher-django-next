'use client';

import Link from 'next/link';
import { User } from '@/types/user';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { AppRoute } from '@/lib/constants/routes';

interface UserCardProps {
  user: User;
}

export function UserCard({ user }: UserCardProps) {
  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg">{user.username}</CardTitle>
          <div className="flex gap-2">
            {user.is_staff && <Badge variant="secondary">Staff</Badge>}
            <Badge variant={user.is_active ? 'default' : 'destructive'}>
              {user.is_active ? 'Active' : 'Inactive'}
            </Badge>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-2">
          <p className="text-sm">
            <span className="font-medium">Name:</span> {user.first_name} {user.last_name}
          </p>
          <p className="text-sm">
            <span className="font-medium">Email:</span> {user.email}
          </p>
          <p className="text-sm text-muted-foreground">
            Joined: {new Date(user.date_joined).toLocaleDateString()}
          </p>
          <Link href={`${AppRoute.USER_DETAIL}/${user.id}`}>
            <Button variant="outline" size="sm" className="w-full mt-4">
              View Details
            </Button>
          </Link>
        </div>
      </CardContent>
    </Card>
  );
}
