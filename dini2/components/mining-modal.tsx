"use client"

import { useState, useEffect, useCallback } from "react"
import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { Progress } from "@/components/ui/progress"

interface MiningModalProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  onMiningComplete: () => void
}

export function MiningModal({ open, onOpenChange, onMiningComplete }: MiningModalProps) {
  const [isMining, setIsMining] = useState(false)
  const [progress, setProgress] = useState(0)

  // Reset state when modal closes
  useEffect(() => {
    if (!open) {
      setProgress(0)
      setIsMining(false)
    }
  }, [open])

  const handleMiningComplete = useCallback(() => {
    setIsMining(false)
    setProgress(0)
    onMiningComplete()
    onOpenChange(false) // Close modal after mining completes
  }, [onMiningComplete, onOpenChange])

  useEffect(() => {
    if (isMining) {
      const timer = setInterval(() => {
        setProgress((oldProgress) => {
          if (oldProgress === 100) {
            clearInterval(timer)
            handleMiningComplete()
            return 100
          }
          const diff = Math.random() * 10
          return Math.min(oldProgress + diff, 100)
        })
      }, 500)

      return () => {
        clearInterval(timer)
      }
    }
  }, [isMining, handleMiningComplete])

  const startMining = () => {
    setIsMining(true)
    setProgress(0)
  }

  return (
    <Dialog 
      open={open} 
      onOpenChange={(newOpen) => {
        // Only allow closing if not mining
        if (!isMining) {
          onOpenChange(newOpen)
        }
      }}
    >
      <DialogContent className="sm:max-w-[425px] backdrop-blur-xl bg-white/10 border-white/20">
        <DialogHeader>
          <DialogTitle className="text-white">Mine Dini Blocks</DialogTitle>
          <DialogDescription className="text-white/70">
            Start mining to earn Dini tokens.
          </DialogDescription>
        </DialogHeader>
        <div className="py-4">
          <Progress value={progress} className="w-full" />
          <p className="mt-2 text-center text-white">{progress.toFixed(0)}% Complete</p>
        </div>
        <DialogFooter>
          <Button
            variant="secondary"
            className="backdrop-blur-xl bg-white/10 border-white/20 hover:bg-white/20 text-white"
            onClick={() => onOpenChange(false)}
            disabled={isMining}  // Disable close button while mining
          >
            Close
          </Button>
          <Button
            className="bg-purple-600 hover:bg-purple-700 text-white"
            onClick={startMining}
            disabled={isMining}
          >
            {isMining ? "Mining..." : "Start Mining"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}