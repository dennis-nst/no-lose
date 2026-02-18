"use client";

import { useEffect, useState, useRef } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useAuth } from "@/contexts/AuthContext";
import { evolutionApi } from "@/lib/api";

export default function DashboardPage() {
  const { user, token, loading, logout } = useAuth();
  const router = useRouter();
  const [chatsCount, setChatsCount] = useState<number | null>(null);
  const [syncing, setSyncing] = useState(false);
  const didRun = useRef(false);

  useEffect(() => {
    if (!loading && !user) {
      router.push("/login");
    }
  }, [user, loading, router]);

  useEffect(() => {
    if (!token || didRun.current) return;
    didRun.current = true;

    (async () => {
      try {
        const status = await evolutionApi.getStatus(token);

        if (status.chats_count != null) {
          setChatsCount(status.chats_count);
          return;
        }

        if (status.status !== "connected") return;

        setSyncing(true);
        const result = await evolutionApi.syncChats(token);
        setChatsCount(result.total);
      } catch {
        /* WA may not be ready */
      } finally {
        setSyncing(false);
      }
    })();
  }, [token]);

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-100 dark:bg-gray-900 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  if (!user) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gray-100 dark:bg-gray-900">
      <nav className="bg-white dark:bg-gray-800 shadow">
        <div className="max-w-6xl mx-auto px-4 py-4 flex justify-between items-center">
          <Link href="/dashboard" className="text-xl font-bold text-indigo-600 dark:text-indigo-400">
            No Lose
          </Link>
          <div className="flex items-center gap-4">
            <Link
              href="/whatsapp"
              className="text-gray-700 dark:text-gray-300 hover:text-indigo-600 dark:hover:text-indigo-400"
            >
              WhatsApp
            </Link>
            <Link
              href="/account"
              className="text-gray-700 dark:text-gray-300 hover:text-indigo-600 dark:hover:text-indigo-400"
            >
              Account
            </Link>
            <button
              onClick={() => {
                logout();
                router.push("/");
              }}
              className="text-gray-700 dark:text-gray-300 hover:text-red-600 dark:hover:text-red-400"
            >
              Logout
            </button>
          </div>
        </div>
      </nav>

      <main className="max-w-6xl mx-auto px-4 py-12">
        <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-lg p-8">
          <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-4">
            Hello, {user.name}!
          </h1>
          <p className="text-gray-600 dark:text-gray-400 text-lg">
            Welcome to your dashboard. This is your personal space.
          </p>
        </div>

        <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-6">
          <Link href="/whatsapp" className="bg-white dark:bg-gray-800 rounded-xl shadow p-6 hover:shadow-lg transition">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
              WhatsApp Connection
            </h3>
            <p className="text-gray-600 dark:text-gray-400">
              Connect your WhatsApp account to sync chat history.
            </p>
          </Link>

          <Link href="/whatsapp/sync" className="bg-white dark:bg-gray-800 rounded-xl shadow p-6 hover:shadow-lg transition">
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                Sync Chats
              </h3>
              {syncing && (
                <div className="animate-spin rounded-full h-5 w-5 border-2 border-indigo-400 border-t-transparent"></div>
              )}
              {!syncing && chatsCount != null && (
                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-sm font-medium bg-indigo-100 text-indigo-800 dark:bg-indigo-900 dark:text-indigo-200">
                  {chatsCount}
                </span>
              )}
            </div>
            <p className="text-gray-600 dark:text-gray-400">
              View and sync your WhatsApp contacts and messages.
            </p>
          </Link>

          <div className="bg-white dark:bg-gray-800 rounded-xl shadow p-6">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
              Quick Stats
            </h3>
            <p className="text-gray-600 dark:text-gray-400">
              Your synced contacts and messages will appear here.
            </p>
          </div>
        </div>
      </main>
    </div>
  );
}
