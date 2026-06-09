"use client";
import { useEffect } from "react";
import { useRouter } from "next/navigation";

export default function HomePage() {
  const router = useRouter();
  useEffect(() => {
    const token = localStorage.getItem("access_token");
    router.replace(token ? "/chat" : "/login");
  }, [router]);

  return <div className="p-8 text-muted-foreground">Yo&apos;naltirilmoqda...</div>;
}
