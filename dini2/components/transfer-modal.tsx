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

interface TransferModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onTransfer: (recipient: string, amount: number) => void; // Callback for transfer
}

export function TransferModal({ open, onOpenChange, onTransfer }: TransferModalProps) {
  const [recipient, setRecipient] = useState('');
  const [amount, setAmount] = useState(0);
  const [isProcessing, setIsProcessing] = useState(false);

  const handleTransfer = useCallback(() => {
    if (!recipient || amount <= 0 || isProcessing) {
      return;
    }
    setIsProcessing(true);
    onTransfer(recipient, amount);
    setRecipient('');
    setAmount(0);
    setIsProcessing(false);
    onOpenChange(false);
  }, [recipient, amount, isProcessing, onTransfer, onOpenChange]);

  return (
    <Dialog 
      open={open} 
      onOpenChange={(newOpen) => {
        if (!isProcessing) {
          if (!newOpen) {
            setRecipient('');
            setAmount(0);
          }
          onOpenChange(newOpen);
        }
      }}
    >
      <DialogContent className="sm:max-w-[425px] backdrop-blur-xl bg-white/10 border-white/20">
        <DialogHeader>
          <DialogTitle className="text-white">Transfer Dini</DialogTitle>
          <DialogDescription className="text-white/70">
            Enter the recipient&apos;s address and the amount to transfer.
          </DialogDescription>
        </DialogHeader>
        <div className="grid gap-4 py-4">
          <div className="grid gap-2">
            <Label htmlFor="recipient" className="text-white">
              Recipient Address
            </Label>
            <Input
              id="recipient"
              type="text"
              value={recipient}
              onChange={(e) => setRecipient(e.target.value)}
              placeholder="Enter recipient's address"
              className="backdrop-blur-xl bg-white/10 border-white/20 text-white placeholder:text-white/50"
              disabled={isProcessing}
            />
          </div>
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
            disabled={isProcessing || !recipient || amount <= 0}
          >
            {isProcessing ? "Processing..." : "Transfer Now"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}