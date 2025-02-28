"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"

export default function AuthPage() {
  const router = useRouter()
  const [isLoading, setIsLoading] = useState(false)
  const API_URL = "http://localhost:8000"

  const handleLogin = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    setIsLoading(true)
    const formData = new FormData(e.currentTarget)
    const username = formData.get("username")
    const password = formData.get("password")

    try {
      const response = await fetch(`${API_URL}/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password })
      })

      if (!response.ok) throw new Error("Login failed")

      const result = await response.json()
      // Save both username and session_id in localStorage
      localStorage.setItem("user", JSON.stringify({ username, session_id: result.session_id }))
      router.push("/")
    } catch (error) {
      console.error("Login error:", error)
      // Optionally, display an error message to the user here.
    } finally {
      setIsLoading(false)
    }
  }

  const handleSignup = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    setIsLoading(true)
    const formData = new FormData(e.currentTarget)
    const username = formData.get("username")
    const password = formData.get("password")
    const confirmPassword = formData.get("confirmPassword")

    if (password !== confirmPassword) {
      console.error("Passwords do not match")
      setIsLoading(false)
      return
    }

    try {
      const response = await fetch(`${API_URL}/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password })
      })

      if (!response.ok) throw new Error("Registration failed")

      const result = await response.json()
      // Save both username and session_id in localStorage
      localStorage.setItem("user", JSON.stringify({ username, session_id: result.session_id }))
      router.push("/")
    } catch (error) {
      console.error("Signup error:", error)
      // Optionally, display an error message to the user here.
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="flex min-h-[calc(100vh-4rem)] items-center justify-center">
      <Card className="w-full max-w-md backdrop-blur-xl bg-white/10 border-white/20">
        <CardHeader>
          <CardTitle className="text-2xl font-bold text-center text-white">Welcome to Dini</CardTitle>
          <CardDescription className="text-center text-white/70">
            Login or create an account to start trading
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Tabs defaultValue="login" className="w-full">
            <TabsList className="grid w-full grid-cols-2 bg-white/10">
              <TabsTrigger value="login" className="text-white data-[state=active]:bg-white/20">Login</TabsTrigger>
              <TabsTrigger value="signup" className="text-white data-[state=active]:bg-white/20">Sign Up</TabsTrigger>
            </TabsList>
            <TabsContent value="login">
              <form onSubmit={handleLogin} className="space-y-4 mt-4">
                <div className="space-y-2">
                  <Label htmlFor="username" className="text-white">Username</Label>
                  <Input
                    id="username"
                    name="username"
                    required
                    className="backdrop-blur-xl bg-white/10 border-white/20 text-white"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="password" className="text-white">Password</Label>
                  <Input
                    id="password"
                    name="password"
                    type="password"
                    required
                    className="backdrop-blur-xl bg-white/10 border-white/20 text-white"
                  />
                </div>
                <Button
                  type="submit"
                  className="w-full bg-purple-600 hover:bg-purple-700"
                  disabled={isLoading}
                >
                  {isLoading ? "Loading..." : "Login"}
                </Button>
              </form>
            </TabsContent>
            <TabsContent value="signup">
              <form onSubmit={handleSignup} className="space-y-4 mt-4">
                <div className="space-y-2">
                  <Label htmlFor="new-username" className="text-white">Username</Label>
                  <Input
                    id="new-username"
                    name="username"
                    required
                    className="backdrop-blur-xl bg-white/10 border-white/20 text-white"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="new-password" className="text-white">Password</Label>
                  <Input
                    id="new-password"
                    name="password"
                    type="password"
                    required
                    className="backdrop-blur-xl bg-white/10 border-white/20 text-white"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="confirm-password" className="text-white">Confirm Password</Label>
                  <Input
                    id="confirm-password"
                    name="confirmPassword"
                    type="password"
                    required
                    className="backdrop-blur-xl bg-white/10 border-white/20 text-white"
                  />
                </div>
                <Button
                  type="submit"
                  className="w-full bg-purple-600 hover:bg-purple-700"
                  disabled={isLoading}
                >
                  {isLoading ? "Loading..." : "Sign Up"}
                </Button>
              </form>
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>
    </div>
  )
}
