"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import {
  LayoutDashboard,
  Factory,
  ShoppingCart,
  TrendingUp,
} from "lucide-react"

type SidebarProps = {
  open: boolean
}

const navItems = [
  { href: "/", label: "Dashboard", icon: LayoutDashboard },
  { href: "/production", label: "Production", icon: Factory },
  { href: "/commerce", label: "Commerce", icon: ShoppingCart },
  { href: "/market", label: "Market", icon: TrendingUp },
]

export function Sidebar({ open }: SidebarProps) {
  const pathname = usePathname()

  return (
    <aside
      className={`
        ${open ? "w-64" : "w-16"}
        transition-all duration-200
        bg-[#0e1220]
        border-r border-[#20263a]
        flex flex-col
      `}
    >
      {/* Header */}
      <div className="h-14 flex items-center px-4 border-b border-[#20263a]">
        {open && (
          <span className="text-sm font-semibold tracking-wide text-[#e5e7eb]">
            STAR CITIZEN
          </span>
        )}
      </div>

      {/* Navigation */}
      <nav className="flex-1 py-3 space-y-1">
        {navItems.map(({ href, label, icon: Icon }) => {
          const active = pathname === href

          return (
            <Link
              key={href}
              href={href}
              className={`
                flex items-center gap-3 px-4 py-2 text-sm
                ${
                  active
                    ? "bg-[#1f2a44] text-white"
                    : "text-[#b0b6c3] hover:bg-[#161b2e] hover:text-white"
                }
              `}
            >
              <Icon size={18} />
              {open && <span>{label}</span>}
            </Link>
          )
        })}
      </nav>

      {/* Footer */}
      <div className="border-t border-[#20263a] p-3 text-xs text-[#8b92a3]">
        {open ? (
          <>
            <div>API: online</div>
            <div>v0.1.0</div>
          </>
        ) : (
          <div className="text-center">●</div>
        )}
      </div>
    </aside>
  )
}
