"use client";

import { useState, useEffect } from "react";

const API_BASE = "http://localhost:8000/api";

interface Stats {
  total_messages: number;
  total_contacts: number;
  total_conversations: number;
  inbound_messages: number;
  outbound_messages: number;
}

interface Message {
  id: number;
  wa_message_id: string;
  type: string;
  content: string | null;
  is_outbound: boolean;
  timestamp: string | null;
  contact_id: number;
}

interface Contact {
  id: number;
  wa_id: string;
  name: string | null;
  profile_name: string | null;
  created_at: string;
}

interface ApiStatus {
  status: string;
  data?: Record<string, unknown>;
  error?: string;
}

export default function Home() {
  const [stats, setStats] = useState<Stats | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [contacts, setContacts] = useState<Contact[]>([]);
  const [apiStatus, setApiStatus] = useState<ApiStatus | null>(null);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState<"dashboard" | "messages" | "contacts">("dashboard");

  const checkApiConnection = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/whatsapp/verify`);
      const data = await response.json();
      setApiStatus(data);
    } catch (error) {
      setApiStatus({ status: "error", error: String(error) });
    }
    setLoading(false);
  };

  const fetchStats = async () => {
    try {
      const response = await fetch(`${API_BASE}/stats`);
      const data = await response.json();
      setStats(data);
    } catch (error) {
      console.error("Failed to fetch stats:", error);
    }
  };

  const fetchMessages = async () => {
    try {
      const response = await fetch(`${API_BASE}/messages`);
      const data = await response.json();
      setMessages(data.messages || []);
    } catch (error) {
      console.error("Failed to fetch messages:", error);
    }
  };

  const fetchContacts = async () => {
    try {
      const response = await fetch(`${API_BASE}/contacts`);
      const data = await response.json();
      setContacts(data.contacts || []);
    } catch (error) {
      console.error("Failed to fetch contacts:", error);
    }
  };

  useEffect(() => {
    fetchStats();
  }, []);

  useEffect(() => {
    if (activeTab === "messages") fetchMessages();
    if (activeTab === "contacts") fetchContacts();
  }, [activeTab]);

  return (
    <div className="min-h-screen bg-gray-100 dark:bg-gray-900">
      <header className="bg-green-600 text-white p-4 shadow-lg">
        <div className="max-w-6xl mx-auto">
          <h1 className="text-2xl font-bold">WhatsApp Data Collector</h1>
          <p className="text-green-100">Cloud API Coexistence Integration</p>
        </div>
      </header>

      <nav className="bg-white dark:bg-gray-800 shadow">
        <div className="max-w-6xl mx-auto px-4">
          <div className="flex space-x-4">
            {(["dashboard", "messages", "contacts"] as const).map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`px-4 py-3 font-medium capitalize ${
                  activeTab === tab
                    ? "text-green-600 border-b-2 border-green-600"
                    : "text-gray-600 hover:text-gray-900 dark:text-gray-300"
                }`}
              >
                {tab}
              </button>
            ))}
          </div>
        </div>
      </nav>

      <main className="max-w-6xl mx-auto p-6">
        {activeTab === "dashboard" && (
          <div className="space-y-6">
            {/* API Connection Card */}
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
              <h2 className="text-xl font-semibold mb-4 dark:text-white">WhatsApp API Connection</h2>
              <button
                onClick={checkApiConnection}
                disabled={loading}
                className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700 disabled:opacity-50"
              >
                {loading ? "Checking..." : "Check API Connection"}
              </button>
              {apiStatus && (
                <div
                  className={`mt-4 p-4 rounded ${
                    apiStatus.status === "ok"
                      ? "bg-green-100 text-green-800"
                      : "bg-red-100 text-red-800"
                  }`}
                >
                  <p className="font-medium">
                    Status: {apiStatus.status === "ok" ? "Connected" : "Error"}
                  </p>
                  {apiStatus.error && <p className="text-sm mt-1">{apiStatus.error}</p>}
                  {apiStatus.data && (
                    <pre className="text-sm mt-2 overflow-auto">
                      {JSON.stringify(apiStatus.data, null, 2)}
                    </pre>
                  )}
                </div>
              )}
            </div>

            {/* Stats Cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
                <h3 className="text-gray-500 dark:text-gray-400 text-sm font-medium">
                  Total Messages
                </h3>
                <p className="text-3xl font-bold text-gray-900 dark:text-white">
                  {stats?.total_messages ?? "-"}
                </p>
                <div className="mt-2 text-sm text-gray-600 dark:text-gray-400">
                  <span className="text-green-600">↓ {stats?.inbound_messages ?? 0}</span>
                  {" / "}
                  <span className="text-blue-600">↑ {stats?.outbound_messages ?? 0}</span>
                </div>
              </div>

              <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
                <h3 className="text-gray-500 dark:text-gray-400 text-sm font-medium">
                  Total Contacts
                </h3>
                <p className="text-3xl font-bold text-gray-900 dark:text-white">
                  {stats?.total_contacts ?? "-"}
                </p>
              </div>

              <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
                <h3 className="text-gray-500 dark:text-gray-400 text-sm font-medium">
                  Conversations
                </h3>
                <p className="text-3xl font-bold text-gray-900 dark:text-white">
                  {stats?.total_conversations ?? "-"}
                </p>
              </div>
            </div>

            {/* Quick Actions */}
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
              <h2 className="text-xl font-semibold mb-4 dark:text-white">Quick Actions</h2>
              <div className="flex flex-wrap gap-3">
                <button
                  onClick={fetchStats}
                  className="bg-gray-200 dark:bg-gray-700 px-4 py-2 rounded hover:bg-gray-300 dark:hover:bg-gray-600 dark:text-white"
                >
                  Refresh Stats
                </button>
                <a
                  href="http://localhost:8000/docs"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
                >
                  Open API Docs
                </a>
              </div>
            </div>
          </div>
        )}

        {activeTab === "messages" && (
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow">
            <div className="p-4 border-b dark:border-gray-700 flex justify-between items-center">
              <h2 className="text-xl font-semibold dark:text-white">Messages</h2>
              <button
                onClick={fetchMessages}
                className="bg-green-600 text-white px-3 py-1 rounded text-sm hover:bg-green-700"
              >
                Refresh
              </button>
            </div>
            <div className="divide-y dark:divide-gray-700">
              {messages.length === 0 ? (
                <p className="p-6 text-gray-500 dark:text-gray-400 text-center">
                  No messages yet. Messages will appear here when received via webhook.
                </p>
              ) : (
                messages.map((msg) => (
                  <div key={msg.id} className="p-4">
                    <div className="flex justify-between items-start">
                      <div>
                        <span
                          className={`inline-block px-2 py-1 rounded text-xs ${
                            msg.is_outbound
                              ? "bg-blue-100 text-blue-800"
                              : "bg-green-100 text-green-800"
                          }`}
                        >
                          {msg.is_outbound ? "Sent" : "Received"}
                        </span>
                        <span className="ml-2 text-xs text-gray-500">{msg.type}</span>
                      </div>
                      <span className="text-xs text-gray-400">
                        {msg.timestamp ? new Date(msg.timestamp).toLocaleString() : "-"}
                      </span>
                    </div>
                    <p className="mt-2 text-gray-800 dark:text-gray-200">
                      {msg.content || <span className="italic text-gray-400">[{msg.type}]</span>}
                    </p>
                  </div>
                ))
              )}
            </div>
          </div>
        )}

        {activeTab === "contacts" && (
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow">
            <div className="p-4 border-b dark:border-gray-700 flex justify-between items-center">
              <h2 className="text-xl font-semibold dark:text-white">Contacts</h2>
              <button
                onClick={fetchContacts}
                className="bg-green-600 text-white px-3 py-1 rounded text-sm hover:bg-green-700"
              >
                Refresh
              </button>
            </div>
            <div className="divide-y dark:divide-gray-700">
              {contacts.length === 0 ? (
                <p className="p-6 text-gray-500 dark:text-gray-400 text-center">
                  No contacts yet. Contacts will be added automatically from incoming messages.
                </p>
              ) : (
                contacts.map((contact) => (
                  <div key={contact.id} className="p-4 flex justify-between items-center">
                    <div>
                      <p className="font-medium dark:text-white">
                        {contact.profile_name || contact.name || "Unknown"}
                      </p>
                      <p className="text-sm text-gray-500">{contact.wa_id}</p>
                    </div>
                    <span className="text-xs text-gray-400">
                      {new Date(contact.created_at).toLocaleDateString()}
                    </span>
                  </div>
                ))
              )}
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
