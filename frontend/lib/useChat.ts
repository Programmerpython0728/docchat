"use client";
import { useCallback, useRef, useState } from "react";
import type { Source } from "./types";

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  sources?: Source[];
  streaming?: boolean;
}

const WS_URL = (process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1").replace(
  /^http/,
  "ws"
);

export function useChat(chatId?: number) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isStreaming, setIsStreaming] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);

  const sendMessage = useCallback(
    (content: string, documentIds?: number[], useHybrid = false) => {
      const token = localStorage.getItem("access_token");
      if (!token) return;

      const userMsg: ChatMessage = {
        id: `user-${Date.now()}`,
        role: "user",
        content,
      };
      const aiMsg: ChatMessage = {
        id: `ai-${Date.now()}`,
        role: "assistant",
        content: "",
        streaming: true,
      };
      setMessages((prev) => [...prev, userMsg, aiMsg]);
      setIsStreaming(true);

      const ws = new WebSocket(`${WS_URL}/chat/ws?token=${token}`);
      wsRef.current = ws;

      ws.onopen = () => {
        ws.send(
          JSON.stringify({
            type: "message",
            content,
            chat_id: chatId,
            document_ids: documentIds,
            hybrid: useHybrid,
          })
        );
      };

      ws.onmessage = (event) => {
        const data = JSON.parse(event.data);

        if (data.type === "sources") {
          setMessages((prev) =>
            prev.map((m) => (m.id === aiMsg.id ? { ...m, sources: data.sources } : m))
          );
        } else if (data.type === "token") {
          setMessages((prev) =>
            prev.map((m) =>
              m.id === aiMsg.id ? { ...m, content: m.content + data.content } : m
            )
          );
        } else if (data.type === "done") {
          setMessages((prev) =>
            prev.map((m) => (m.id === aiMsg.id ? { ...m, streaming: false } : m))
          );
          setIsStreaming(false);
          ws.close();
        }
      };

      ws.onerror = () => {
        setIsStreaming(false);
      };

      ws.onclose = () => {
        setIsStreaming(false);
      };
    },
    [chatId]
  );

  return { messages, sendMessage, isStreaming, setMessages };
}
