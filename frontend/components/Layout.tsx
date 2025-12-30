import "../globals.css"
import { Sidebar } from "@/components/layout/Sidebar"

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="fr">
      <body className="flex h-screen bg-zinc-950 text-zinc-100">
        <Sidebar />
        <main className="flex-1 p-6 overflow-auto">
          {children}
        </main>
      </body>
    </html>
  )
}
