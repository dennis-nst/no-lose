import Link from "next/link";

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800 flex flex-col">
      <header className="p-6">
        <nav className="max-w-6xl mx-auto flex justify-between items-center">
          <h1 className="text-2xl font-bold text-indigo-600 dark:text-indigo-400">
            No Lose
          </h1>
          <div className="flex gap-4">
            <Link
              href="/login"
              className="px-4 py-2 text-gray-700 dark:text-gray-300 hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors"
            >
              Login
            </Link>
            <Link
              href="/register"
              className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
            >
              Register
            </Link>
          </div>
        </nav>
      </header>

      <main className="flex-1">
        {/* Hero Section */}
        <section className="max-w-6xl mx-auto px-4 py-20 text-center">
          <h2 className="text-5xl md:text-6xl font-bold text-gray-900 dark:text-white mb-6">
            Your coldest leads are your <br />
            hottest opportunities
          </h2>
          <p className="text-xl text-gray-600 dark:text-gray-400 mb-8 max-w-3xl mx-auto">
            Connect WhatsApp. AI finds who&apos;s ready to buy again. Get the exact message to send.
          </p>
          <Link
            href="/register"
            className="inline-block px-8 py-4 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors text-lg font-medium"
          >
            Connect WhatsApp — Free
          </Link>
        </section>

        {/* How It Works */}
        <section className="max-w-6xl mx-auto px-4 py-20">
          <h3 className="text-4xl font-bold text-center text-gray-900 dark:text-white mb-16">
            How It Works
          </h3>
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            <div className="text-center">
              <div className="w-16 h-16 bg-indigo-600 text-white rounded-full flex items-center justify-center text-2xl font-bold mx-auto mb-4">
                1
              </div>
              <h4 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
                Connect WhatsApp
              </h4>
              <p className="text-gray-600 dark:text-gray-400">
                One click. 60 seconds. Done.
              </p>
            </div>

            <div className="text-center">
              <div className="w-16 h-16 bg-indigo-600 text-white rounded-full flex items-center justify-center text-2xl font-bold mx-auto mb-4">
                2
              </div>
              <h4 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
                AI analyzes your chats
              </h4>
              <p className="text-gray-600 dark:text-gray-400">
                We find clients ready to buy again and deals worth closing.
              </p>
            </div>

            <div className="text-center">
              <div className="w-16 h-16 bg-indigo-600 text-white rounded-full flex items-center justify-center text-2xl font-bold mx-auto mb-4">
                3
              </div>
              <h4 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
                Get personalized messages
              </h4>
              <p className="text-gray-600 dark:text-gray-400">
                AI writes the perfect reactivation message for each lead.
              </p>
            </div>

            <div className="text-center">
              <div className="w-16 h-16 bg-indigo-600 text-white rounded-full flex items-center justify-center text-2xl font-bold mx-auto mb-4">
                4
              </div>
              <h4 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
                Send & close
              </h4>
              <p className="text-gray-600 dark:text-gray-400">
                One click to send. Then just close the deal.
              </p>
            </div>
          </div>

          <div className="text-center mt-12">
            <Link
              href="/register"
              className="inline-block px-8 py-4 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors text-lg font-medium"
            >
              Start Free Trial
            </Link>
            <p className="mt-6 text-2xl font-semibold text-gray-900 dark:text-white">
              Simple. Fast. Revenue.
            </p>
          </div>
        </section>
      </main>

      <footer className="p-6 text-center text-gray-500 dark:text-gray-400">
        <p>&copy; 2025 No Lose. All rights reserved.</p>
      </footer>
    </div>
  );
}
