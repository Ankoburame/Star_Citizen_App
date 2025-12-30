import "./globals.css"
import { AppShell } from "@/components/layout/AppShell"

export const metadata = {
  title: "Star Citizen – Economy Tool",
  description: "Analyse économique et marchés",
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="fr">
      <body>
        <AppShell>{children}</AppShell>
      </body>
    </html>
  )
}
