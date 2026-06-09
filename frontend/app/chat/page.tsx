"use client";
import { useEffect, useRef, useState } from "react";
import { useChat } from "@/lib/useChat";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { ScrollArea } from "@/components/ui/scroll-area";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

export default function ChatPage() {
  const { messages, sendMessage, isStreaming } = useChat();
  const [input, setInput] = useState("");
  const [useHybrid, setUseHybrid] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    scrollRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  function handleSend() {
    if (!input.trim() || isStreaming) return;
    sendMessage(input, undefined, useHybrid);
    setInput("");
  }

  return (
    <div className="flex flex-col h-full max-w-3xl mx-auto w-full">
      <ScrollArea className="flex-1 p-4">
        {messages.length === 0 && (
          <div className="text-center py-12 text-muted-foreground">
            <p className="text-lg">Hujjatlaringiz bo&apos;yicha savol bering</p>
            <p className="text-sm mt-2">
              Avval <a className="underline" href="/documents">hujjatlar</a> sahifasidan PDF/DOCX yuklang
            </p>
          </div>
        )}
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`mb-4 flex ${
              msg.role === "user" ? "justify-end" : "justify-start"
            }`}
          >
            <div
              className={`inline-block p-3 rounded-lg max-w-[85%] ${
                msg.role === "user"
                  ? "bg-primary text-primary-foreground"
                  : "bg-muted"
              }`}
            >
              <div className="prose prose-sm max-w-none dark:prose-invert">
                <ReactMarkdown remarkPlugins={[remarkGfm]}>
                  {msg.content || (msg.streaming ? "..." : "")}
                </ReactMarkdown>
              </div>

              {msg.sources && msg.sources.length > 0 && (
                <div className="mt-2 pt-2 border-t border-current/20 text-xs space-y-1">
                  <p className="font-semibold">Manbalar:</p>
                  {msg.sources.map((s, i) => (
                    <p key={i} className="opacity-80">
                      [{i + 1}] {s.preview}...{" "}
                      <span className="font-mono">
                        ({(s.similarity * 100).toFixed(0)}%)
                      </span>
                    </p>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}
        <div ref={scrollRef} />
      </ScrollArea>

      <div className="p-4 border-t space-y-2">
        <label className="flex items-center gap-2 text-xs text-muted-foreground">
          <input
            type="checkbox"
            checked={useHybrid}
            onChange={(e) => setUseHybrid(e.target.checked)}
          />
          Hybrid search (vector + BM25)
        </label>
        <div className="flex gap-2">
          <Textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                handleSend();
              }
            }}
            placeholder="Savolingizni yozing... (Shift+Enter — yangi qator)"
            className="resize-none"
            rows={2}
          />
          <Button onClick={handleSend} disabled={isStreaming}>
            {isStreaming ? "..." : "Yuborish"}
          </Button>
        </div>
      </div>
    </div>
  );
}
