"use client"

import { authClient } from "@/lib/auth-client"
import { trpc } from "@/lib/trpc/client"
import { ChatInterface } from "@/components/chat/chat-interface"
import { generateId } from "@/lib/id"

export function NewChatPage() {
  const { data: activeOrg, isPending } = authClient.useActiveOrganization()
  const createChat = trpc.chat.create.useMutation()
  const utils = trpc.useUtils()

  if (isPending) {
    return <div className="flex flex-1" />
  }

  if (!activeOrg) {
    return (
      <div className="flex flex-1 items-center justify-center p-8 text-center">
        <div className="space-y-2">
          <p className="text-lg font-medium">No workspace selected</p>
          <p className="text-sm text-muted-foreground">
            Select or create a workspace from the sidebar.
          </p>
        </div>
      </div>
    )
  }

  async function handleFirstMessage(message: string): Promise<string> {
    const chatId = generateId()
    await createChat.mutateAsync({ id: chatId, title: message.slice(0, 80) })
    utils.chat.list.invalidate()
    window.history.replaceState(null, "", `/chat/${chatId}`)
    return chatId
  }

  return (
    <ChatInterface
      organizationId={activeOrg.id}
      onFirstMessage={handleFirstMessage}
    />
  )
}
