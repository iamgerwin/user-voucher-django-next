export function Footer() {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="border-t">
      <div className="container flex h-16 items-center justify-between">
        <p className="text-sm text-muted-foreground">
          Voucher System {currentYear}
        </p>
        <p className="text-sm text-muted-foreground">
          Built with Next.js and Django
        </p>
      </div>
    </footer>
  );
}
