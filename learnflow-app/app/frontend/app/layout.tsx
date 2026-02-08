import type { Metadata } from "next"
import "./globals.css"
import Navbar from "@/components/Navbar"
import Footer from "@/components/Footer"
import ChatWidget from "@/components/ChatWidget"

export const metadata: Metadata = {
  title: "Fatima Zehra Boutique - Elegant Fashion",
  description: "Discover elegant fashion for every occasion at Fatima Zehra Boutique",
  keywords: "fashion, boutique, dresses, elegant, luxury",
  icons: {
    icon: "/favicon.svg",
    apple: "/favicon.svg",
  },
  themeColor: "#1e40af",
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <head></head>
      <body className="bg-white dark:bg-slate-950">
        <Navbar />
        <main className="min-h-screen">
          {children}
        </main>
        <Footer />
        <ChatWidget />
      </body>
    </html>
  )
}
