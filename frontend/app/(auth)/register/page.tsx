"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { login, register } from "@/lib/auth";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card } from "@/components/ui/card";
import { toast } from "sonner";

export default function RegisterPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [fullName, setFullName] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    try {
      await register(email, password, fullName);
      await login(email, password);
      toast.success("Ro'yxatdan o'tdingiz");
      router.push("/chat");
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Xato");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center p-4">
      <Card className="w-full max-w-sm p-6 space-y-4">
        <h1 className="text-2xl font-bold">Ro&apos;yxatdan o&apos;tish</h1>
        <form onSubmit={handleSubmit} className="space-y-4">
          <Input
            type="text"
            placeholder="To'liq ism"
            value={fullName}
            onChange={(e) => setFullName(e.target.value)}
          />
          <Input
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
          <Input
            type="password"
            placeholder="Parol (kamida 8 belgi, katta harf, raqam)"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
          <Button type="submit" disabled={loading} className="w-full">
            {loading ? "Yaratilmoqda..." : "Ro'yxatdan o'tish"}
          </Button>
        </form>
        <p className="text-sm text-center text-muted-foreground">
          Akkauntingiz bormi?{" "}
          <Link href="/login" className="underline text-foreground">
            Kirish
          </Link>
        </p>
      </Card>
    </div>
  );
}
