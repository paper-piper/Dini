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

interface SellModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSell: (amount: number) => void;
}


// SellModal.tsx
export function SellModal({ open, onOpenChange, onSell }: SellModalProps) {
  const [amount, setAmount] = useState(0);
  const [isProcessing, setIsProcessing] = useState(false);

  const handleSell = useCallback(() => {
    if (amount <= 0 || isProcessing) {
      return;
    }
    setIsProcessing(true);
    onSell(amount);
    setAmount(0);
    setIsProcessing(false);
    onOpenChange(false);
  }, [amount, isProcessing, onSell, onOpenChange]);

  return (
    <Dialog 
      open={open} 
      onOpenChange={(newOpen) => {
        if (!isProcessing) {
          if (!newOpen) {
            setAmount(0);
          }
          onOpenChange(newOpen);
        }
      }}
    >
      <DialogContent className="sm:max-w-[425px] backdrop-blur-xl bg-white/10 border-white/20">
        <DialogHeader>
          <DialogTitle className="text-white">Sell Dini</DialogTitle>
          <DialogDescription className="text-white/70">
            Enter the amount of Dini you want to sell.
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
            onClick={handleSell}
            disabled={isProcessing || amount <= 0}
          >
            {isProcessing ? "Processing..." : "Sell Now"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}