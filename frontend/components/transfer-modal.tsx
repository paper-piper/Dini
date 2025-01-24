"use client"

import { useState, useCallback, useEffect } from "react"
import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"

interface TransferModalProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  onTransfer: (recipient: string, amount: number) => void // callback from parent
}

// Adjust this to match your backend URL if it's different
const API_URL = "http://localhost:8000"

export function TransferModal({ open, onOpenChange, onTransfer }: TransferModalProps) {
  const [connectedUsers, setConnectedUsers] = useState<string[]>([])
  const [selectedRecipient, setSelectedRecipient] = useState("")
  const [amount, setAmount] = useState(0)
  const [isProcessing, setIsProcessing] = useState(false)

  // Fetch connected users from the backend when the modal opens
  useEffect(() => {
    if (open) {
      // GET the array of connected user names
      fetch(`${API_URL}/connected-users`)
        .then((res) => res.json())
        .then((data: string[]) => {
          setConnectedUsers(data || [])
        })
        .catch((error) => {
          console.error("Failed to fetch connected users:", error)
          setConnectedUsers([]) // fallback to empty array
        })
    }
  }, [open])

  const handleTransfer = useCallback(() => {
    if (!selectedRecipient || amount <= 0 || isProcessing) return
    setIsProcessing(true)

    // Call parent's onTransfer (which triggers the creation of a transaction)
    onTransfer(selectedRecipient, amount)

    // Reset fields
    setSelectedRecipient("")
    setAmount(0)
    setIsProcessing(false)
    onOpenChange(false)
  }, [selectedRecipient, amount, isProcessing, onOpenChange, onTransfer])

  return (
    <Dialog
      open={open}
      onOpenChange={(newOpen) => {
        // Prevent closing while processing
        if (!isProcessing) {
          if (!newOpen) {
            // Reset when user manually closes or modal unmounts
            setSelectedRecipient("")
            setAmount(0)
          }
          onOpenChange(newOpen)
        }
      }}
    >
      <DialogContent className="sm:max-w-[425px] backdrop-blur-xl bg-white/10 border-white/20">
        <DialogHeader>
          <DialogTitle className="text-white">Transfer Dini</DialogTitle>
          <DialogDescription className="text-white/70">
            Select a recipient and enter the amount to transfer.
          </DialogDescription>
        </DialogHeader>
        <div className="grid gap-4 py-4">
          {/* Recipient Dropdown */}
          <div className="grid gap-2">
            <Label htmlFor="recipient" className="text-white">
              Recipient
            </Label>
            <Select
              onValueChange={setSelectedRecipient}
              value={selectedRecipient}
              disabled={isProcessing}
            >
              <SelectTrigger
                id="recipient"
                className="backdrop-blur-xl bg-white/10 border-white/20 text-white"
              >
                <SelectValue placeholder="Select recipient" />
              </SelectTrigger>
              <SelectContent className="backdrop-blur-xl bg-white/10 border-white/20">
                {connectedUsers.map((userName, index) => (
                  <SelectItem
                    key={index}
                    value={userName}
                    className="text-white hover:bg-white/20"
                  >
                    {userName}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Amount Input */}
          <div className="grid gap-2">
            <Label htmlFor="amount" className="text-white">
              Amount
            </Label>
            <Input
              id="amount"
              type="number"
              value={amount}
              onChange={(e) => setAmount(Number(e.target.value))}
              placeholder="Enter amount"
              className="backdrop-blur-xl bg-white/10 border-white/20 text-white placeholder:text-white/50"
              disabled={isProcessing}
            />
          </div>
        </div>
        <DialogFooter>
          <Button
            variant="secondary"
            className="backdrop-blur-xl bg-white/10 border-white/20 hover:bg-white/20 text-white"
            onClick={() => onOpenChange(false)}
            disabled={isProcessing}
          >
            Cancel
          </Button>
          <Button
            className="bg-purple-600 hover:bg-purple-700 text-white"
            onClick={handleTransfer}
            disabled={!selectedRecipient || amount <= 0 || isProcessing}
          >
            {isProcessing ? "Processing..." : "Transfer Now"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
