"use client";
import { useCallback, useEffect, useState } from "react";
import { apiFetch } from "@/lib/api";
import type { Document, DocumentList } from "@/lib/types";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { FileUpload } from "@/components/FileUpload";

const STATUS_LABEL: Record<Document["status"], string> = {
  pending: "kutilmoqda",
  processing: "indekslanmoqda",
  indexed: "tayyor",
  failed: "xato",
};

const STATUS_VARIANT: Record<
  Document["status"],
  "default" | "secondary" | "destructive" | "outline"
> = {
  pending: "secondary",
  processing: "secondary",
  indexed: "default",
  failed: "destructive",
};

export default function DocumentsPage() {
  const [docs, setDocs] = useState<Document[]>([]);
  const [loading, setLoading] = useState(true);

  const refetch = useCallback(async () => {
    try {
      const res = await apiFetch<DocumentList>("/documents/");
      setDocs(res.items);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    refetch();
  }, [refetch]);

  // Polling — pending/processing bo'lsa har 3 sekundda yangilash
  useEffect(() => {
    const hasProcessing = docs.some(
      (d) => d.status === "pending" || d.status === "processing"
    );
    if (!hasProcessing) return;

    const id = setInterval(refetch, 3000);
    return () => clearInterval(id);
  }, [docs, refetch]);

  return (
    <div className="p-8 max-w-3xl mx-auto space-y-6">
      <h1 className="text-2xl font-bold">Hujjatlar</h1>

      <FileUpload onUploaded={refetch} />

      {loading ? (
        <div className="space-y-3">
          {Array.from({ length: 3 }).map((_, i) => (
            <Skeleton key={i} className="h-20 w-full" />
          ))}
        </div>
      ) : docs.length === 0 ? (
        <div className="text-center py-12 text-muted-foreground">
          <p>Hali hujjat yo&apos;q</p>
          <p className="text-sm">Birinchi hujjatingizni yuklang</p>
        </div>
      ) : (
        <div className="space-y-3">
          {docs.map((doc) => (
            <Card key={doc.id} className="p-4 flex justify-between items-center">
              <div className="min-w-0 flex-1">
                <p className="font-medium truncate">{doc.filename}</p>
                <p className="text-sm text-muted-foreground">
                  {doc.file_size_mb} MB · {doc.chunk_count ?? 0} chunks
                  {doc.page_count ? ` · ${doc.page_count} pages` : ""}
                </p>
                {doc.error_message && (
                  <p className="text-xs text-destructive mt-1">
                    {doc.error_message}
                  </p>
                )}
              </div>
              <Badge variant={STATUS_VARIANT[doc.status]}>
                {STATUS_LABEL[doc.status]}
              </Badge>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
