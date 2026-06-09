"use client";
import { useCallback, useState } from "react";
import { uploadDocument } from "@/lib/upload";
import { Card } from "@/components/ui/card";
import { toast } from "sonner";

export function FileUpload({ onUploaded }: { onUploaded?: () => void }) {
  const [dragging, setDragging] = useState(false);
  const [progress, setProgress] = useState<number | null>(null);

  const handleFiles = useCallback(
    async (files: FileList) => {
      for (const file of Array.from(files)) {
        try {
          setProgress(0);
          await uploadDocument(file, setProgress);
          toast.success(`${file.name} yuklandi, indekslanmoqda`);
          onUploaded?.();
        } catch (e) {
          toast.error(e instanceof Error ? e.message : `${file.name} yuklanmadi`);
        } finally {
          setProgress(null);
        }
      }
    },
    [onUploaded]
  );

  return (
    <Card
      className={`p-8 border-2 border-dashed text-center cursor-pointer transition ${
        dragging ? "border-primary bg-muted" : ""
      }`}
      onDragOver={(e) => {
        e.preventDefault();
        setDragging(true);
      }}
      onDragLeave={() => setDragging(false)}
      onDrop={(e) => {
        e.preventDefault();
        setDragging(false);
        handleFiles(e.dataTransfer.files);
      }}
      onClick={() => document.getElementById("file-input")?.click()}
    >
      <input
        id="file-input"
        type="file"
        className="hidden"
        accept=".pdf,.docx,.txt,.md"
        multiple
        onChange={(e) => e.target.files && handleFiles(e.target.files)}
      />
      {progress !== null ? (
        <p>Yuklanmoqda... {progress}%</p>
      ) : (
        <p className="text-muted-foreground">
          Hujjat tashlang yoki bosing (PDF, DOCX, TXT, MD)
        </p>
      )}
    </Card>
  );
}
