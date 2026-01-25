const API_BASE = process.env.NEXT_PUBLIC_API_URL || "/api";

export interface User {
  id: number;
  email: string;
  name: string;
  is_active: boolean;
  created_at: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
}

// Evolution API Types
export interface InstanceStatus {
  instance_name: string;
  status: "disconnected" | "qr" | "connecting" | "connected";
  phone_number?: string;
  profile_name?: string;
  qr_code?: string;
  last_connected_at?: string;
}

export interface QRCodeResponse {
  qr_code: string;
  instance_name: string;
}

export interface SyncResult {
  synced_count: number;
  message: string;
}

export interface Contact {
  id: number;
  wa_id: string;
  name?: string;
  profile_name?: string;
  evolution_remote_jid?: string;
}

export interface ChatInfo {
  id: string;
  name?: string;
  unread_count: number;
  last_message_time?: string;
}

export interface Message {
  id: number;
  type: string;
  content?: string;
  is_outbound: boolean;
  status: string;
  timestamp?: string;
  source: string;
}

export async function login(email: string, password: string): Promise<AuthResponse> {
  const response = await fetch(`${API_BASE}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Login failed");
  }

  return response.json();
}

export async function register(email: string, password: string, name: string): Promise<User> {
  const response = await fetch(`${API_BASE}/auth/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password, name }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Registration failed");
  }

  return response.json();
}

export async function getMe(token: string): Promise<User> {
  const response = await fetch(`${API_BASE}/auth/me`, {
    headers: { Authorization: `Bearer ${token}` },
  });

  if (!response.ok) {
    throw new Error("Failed to fetch user");
  }

  return response.json();
}

export async function updateProfile(token: string, name: string): Promise<User> {
  const response = await fetch(`${API_BASE}/auth/me?name=${encodeURIComponent(name)}`, {
    method: "PUT",
    headers: { Authorization: `Bearer ${token}` },
  });

  if (!response.ok) {
    throw new Error("Failed to update profile");
  }

  return response.json();
}

// ==================== Evolution API ====================

async function authFetch(token: string, endpoint: string, options: RequestInit = {}) {
  const response = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
      ...options.headers,
    },
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Request failed" }));
    throw new Error(error.detail || "Request failed");
  }

  return response.json();
}

export const evolutionApi = {
  // Instance Management
  createInstance: (token: string): Promise<InstanceStatus> =>
    authFetch(token, "/evolution/instance/create", { method: "POST" }),

  getStatus: (token: string): Promise<InstanceStatus> =>
    authFetch(token, "/evolution/instance/status"),

  getQRCode: (token: string): Promise<QRCodeResponse> =>
    authFetch(token, "/evolution/instance/qrcode"),

  disconnect: (token: string): Promise<{ message: string }> =>
    authFetch(token, "/evolution/instance/disconnect", { method: "DELETE" }),

  // Sync Operations
  syncContacts: (token: string): Promise<SyncResult> =>
    authFetch(token, "/evolution/sync/contacts", { method: "POST" }),

  syncChats: (token: string): Promise<{ chats: ChatInfo[]; total: number }> =>
    authFetch(token, "/evolution/sync/chats", { method: "POST" }),

  syncMessages: (token: string, contactId: number, limit: number = 30): Promise<SyncResult> =>
    authFetch(token, `/evolution/sync/messages/${contactId}?limit=${limit}`, { method: "POST" }),

  // Data
  getContacts: (token: string): Promise<{ contacts: Contact[]; total: number }> =>
    authFetch(token, "/evolution/contacts"),

  getMessages: (
    token: string,
    contactId: number
  ): Promise<{ messages: Message[]; contact: Contact }> =>
    authFetch(token, `/evolution/messages/${contactId}`),

  // Messaging
  sendText: (
    token: string,
    phoneNumber: string,
    text: string
  ): Promise<{ success: boolean; message_id?: string }> =>
    authFetch(token, "/evolution/send/text", {
      method: "POST",
      body: JSON.stringify({ phone_number: phoneNumber, text }),
    }),
};
