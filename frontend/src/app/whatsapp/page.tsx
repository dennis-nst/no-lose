"use client";

import { useEffect, useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useAuth } from "@/contexts/AuthContext";
import { evolutionApi, InstanceStatus } from "@/lib/api";

export default function WhatsAppPage() {
  const { user, loading, token, logout } = useAuth();
  const router = useRouter();

  const [status, setStatus] = useState<InstanceStatus | null>(null);
  const [statusLoading, setStatusLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchStatus = useCallback(async () => {
    if (!token) return;

    try {
      const data = await evolutionApi.getStatus(token);
      setStatus(data);
      setError(null);
    } catch (err) {
      console.error("Failed to fetch status:", err);
    } finally {
      setStatusLoading(false);
    }
  }, [token]);

  useEffect(() => {
    if (!loading && !user) {
      router.push("/login");
    }
  }, [user, loading, router]);

  useEffect(() => {
    if (token) {
      fetchStatus();
    }
  }, [token, fetchStatus]);

  // Auto-refresh status when QR code is shown or connecting
  useEffect(() => {
    if (status?.status === "qr" || status?.status === "connecting") {
      const interval = setInterval(fetchStatus, 5000);
      return () => clearInterval(interval);
    }
  }, [status?.status, fetchStatus]);

  const handleConnect = async () => {
    if (!token) return;

    setActionLoading(true);
    setError(null);

    try {
      const data = await evolutionApi.createInstance(token);
      setStatus(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to connect");
    } finally {
      setActionLoading(false);
    }
  };

  const handleRefreshQR = async () => {
    if (!token) return;

    setActionLoading(true);
    setError(null);

    try {
      const data = await evolutionApi.getQRCode(token);
      setStatus((prev) => (prev ? { ...prev, qr_code: data.qr_code, status: "qr" } : null));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to refresh QR code");
    } finally {
      setActionLoading(false);
    }
  };

  const handleDisconnect = async () => {
    if (!token) return;

    setActionLoading(true);
    setError(null);

    try {
      await evolutionApi.disconnect(token);
      setStatus((prev) => (prev ? { ...prev, status: "disconnected", qr_code: undefined } : null));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to disconnect");
    } finally {
      setActionLoading(false);
    }
  };

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

  const getStatusColor = () => {
    switch (status?.status) {
      case "connected":
        return "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200";
      case "connecting":
        return "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200";
      case "qr":
        return "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200";
      default:
        return "bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200";
    }
  };

  const getStatusText = () => {
    switch (status?.status) {
      case "connected":
        return "Connected";
      case "connecting":
        return "Connecting...";
      case "qr":
        return "Scan QR Code";
      default:
        return "Disconnected";
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 dark:bg-gray-900">
      <nav className="bg-white dark:bg-gray-800 shadow">
        <div className="max-w-6xl mx-auto px-4 py-4 flex justify-between items-center">
          <Link href="/dashboard" className="text-xl font-bold text-indigo-600 dark:text-indigo-400">
            No Lose
          </Link>
          <div className="flex items-center gap-4">
            <Link
              href="/dashboard"
              className="text-gray-700 dark:text-gray-300 hover:text-indigo-600 dark:hover:text-indigo-400"
            >
              Dashboard
            </Link>
            <Link
              href="/whatsapp/sync"
              className="text-gray-700 dark:text-gray-300 hover:text-indigo-600 dark:hover:text-indigo-400"
            >
              Sync Chats
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

      <main className="max-w-4xl mx-auto px-4 py-12">
        <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-lg p-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
            WhatsApp Connection
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mb-8">
            Connect your WhatsApp account to sync your chat history.
          </p>

          {error && (
            <div className="mb-6 p-4 bg-red-100 dark:bg-red-900 text-red-800 dark:text-red-200 rounded-lg">
              {error}
            </div>
          )}

          {/* Status Card */}
          <div className="mb-8 p-6 border dark:border-gray-700 rounded-xl">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
                Connection Status
              </h2>
              <span className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor()}`}>
                {statusLoading ? "Loading..." : getStatusText()}
              </span>
            </div>

            {status?.status === "connected" && (
              <div className="space-y-2 text-gray-600 dark:text-gray-400">
                {status.phone_number && (
                  <p>
                    <span className="font-medium">Phone:</span> +{status.phone_number}
                  </p>
                )}
                {status.profile_name && (
                  <p>
                    <span className="font-medium">Profile:</span> {status.profile_name}
                  </p>
                )}
                {status.last_connected_at && (
                  <p>
                    <span className="font-medium">Connected since:</span>{" "}
                    {new Date(status.last_connected_at).toLocaleString()}
                  </p>
                )}
              </div>
            )}
          </div>

          {/* QR Code Display */}
          {status?.status === "qr" && status.qr_code && (
            <div className="mb-8 text-center">
              <div className="inline-block p-4 bg-white rounded-xl shadow-lg">
                <img
                  src={status.qr_code}
                  alt="WhatsApp QR Code"
                  className="w-64 h-64"
                />
              </div>
              <p className="mt-4 text-gray-600 dark:text-gray-400">
                Open WhatsApp on your phone, go to{" "}
                <span className="font-medium">Settings &gt; Linked Devices</span>, and scan this QR
                code.
              </p>
              <p className="mt-2 text-sm text-gray-500 dark:text-gray-500">
                QR code refreshes automatically. Click &quot;Refresh QR&quot; if it expires.
              </p>
            </div>
          )}

          {/* Connecting state */}
          {status?.status === "connecting" && (
            <div className="mb-8 text-center">
              <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-indigo-600 mx-auto"></div>
              <p className="mt-4 text-gray-600 dark:text-gray-400">Connecting to WhatsApp...</p>
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex flex-wrap gap-4">
            {(!status || status.status === "disconnected") && (
              <button
                onClick={handleConnect}
                disabled={actionLoading}
                className="px-6 py-3 bg-green-600 text-white rounded-lg font-medium hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition"
              >
                {actionLoading ? "Connecting..." : "Connect WhatsApp"}
              </button>
            )}

            {status?.status === "qr" && (
              <button
                onClick={handleRefreshQR}
                disabled={actionLoading}
                className="px-6 py-3 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition"
              >
                {actionLoading ? "Refreshing..." : "Refresh QR Code"}
              </button>
            )}

            {status?.status === "connected" && (
              <>
                <Link
                  href="/whatsapp/sync"
                  className="px-6 py-3 bg-indigo-600 text-white rounded-lg font-medium hover:bg-indigo-700 transition"
                >
                  Sync Chats
                </Link>
                <button
                  onClick={handleDisconnect}
                  disabled={actionLoading}
                  className="px-6 py-3 bg-red-600 text-white rounded-lg font-medium hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed transition"
                >
                  {actionLoading ? "Disconnecting..." : "Disconnect"}
                </button>
              </>
            )}

            <button
              onClick={fetchStatus}
              disabled={statusLoading}
              className="px-6 py-3 bg-gray-200 dark:bg-gray-700 text-gray-800 dark:text-gray-200 rounded-lg font-medium hover:bg-gray-300 dark:hover:bg-gray-600 disabled:opacity-50 transition"
            >
              Refresh Status
            </button>
          </div>
        </div>
      </main>
    </div>
  );
}
