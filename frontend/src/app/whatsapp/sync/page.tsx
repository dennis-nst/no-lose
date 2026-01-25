"use client";

import { useEffect, useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useAuth } from "@/contexts/AuthContext";
import { evolutionApi, Contact, ChatInfo, Message, InstanceStatus } from "@/lib/api";

export default function SyncPage() {
  const { user, loading, token, logout } = useAuth();
  const router = useRouter();

  const [status, setStatus] = useState<InstanceStatus | null>(null);
  const [contacts, setContacts] = useState<Contact[]>([]);
  const [chats, setChats] = useState<ChatInfo[]>([]);
  const [selectedContact, setSelectedContact] = useState<Contact | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);

  const [syncingContacts, setSyncingContacts] = useState(false);
  const [syncingChats, setSyncingChats] = useState(false);
  const [syncingMessages, setSyncingMessages] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  const fetchStatus = useCallback(async () => {
    if (!token) return;

    try {
      const data = await evolutionApi.getStatus(token);
      setStatus(data);
    } catch (err) {
      console.error("Failed to fetch status:", err);
    }
  }, [token]);

  const fetchContacts = useCallback(async () => {
    if (!token) return;

    try {
      const data = await evolutionApi.getContacts(token);
      setContacts(data.contacts);
    } catch (err) {
      console.error("Failed to fetch contacts:", err);
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
      fetchContacts();
    }
  }, [token, fetchStatus, fetchContacts]);

  const handleSyncContacts = async () => {
    if (!token) return;

    setSyncingContacts(true);
    setError(null);
    setSuccessMessage(null);

    try {
      const result = await evolutionApi.syncContacts(token);
      setSuccessMessage(result.message);
      await fetchContacts();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to sync contacts");
    } finally {
      setSyncingContacts(false);
    }
  };

  const handleSyncChats = async () => {
    if (!token) return;

    setSyncingChats(true);
    setError(null);
    setSuccessMessage(null);

    try {
      const result = await evolutionApi.syncChats(token);
      setChats(result.chats);
      setSuccessMessage(`Found ${result.total} chats`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to sync chats");
    } finally {
      setSyncingChats(false);
    }
  };

  const handleSyncMessages = async (contact: Contact) => {
    if (!token) return;

    setSyncingMessages(contact.id);
    setError(null);
    setSuccessMessage(null);

    try {
      const result = await evolutionApi.syncMessages(token, contact.id, 30);
      setSuccessMessage(result.message);

      // Load messages for this contact
      const messagesData = await evolutionApi.getMessages(token, contact.id);
      setMessages(messagesData.messages);
      setSelectedContact(contact);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to sync messages");
    } finally {
      setSyncingMessages(null);
    }
  };

  const handleViewMessages = async (contact: Contact) => {
    if (!token) return;

    try {
      const data = await evolutionApi.getMessages(token, contact.id);
      setMessages(data.messages);
      setSelectedContact(contact);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load messages");
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

  const isConnected = status?.status === "connected";

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
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">Sync Chats</h1>
          <p className="text-gray-600 dark:text-gray-400">
            Synchronize your WhatsApp contacts and chat history.
          </p>
        </div>

        {!isConnected && (
          <div className="bg-yellow-100 dark:bg-yellow-900 text-yellow-800 dark:text-yellow-200 p-4 rounded-lg mb-6">
            WhatsApp is not connected.{" "}
            <Link href="/whatsapp" className="underline font-medium">
              Connect first
            </Link>
            .
          </div>
        )}

        {error && (
          <div className="bg-red-100 dark:bg-red-900 text-red-800 dark:text-red-200 p-4 rounded-lg mb-6">
            {error}
          </div>
        )}

        {successMessage && (
          <div className="bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200 p-4 rounded-lg mb-6">
            {successMessage}
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Contacts Panel */}
          <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-lg p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold text-gray-900 dark:text-white">Contacts</h2>
              <div className="flex gap-2">
                <button
                  onClick={handleSyncContacts}
                  disabled={!isConnected || syncingContacts}
                  className="px-4 py-2 bg-indigo-600 text-white rounded-lg text-sm font-medium hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition"
                >
                  {syncingContacts ? "Syncing..." : "Sync Contacts"}
                </button>
                <button
                  onClick={handleSyncChats}
                  disabled={!isConnected || syncingChats}
                  className="px-4 py-2 bg-green-600 text-white rounded-lg text-sm font-medium hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition"
                >
                  {syncingChats ? "Loading..." : "Load Chats"}
                </button>
              </div>
            </div>

            {chats.length > 0 && (
              <div className="mb-4 p-3 bg-blue-50 dark:bg-blue-900/30 rounded-lg">
                <p className="text-sm text-blue-800 dark:text-blue-200">
                  {chats.length} active chats found. Click on a contact to sync messages.
                </p>
              </div>
            )}

            <div className="space-y-2 max-h-96 overflow-y-auto">
              {contacts.length === 0 ? (
                <p className="text-gray-500 dark:text-gray-400 text-center py-8">
                  No contacts synced yet. Click &quot;Sync Contacts&quot; to start.
                </p>
              ) : (
                contacts.map((contact) => (
                  <div
                    key={contact.id}
                    className={`p-3 rounded-lg border dark:border-gray-700 cursor-pointer transition ${
                      selectedContact?.id === contact.id
                        ? "bg-indigo-50 dark:bg-indigo-900/30 border-indigo-300 dark:border-indigo-700"
                        : "hover:bg-gray-50 dark:hover:bg-gray-700/50"
                    }`}
                    onClick={() => handleViewMessages(contact)}
                  >
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="font-medium text-gray-900 dark:text-white">
                          {contact.name || contact.profile_name || contact.wa_id}
                        </p>
                        <p className="text-sm text-gray-500 dark:text-gray-400">+{contact.wa_id}</p>
                      </div>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          handleSyncMessages(contact);
                        }}
                        disabled={!isConnected || syncingMessages === contact.id}
                        className="px-3 py-1 bg-gray-200 dark:bg-gray-700 text-gray-800 dark:text-gray-200 rounded text-sm hover:bg-gray-300 dark:hover:bg-gray-600 disabled:opacity-50 transition"
                      >
                        {syncingMessages === contact.id ? "..." : "Sync"}
                      </button>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>

          {/* Messages Panel */}
          <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-lg p-6">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
              {selectedContact
                ? `Messages with ${selectedContact.name || selectedContact.profile_name || selectedContact.wa_id}`
                : "Messages"}
            </h2>

            <div className="space-y-3 max-h-96 overflow-y-auto">
              {!selectedContact ? (
                <p className="text-gray-500 dark:text-gray-400 text-center py-8">
                  Select a contact to view messages.
                </p>
              ) : messages.length === 0 ? (
                <p className="text-gray-500 dark:text-gray-400 text-center py-8">
                  No messages synced yet. Click &quot;Sync&quot; on the contact to download history.
                </p>
              ) : (
                messages.map((message) => (
                  <div
                    key={message.id}
                    className={`p-3 rounded-lg max-w-[80%] ${
                      message.is_outbound
                        ? "ml-auto bg-indigo-100 dark:bg-indigo-900/50"
                        : "bg-gray-100 dark:bg-gray-700"
                    }`}
                  >
                    <p className="text-gray-900 dark:text-white">
                      {message.content || `[${message.type}]`}
                    </p>
                    <div className="flex items-center gap-2 mt-1">
                      <span className="text-xs text-gray-500 dark:text-gray-400">
                        {message.timestamp
                          ? new Date(message.timestamp).toLocaleString()
                          : "Unknown time"}
                      </span>
                      <span className="text-xs text-gray-400 dark:text-gray-500">
                        {message.source === "evolution_api" ? "Evolution" : "Cloud"}
                      </span>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
