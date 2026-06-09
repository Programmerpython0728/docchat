// Backend Pydantic schemalardan moslashtirilgan
export interface User {
  id: number;
  email: string;
  full_name: string | null;
  is_active: boolean;
  is_superuser: boolean;
  created_at: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token?: string;
  token_type: string;
  expires_in: number;
}

export interface Document {
  id: number;
  filename: string;
  file_size: number;
  content_type: string;
  status: "pending" | "processing" | "indexed" | "failed";
  error_message: string | null;
  page_count: number | null;
  chunk_count: number | null;
  created_at: string;
  indexed_at: string | null;
  file_size_mb: number;
  is_ready: boolean;
}

export interface DocumentList {
  items: Document[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface Chat {
  id: number;
  title: string;
  user_id: number;
  message_count: number;
  last_message_at: string | null;
  created_at: string;
}

export interface Message {
  id: number;
  chat_id: number;
  role: "user" | "assistant" | "system";
  content: string;
  sources?: Source[];
  created_at: string;
}

export interface Source {
  chunk_id: number;
  document_id: number;
  preview: string;
  similarity: number;
}
