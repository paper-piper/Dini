"use client"

import { useState, useCallback } from "react"
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

// In a real application, you would fetch or receive this list from your backend:
const users = [
  { id: "1", name: "Alice" },
  { id: "2", name: "Bob" },
  { id: "3", name: "Charlie" },
  { id: "4", name: "Diana" },
]

interface TransferModalProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  onTransfer: (recipient: string, amount: number) => void // callback from parent
}

export function TransferModal({ open, onOpenChange, onTransfer }: TransferModalProps) {
  const [selectedRecipient, setSelectedRecipient] = useState("")
  const [amount, setAmount] = useState(0)
  const [isProcessing, setIsProcessing] = useState(false)

  const handleTransfer = useCallback(() => {
    // Basic validation
    if (!selectedRecipient || amount <= 0 || isProcessing) return

    setIsProcessing(true)
    // Call the parent's onTransfer, passing the selected user name and amount
    onTransfer(selectedRecipient, amount)
    // Reset fields
    setSelectedRecipient("")
    setAmount(0)
    setIsProcessing(false)
    onOpenChange(false)
  }, [selectedRecipient, amount, isProcessing, onTransfer, onOpenChange])

  return (
    <Dialog
      open={open}
      onOpenChange={(newOpen) => {
        // Prevent closing while processing
        if (!isProcessing) {
          if (!newOpen) {
            // Reset fields on close
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
                {users.map((user) => (
                  <SelectItem
                    key={user.id}
                    value={user.name} // store the user name (or use user.id if you prefer)
                    className="text-white hover:bg-white/20"
                  >
                    {user.name}
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
            disabled={
              isProcessing ||
              !selectedRecipient ||
              amount <= 0
            }
          >
            {isProcessing ? "Processing..." : "Transfer Now"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
