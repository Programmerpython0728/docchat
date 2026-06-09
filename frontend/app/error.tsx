"use client";
import { Button } from "@/components/ui/button";

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <div className="p-8 text-center min-h-screen flex flex-col justify-center items-center">
      <h2 className="text-xl font-bold mb-2">Xato yuz berdi</h2>
      <p className="text-muted-foreground mb-4">{error.message}</p>
      <Button onClick={reset}>Qayta urinish</Button>
    </div>
  );
}
