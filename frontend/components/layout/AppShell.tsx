"use client"

import { useState } from "react"
import { Sidebar } from "./Sidebar"
import { Topbar } from "./Topbar"

export function AppShell({ children }: { children: React.ReactNode }) {
  const [sidebarOpen, setSidebarOpen] = useState(true)

  return (
    <div className="flex h-screen bg-[#0b0e14] text-zinc-200">
      <Sidebar open={sidebarOpen} />

      <div className="flex flex-col flex-1">
        <Topbar
          sidebarOpen={sidebarOpen}
          toggleSidebar={() => setSidebarOpen((v) => !v)}
        />

        <main className="flex-1 overflow-auto p-6">
          {children}
        </main>
      </div>
    </div>
  )
}
