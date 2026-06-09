import { AuthGuard } from "@/components/AuthGuard";
import { Header } from "@/components/Header";

export default function ChatLayout({ children }: { children: React.ReactNode }) {
  return (
    <AuthGuard>
      <div className="flex flex-col h-screen">
        <Header />
        <div className="flex-1 min-h-0">{children}</div>
      </div>
    </AuthGuard>
  );
}
