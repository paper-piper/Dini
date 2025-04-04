// BuyModal.tsx
import { useState, useCallback } from "react";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

interface BuyModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onBuy: (amount: number) => Promise<void>;
}

export function BuyModal({ open, onOpenChange, onBuy }: BuyModalProps) {
  const [amount, setAmount] = useState("");
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState("");

  const handleBuy = async () => {
    try {
      setError("");
      setIsProcessing(true);
      await onBuy(Number(amount));
      setAmount("");
      setIsProcessing(false);
      onOpenChange(false);
    } catch (error) {
      setError("Failed to process transaction. Please try again.");
      console.error("Buy transaction failed:", error);
    }
  };

  return (
    <Dialog 
      open={open} 
      onOpenChange={(newOpen) => {
        if (!isProcessing) {
          if (!newOpen) {
            setAmount("");
          }
          onOpenChange(newOpen);
        }
      }}
    >
      <DialogContent className="sm:max-w-[425px] backdrop-blur-xl bg-white/10 border-white/20">
        <DialogHeader>
          <DialogTitle className="text-white">Buy Dini</DialogTitle>
          <DialogDescription className="text-white/70">
            Enter the amount of Dini you want to buy.
          </DialogDescription>
        </DialogHeader>
        <div className="grid gap-4 py-4">
          <div className="grid gap-2">
            <Label htmlFor="amount" className="text-white">
              Amount
            </Label>
            <Input
              id="amount"
              type="number"
              value={amount}
              onChange={(e) => setAmount(e.target.value)}
              placeholder="Enter amount"
              className="backdrop-blur-xl bg-white/10 border-white/20 text-white placeholder:text-white/50"
              disabled={isProcessing}
            />
          </div>
        </div>
        {error && <div className="text-red-500 text-sm mt-2">{error}</div>}
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
            onClick={handleBuy}
            disabled={isProcessing || amount === ""}
          >
            {isProcessing ? "Processing..." : "Buy Now"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
