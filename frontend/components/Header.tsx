"use client";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { logout } from "@/lib/auth";
import { Button } from "@/components/ui/button";

export function Header() {
  const router = useRouter();
  return (
    <header className="border-b p-4 flex justify-between items-center">
      <Link href="/chat" className="font-bold text-lg">
        DocChat
      </Link>
      <nav className="flex gap-4 items-center">
        <Link href="/chat" className="hover:underline">
          Chat
        </Link>
        <Link href="/documents" className="hover:underline">
          Hujjatlar
        </Link>
        <Button
          variant="ghost"
          onClick={() => {
            logout();
            router.push("/login");
          }}
        >
          Chiqish
        </Button>
      </nav>
    </header>
  );
}
