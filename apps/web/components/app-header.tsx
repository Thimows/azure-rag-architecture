"use client"

import { SidebarTrigger } from "@/components/ui/sidebar"
import { useHeader } from "@/components/header-context"

export function AppHeader() {
  const { title, actions } = useHeader()

  return (
    <header className="flex h-14 shrink-0 items-center gap-2 border-b px-4">
      <SidebarTrigger className="-ml-1.5" />
      <span className="text-sm font-medium">{title}</span>
      {actions && <div className="ml-auto flex items-center gap-2">{actions}</div>}
    </header>
  )
}
