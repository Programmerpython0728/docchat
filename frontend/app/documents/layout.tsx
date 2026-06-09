import { AuthGuard } from "@/components/AuthGuard";
import { Header } from "@/components/Header";

export default function DocumentsLayout({ children }: { children: React.ReactNode }) {
  return (
    <AuthGuard>
      <Header />
      <div className="flex-1">{children}</div>
    </AuthGuard>
  );
}
