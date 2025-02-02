"use client"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog"

interface MiningModalProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  onMiningComplete: () => void
}

const symbols = ["💎", "🔔", "❤️", "7️⃣", "🍋", "🍒"]

export function MiningModal({ open, onOpenChange, onMiningComplete }: MiningModalProps) {
  const [isMining, setIsMining] = useState(false)
  const [slots, setSlots] = useState(["?", "?", "?"])
  const [jackpot, setJackpot] = useState(false)

  useEffect(() => {
    let interval: NodeJS.Timeout
    if (isMining) {
      interval = setInterval(() => {
        setSlots(slots.map(() => symbols[Math.floor(Math.random() * symbols.length)]))
      }, 100)

      // Random mining duration between 3 and 7 seconds
      const miningDuration = Math.floor(Math.random() * 4000) + 3000

      setTimeout(() => {
        clearInterval(interval)
        setIsMining(false)
        setJackpot(true)
        setSlots(["🎉", "🎉", "🎉"])
        onMiningComplete()
      }, miningDuration)
    }
    return () => clearInterval(interval)
  }, [isMining, onMiningComplete, slots]) // Added slots to dependencies

  const startMining = () => {
    setIsMining(true)
    setJackpot(false)
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[425px] backdrop-blur-xl bg-white/10 border-white/20">
        <DialogHeader>
          <DialogTitle className="text-white">Mine Dini Blocks</DialogTitle>
          <DialogDescription className="text-white/70">Start mining to earn Dini tokens.</DialogDescription>
        </DialogHeader>
        <div className="py-4">
          <div className="flex justify-center items-center space-x-4 text-6xl mb-4">
            {slots.map((symbol, index) => (
              <div
                key={index}
                className="w-20 h-20 flex items-center justify-center bg-purple-800 rounded-lg shadow-inner"
              >
                {symbol}
              </div>
            ))}
          </div>
          {jackpot && <p className="text-center text-2xl font-bold text-yellow-400 animate-pulse">🎊 JACKPOT! 🎊</p>}
        </div>
        <DialogFooter>
          <Button
            variant="secondary"
            className="backdrop-blur-xl bg-white/10 border-white/20 hover:bg-white/20 text-white"
            onClick={() => onOpenChange(false)}
          >
            Close
          </Button>
          <Button className="bg-purple-600 hover:bg-purple-700 text-white" onClick={startMining} disabled={isMining}>
            {isMining ? "Mining..." : "Start Mining"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}

