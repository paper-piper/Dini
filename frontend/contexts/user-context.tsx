"use client"

import { createContext, useContext, useEffect, useState, type ReactNode } from "react"
import { useRouter, usePathname } from "next/navigation"

interface User {
  username: string
  session_id: string
}

export const UserContext = createContext<{
  user: User | null
  login: (username: string, password: string) => Promise<void>
  logout: () => void
}>({
  user: null,
  login: async () => {},
  logout: () => {},
})

export function UserProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const router = useRouter()
  const pathname = usePathname()

  useEffect(() => {
    // Check for user in localStorage on mount
    const storedUser = localStorage.getItem("user")
    if (storedUser) {
      setUser(JSON.parse(storedUser))
    } else if (pathname !== "/auth") {
      router.push("/auth")
    }
  }, [router, pathname])

  // Add session heartbeat
  useEffect(() => {
    if (!user?.session_id) return

    const heartbeat = async () => {
      try {
        const response = await fetch('https://localhost:8000/heartbeat', {
          method: 'POST',
          headers: {
            'Session-Id': user.session_id,
          },
        })
        
        if (!response.ok) {
          // Session expired or invalid
          setUser(null)
        }
      } catch (error) {
        console.error('Heartbeat failed:', error)
      }
    }

    const interval = setInterval(heartbeat, 60000) // Every minute
    return () => clearInterval(interval)
  }, [user])

  const login = async (username: string, password: string) => {
    // Implement login logic here
    // For now, we'll just create a new user
    const newUser: User = {
      username,
      session_id: "new_session_id", // Replace with actual session ID
    }
    setUser(newUser)
    localStorage.setItem("user", JSON.stringify(newUser))
  }

  const logout = () => {
    setUser(null)
    localStorage.removeItem("user")
    router.push("/auth")
  }

  return <UserContext.Provider value={{ user, login, logout }}>{children}</UserContext.Provider>
}

export function useUser() {
  const context = useContext(UserContext)
  if (context === undefined) {
    throw new Error("useUser must be used within a UserProvider")
  }
  return context
}

