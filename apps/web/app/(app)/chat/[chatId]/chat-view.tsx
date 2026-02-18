"use client"

import { trpc } from "@/lib/trpc/client"
import { ChatInterface } from "@/components/chat/chat-interface"
import { Skeleton } from "@/components/ui/skeleton"

export function ChatView({ chatId }: { chatId: string }) {
  const { data, isPending } = trpc.chat.getMessages.useQuery({ chatId })

  if (isPending) {
    return (
      <div className="flex flex-1 overflow-y-auto">
        <div className="mx-auto flex min-h-full max-w-3xl flex-col justify-end gap-4 px-4 py-4">
          <div className="flex justify-end">
            <Skeleton className="h-10 w-48 rounded-2xl" />
          </div>
          <div className="flex justify-start">
            <Skeleton className="h-24 w-72 rounded-2xl" />
          </div>
          <div className="flex justify-end">
            <Skeleton className="h-10 w-56 rounded-2xl" />
          </div>
          <div className="flex justify-start">
            <Skeleton className="h-16 w-64 rounded-2xl" />
          </div>
        </div>
      </div>
    )
  }

  if (!data || !data.organizationId) {
    return (
      <div className="flex flex-1 items-center justify-center">
        <p className="text-muted-foreground">Chat not found</p>
      </div>
    )
  }

  return (
    <ChatInterface
      organizationId={data.organizationId}
      chatId={chatId}
      initialMessages={data.messages}
      initialCitations={data.citations.map((c) => ({
        ...c,
        documentUrl: "",
      }))}
    />
  )
}
