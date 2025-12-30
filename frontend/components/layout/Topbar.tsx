"use client"

import { Menu } from "lucide-react"

type TopbarProps = {
  sidebarOpen: boolean
  toggleSidebar: () => void
}

export function Topbar({ toggleSidebar }: TopbarProps) {
  return (
    <header className="h-14 flex items-center gap-4 px-4 bg-[#0f1320] border-b border-[#1b2030]">
      <button
        onClick={toggleSidebar}
        className="p-2 rounded hover:bg-[#1b2030] transition"
      >
        <Menu size={18} />
      </button>

      <h1 className="text-sm font-medium text-zinc-300">
        Star Citizen – Economy Tool
      </h1>
    </header>
  )
}
