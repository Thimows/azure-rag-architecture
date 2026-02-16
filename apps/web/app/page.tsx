export default function Home() {
  return (
    <div className="flex min-h-screen flex-col bg-gray-50 text-gray-900 dark:bg-gray-950 dark:text-gray-100">
      <header className="border-b border-gray-200 bg-white px-6 py-4 dark:border-gray-800 dark:bg-gray-900">
        <div className="mx-auto flex max-w-4xl items-center justify-between">
          <h1 className="text-xl font-semibold">Enterprise RAG</h1>
          <span className="text-sm text-gray-500 dark:text-gray-400">
            v0.1.0
          </span>
        </div>
      </header>

      <main className="mx-auto flex w-full max-w-4xl flex-1 flex-col p-6">
        <div className="flex flex-1 flex-col items-center justify-center space-y-4 text-center">
          <div className="rounded-full bg-gray-200 p-4 dark:bg-gray-800">
            <svg
              className="h-8 w-8 text-gray-500 dark:text-gray-400"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={1.5}
                d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"
              />
            </svg>
          </div>
          <h2 className="text-lg font-medium text-gray-700 dark:text-gray-300">
            Ask a question about your documents
          </h2>
          <p className="max-w-md text-sm text-gray-500 dark:text-gray-400">
            Upload documents and ask questions. Answers are grounded in your
            data with inline citations.
          </p>
        </div>
      </main>

      <footer className="border-t border-gray-200 bg-white p-4 dark:border-gray-800 dark:bg-gray-900">
        <div className="mx-auto flex max-w-4xl gap-3">
          <input
            type="text"
            placeholder="Ask a question..."
            className="flex-1 rounded-lg border border-gray-300 bg-white px-4 py-3 text-sm outline-none transition-colors placeholder:text-gray-400 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 dark:border-gray-700 dark:bg-gray-800 dark:placeholder:text-gray-500 dark:focus:border-blue-400"
          />
          <button className="rounded-lg bg-blue-600 px-6 py-3 text-sm font-medium text-white transition-colors hover:bg-blue-700 disabled:opacity-50">
            Send
          </button>
        </div>
      </footer>
    </div>
  );
}
