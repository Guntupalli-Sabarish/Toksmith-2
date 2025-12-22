import { AuthGuard } from "@/components/auth-guard";
import { DashboardShell } from "@/components/dashboard";

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <AuthGuard requireAuth={true}>
      <DashboardShell>{children}</DashboardShell>
    </AuthGuard>
  );
}
