import { headers } from "next/headers"
import { redirect } from "next/navigation"
import { auth } from "@/lib/auth"
import { AppSidebar } from "@/components/app-sidebar"
import { AppHeader } from "@/components/app-header"
import { HeaderProvider } from "@/components/header-context"
import {
  SidebarInset,
  SidebarProvider,
} from "@/components/ui/sidebar"

export default async function AppLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const session = await auth.api.getSession({
    headers: await headers(),
  })

  if (!session) {
    redirect("/sign-in")
  }

  return (
    <SidebarProvider className="!h-dvh">
      <AppSidebar />
      <SidebarInset className="overflow-hidden">
        <HeaderProvider>
          <AppHeader />
          <div className="flex flex-1 flex-col overflow-hidden">{children}</div>
        </HeaderProvider>
      </SidebarInset>
    </SidebarProvider>
  )
}
