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
}
from "@/components/ui/select"
import { useUser } from "@/contexts/user-context"; // ✅ Import user session from correct path

// Define the shape of a user option
interface UserOption {
  label: string
  value: string
}

interface TransferModalProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  onTransfer: (recipient: string, amount: number) => void // callback from parent
}

const API_IP = process.env.NEXT_PUBLIC_API_IP;
const API_URL = `https://${API_IP}:8000`;

export function TransferModal({ open, onOpenChange, onTransfer }: TransferModalProps) {
    const { user } = useUser()
  const [connectedUsers, setConnectedUsers] = useState<UserOption[]>([])
  const [selectedRecipient, setSelectedRecipient] = useState<string>("")
  const [amount, setAmount] = useState<number>(0)
  const [isProcessing, setIsProcessing] = useState<boolean>(false)

  // Fetch connected users from the backend when the modal opens
  useEffect(() => {
    if (open) {
      // GET the array of connected user names
      fetch(`${API_URL}/connected-users`, {
        method: "GET",
        headers: {
          "Session-Id": user.session_id, // ✅ Include session ID for authentication
          "Content-Type": "application/json",
        },
        credentials: "include", // ✅ Allow session-based authentication
      })
        .then((res) => {
          if (!res.ok) {
            throw new Error(`Error fetching users: ${res.statusText}`)
          }
          return res.json()
        })
        .then((data: string[]) => {
          // Transform the data into the format expected
          const options = data.map((userName) => ({
            label: userName,
            value: userName, // You can use user IDs here if available
          }))
          setConnectedUsers(options)
        })
        .catch((error) => {
          console.error("Failed to fetch connected users:", error)
          setConnectedUsers([]) // fallback to empty array
        })
    }
  }, [open])

  const handleTransfer = useCallback(() => {
    if (!selectedRecipient || amount <= 0 || isProcessing || !user?.session_id) return;
    setIsProcessing(true);

    fetch(`${API_URL}/transactions`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Session-Id": user.session_id, // ✅ Include session ID
      },
      credentials: "include",
      body: JSON.stringify({
        type: "transfer",
        amount,
        details: selectedRecipient,
        status: "pending",
      }),
    })
      .then((res) => {
        if (!res.ok) throw new Error("Failed to create transfer transaction");
        return res.json();
      })
      .then((data) => {
        console.log("Transfer transaction created:", data);
        onTransfer(selectedRecipient, amount);
      })
      .catch((error) => {
        console.error("Transfer failed:", error);
      })
      .finally(() => {
        setIsProcessing(false);
        onOpenChange(false);
        setSelectedRecipient("");
        setAmount(0);
      });
  }, [selectedRecipient, amount, isProcessing, user, onOpenChange, onTransfer]);

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
            >
              <SelectTrigger
                id="recipient"
                className="backdrop-blur-xl bg-white/10 border-white/20 text-white"
              >
                <SelectValue placeholder="Select recipient" />
              </SelectTrigger>
              <SelectContent className="backdrop-blur-xl bg-white/10 border-white/20">
                {connectedUsers.map((user) => (
                  <SelectItem
                    key={user.value}
                    value={user.value}
                    className="text-white hover:bg-white/20"
                  >
                    {user.label}
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
