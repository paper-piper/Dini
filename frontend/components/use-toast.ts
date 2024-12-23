import { useState, useEffect, useCallback } from "react"

export interface ToastProps {
  title: string
  description?: string
  duration?: number
}

export function useToast() {
  const [toasts, setToasts] = useState<ToastProps[]>([])

  const toast = useCallback(({ title, description, duration = 5000 }: ToastProps) => {
    const id = Date.now()
    setToasts((prevToasts) => [...prevToasts, { id, title, description, duration }])

    if (duration > 0) {
      setTimeout(() => {
        setToasts((prevToasts) => prevToasts.filter((toast) => toast.id !== id))
      }, duration)
    }
  }, [])

  return { toast }
}

