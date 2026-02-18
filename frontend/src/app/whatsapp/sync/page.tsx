"use client";

import { useEffect, useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useAuth } from "@/contexts/AuthContext";
import { evolutionApi } from "@/lib/api";

interface RawChat {
  remoteJid?: string;
  name?: string;
  pushName?: string;
  unreadCount?: number;
  lastMessageTime?: number;
  [key: string]: any;
}

export default function SyncPage() {
  const { user, loading, token, logout } = useAuth();
  const router = useRouter();

  const [chats, setChats] = useState<RawChat[]>([]);
  const [selectedJid, setSelectedJid] = useState<string | null>(null);
  const [messagesRaw, setMessagesRaw] = useState<string>("");
  const [chatsRaw, setChatsRaw] = useState<string>("");
  const [loadingChats, setLoadingChats] = useState(false);
  const [loadingMessages, setLoadingMessages] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadChats = useCallback(async () => {
    if (!token) return;
    setLoadingChats(true);
    setError(null);
    setChatsRaw("");
    setChats([]);

    try {
      const result = await evolutionApi.getChatsRaw(token);
      setChatsRaw(JSON.stringify(result.raw, null, 2));

      const parsed: RawChat[] = Array.isArray(result.raw) ? result.raw : [];
      const filtered = parsed.filter(
        (c) => !(c.remoteJid || "").includes("@g.us")
      );
      setChats(filtered);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load chats");
    } finally {
      setLoadingChats(false);
    }
  }, [token]);

  useEffect(() => {
    if (!loading && !user) {
      router.push("/login");
    }
  }, [user, loading, router]);

  useEffect(() => {
    if (token) loadChats();
  }, [token, loadChats]);

  const handleOpenChat = async (remoteJid: string) => {
    if (!token) return;
    setSelectedJid(remoteJid);
    setLoadingMessages(true);
    setMessagesRaw("");
    setError(null);

    try {
      const result = await evolutionApi.getChatMessagesRaw(token, remoteJid, 50);
      setMessagesRaw(JSON.stringify(result.raw, null, 2));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load messages");
    } finally {
      setLoadingMessages(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-100 dark:bg-gray-900 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  if (!user) return null;

  return (
    <div className="min-h-screen bg-gray-100 dark:bg-gray-900">
      <nav className="bg-white dark:bg-gray-800 shadow">
        <div className="max-w-6xl mx-auto px-4 py-4 flex justify-between items-center">
          <Link href="/dashboard" className="text-xl font-bold text-indigo-600 dark:text-indigo-400">
            No Lose
          </Link>
          <div className="flex items-center gap-4">
            <Link href="/dashboard" className="text-gray-700 dark:text-gray-300 hover:text-indigo-600">
              Dashboard
            </Link>
            <Link href="/whatsapp" className="text-gray-700 dark:text-gray-300 hover:text-indigo-600">
              WhatsApp
            </Link>
            <button
              onClick={() => { logout(); router.push("/"); }}
              className="text-gray-700 dark:text-gray-300 hover:text-red-600"
            >
              Logout
            </button>
          </div>
        </div>
      </nav>

      <main className="max-w-6xl mx-auto px-4 py-8">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">Chats Browser</h1>

        {error && (
          <pre className="bg-red-100 dark:bg-red-900 text-red-800 dark:text-red-200 p-4 rounded mb-4 whitespace-pre-wrap text-sm">
            {error}
          </pre>
        )}

        <button
          onClick={loadChats}
          disabled={loadingChats}
          className="mb-6 px-6 py-2 bg-indigo-600 text-white rounded-lg font-medium hover:bg-indigo-700 disabled:opacity-50 transition"
        >
          {loadingChats ? "Loading..." : "Reload Chats"}
        </button>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Chat list */}
          <div className="lg:col-span-1">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
              Chats ({chats.length})
            </h2>
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow max-h-[70vh] overflow-y-auto">
              {chats.length === 0 && !loadingChats && (
                <p className="text-gray-500 dark:text-gray-400 p-4 text-sm">
                  Loading chats...
                </p>
              )}
              {chats.map((chat, idx) => {
                const jid = chat.remoteJid || "";
                const name = chat.name || chat.pushName || jid.split("@")[0];
                const isSelected = selectedJid === jid;
                return (
                  <div
                    key={jid || idx}
                    onClick={() => handleOpenChat(jid)}
                    className={`p-3 border-b dark:border-gray-700 cursor-pointer text-sm transition ${
                      isSelected
                        ? "bg-indigo-50 dark:bg-indigo-900/40"
                        : "hover:bg-gray-50 dark:hover:bg-gray-700/50"
                    }`}
                  >
                    <p className="font-medium text-gray-900 dark:text-white truncate">{name}</p>
                    <p className="text-gray-500 dark:text-gray-400 text-xs truncate">{jid}</p>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Raw messages output */}
          <div className="lg:col-span-2">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
              {selectedJid ? `Messages: ${selectedJid}` : "Messages"}
            </h2>
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4 max-h-[70vh] overflow-auto">
              {loadingMessages ? (
                <p className="text-gray-500 dark:text-gray-400">Loading messages...</p>
              ) : messagesRaw ? (
                <pre className="text-xs text-gray-800 dark:text-gray-200 whitespace-pre-wrap break-words font-mono">
                  {messagesRaw}
                </pre>
              ) : (
                <p className="text-gray-500 dark:text-gray-400 text-sm">
                  Select a chat to view raw messages from the API
                </p>
              )}
            </div>
          </div>
        </div>

        {/* Raw chats response */}
        {chatsRaw && (
          <details className="mt-8">
            <summary className="cursor-pointer text-gray-700 dark:text-gray-300 font-medium mb-2">
              Raw chats API response
            </summary>
            <pre className="bg-white dark:bg-gray-800 rounded-lg shadow p-4 text-xs text-gray-800 dark:text-gray-200 whitespace-pre-wrap break-words font-mono max-h-96 overflow-auto">
              {chatsRaw}
            </pre>
          </details>
        )}
      </main>
    </div>
  );
}
