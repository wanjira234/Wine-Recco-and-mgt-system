import type { Metadata } from "next"
import { Inter } from "next/font/google"
import "./globals.css"
import Layout from "@/components/layout/Layout"

const inter = Inter({ subsets: ["latin"] })

export const metadata: Metadata = {
  title: "WineRecco - Your Personal Wine Recommendation System",
  description: "Discover and track your wine preferences with personalized recommendations.",
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <Layout>{children}</Layout>
      </body>
    </html>
  )
}
