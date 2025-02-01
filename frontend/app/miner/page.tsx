"use client";

import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { BuyModal } from "@/components/buy-modal";
import { SellModal } from "@/components/sell-modal";
import { TransferModal } from "@/components/transfer-modal";
import { MiningModal } from "@/components/mining-modal";
import { Wallet } from "@/components/wallet";
import { History } from "@/components/history";
import { useToast } from "@/components/use-toast";
import { Transaction } from "@/components/history";
import { Coins, ArrowLeftRight, WalletIcon, PickaxeIcon as Pick } from "lucide-react";

const API_URL = "http://localhost:8000";

export default function MinerPage() {
  const [buyOpen, setBuyOpen] = useState(false);
  const [sellOpen, setSellOpen] = useState(false);
  const [transferOpen, setTransferOpen] = useState(false);
  const [miningOpen, setMiningOpen] = useState(false);
  const [isMining, setIsMining] = useState(false);  // Prevent double mining
  const [balance, setBalance] = useState(2000);
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const { toast } = useToast();

  const fetchAllTransactions = async () => {
    try {
      const response = await fetch(`${API_URL}/transactions`);
      const data: Transaction[] = await response.json();
      console.log("Fetched transactions from backend:", data);

      setTransactions((prevTransactions) => {
        const updatedTransactions = data.map((newTx: Transaction) => {
          const oldTx = prevTransactions.find((tx) => tx.id === newTx.id);

          if (!oldTx || oldTx.status !== newTx.status) {
            if (newTx.status === "approved" && newTx.status !== oldTx?.status) {
              if (newTx.type === "buy" || newTx.type === "mine") setBalance((prev) => prev + (newTx.amount / 2));
              if (newTx.type === "sell" || newTx.type === "transfer")
                setBalance((prev) => prev - (newTx.amount - 2));
            }
            return newTx;
          }
          return oldTx;
        });

        return updatedTransactions;
      });
    } catch (error) {
      console.error("Failed to fetch all transactions:", error);
    }
  };

  useEffect(() => {
    const hasPendingTransactions = transactions.some((tx) => tx.status === "pending");

    if (!hasPendingTransactions) {
      return;
    }

    const interval = setInterval(fetchAllTransactions, 5000);
    return () => clearInterval(interval);
  }, [transactions]);

  const createTransaction = async (type: string, amount: number, details?: string) => {
    try {
      const response = await fetch(`${API_URL}/transactions`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          type,
          amount,
          details,
          status: "pending",
        }),
      });
      if (!response.ok) {
        throw new Error("Failed to create transaction");
      }
      const newTransaction = await response.json();
      console.log("Created transaction response:", newTransaction);
      setTransactions((prev) => [newTransaction, ...prev]);
    } catch (error) {
      console.error("Failed to create transaction:", error);
    }
  };

  // Function to start mining
  const startMining = () => {
    if (isMining) return;  // Prevent double mining

    setIsMining(true);
    setMiningOpen(true);  // Open the MiningModal

    toast({
      title: "Mining Started",
      description: "Your block is being mined. Please wait...",
    });
  };

  // Function to handle mining completion
  const handleMiningComplete = () => {
    const miningAmount = 20;
    createTransaction("mine", miningAmount);
    toast({
      title: "Block Mined Successfully!",
      description: `You've earned ${miningAmount} Dini tokens.`,
      duration: 5000,
    });
    setIsMining(false);  // Reset mining state
    // Note: Do NOT close the modal here. Let the user close it manually.
  };

  return (
    <div className="flex flex-col gap-8">
      <Card className="w-full backdrop-blur-xl bg-white/10 border-white/20 shadow-xl">
        <CardHeader>
          <CardTitle className="text-3xl font-bold text-center text-white">
            Dini - Miner Dashboard
          </CardTitle>
        </CardHeader>
        <CardContent className="grid gap-6">
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            <Button
              variant="secondary"
              className="h-32 backdrop-blur-xl bg-white/10 border-white/20 hover:bg-white/20"
              onClick={() => setBuyOpen(true)}
            >
              <div className="flex flex-col items-center gap-2">
                <Coins className="h-8 w-8" />
                <span className="text-lg">Buy Dini</span>
              </div>
            </Button>
            <Button
              variant="secondary"
              className="h-32 backdrop-blur-xl bg-white/10 border-white/20 hover:bg-white/20"
              onClick={() => setSellOpen(true)}
            >
              <div className="flex flex-col items-center gap-2">
                <WalletIcon className="h-8 w-8" />
                <span className="text-lg">Sell Dini</span>
              </div>
            </Button>
            <Button
              variant="secondary"
              className="h-32 backdrop-blur-xl bg-white/10 border-white/20 hover:bg-white/20"
              onClick={() => setTransferOpen(true)}
            >
              <div className="flex flex-col items-center gap-2">
                <ArrowLeftRight className="h-8 w-8" />
                <span className="text-lg">Transfer</span>
              </div>
            </Button>
            <Button
              variant="secondary"
              className="h-32 backdrop-blur-xl bg-white/10 border-white/20 hover:bg-white/20"
              onClick={startMining}
              disabled={isMining}
            >
              <div className="flex flex-col items-center gap-2">
                <Pick className="h-8 w-8" />
                <span className="text-lg">Mine Blocks</span>
              </div>
            </Button>
          </div>
        </CardContent>
      </Card>

      <div className="grid gap-8 md:grid-cols-2">
        <Wallet balance={balance} />
        <History transactions={transactions} />
      </div>

      <BuyModal
        open={buyOpen}
        onOpenChange={setBuyOpen}
        onBuy={(amount: number) => {
          setBuyOpen(false);
          createTransaction("buy", amount);
        }}
      />
      <SellModal
        open={sellOpen}
        onOpenChange={setSellOpen}
        onSell={(amount: number) => {
          setSellOpen(false);
          createTransaction("sell", amount);
        }}
      />
      <TransferModal
        open={transferOpen}
        onOpenChange={setTransferOpen}
        onTransfer={(recipient, amount) => {
          setTransferOpen(false);
          createTransaction("transfer", amount, `To: ${recipient}`);
        }}
      />
      <MiningModal
        open={miningOpen}
        onOpenChange={setMiningOpen}
        onMiningComplete={handleMiningComplete}
      />
    </div>
  );
}
