import "./globals.css"
import { Inter } from 'next/font/google'
import { ToastProvider } from "@/components/ui/toast"

const inter = Inter({ subsets: ["latin"] })

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <ToastProvider>
<div
  className="min-h-screen w-full"
  style={{
    background: "linear-gradient(to bottom right, #3606A9 10%, #57C1F5 40%, #7F12AC 100%)",
  }}
>        
<div className="container mx-auto px-4 py-8">
              {children}
            </div>
          </div>
        </ToastProvider>
      </body>
    </html>
  )
}

