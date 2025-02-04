// Frontend Code (React)
"use client";

import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { BuyModal } from "@/components/buy-modal";
import { SellModal } from "@/components/sell-modal";
import { TransferModal } from "@/components/transfer-modal";
import { Wallet } from "@/components/wallet";
import { History } from "@/components/history";
import { Coins, ArrowLeftRight, WalletIcon } from "lucide-react";
import { Transaction } from "@/components/history";

const API_URL = "http://localhost:8000"; // Backend URL

export default function Home() {
  const [buyOpen, setBuyOpen] = useState(false);
  const [sellOpen, setSellOpen] = useState(false);
  const [transferOpen, setTransferOpen] = useState(false);

  // Wallet balance state
  const [balance, setBalance] = useState(1000);

  // Transactions state
  const [transactions, setTransactions] = useState<Transaction[]>([]);

  const INITIAL_BALANCE = 1000;

    const fetchAllTransactions = async () => {
      try {
        const response = await fetch(`${API_URL}/transactions`);
        const data: Transaction[] = await response.json();
        console.log("Fetched all transactions from backend:", data);

        // Update local transactions state
        setTransactions(data);

        // Recalculate balance from scratch
        const approvedTransactions = data.filter(tx => tx.status === "approved");
        const newBalance = approvedTransactions.reduce((balance, tx) => {
          if (tx.type === "buy") {
            return balance + tx.amount;
          } else if (tx.type === "sell" || tx.type === "transfer") {
            return balance - tx.amount;
          }
          return balance;
        }, INITIAL_BALANCE);

        setBalance(newBalance);
      } catch (error) {
        console.error("Failed to fetch all transactions:", error);
      }
    };

  

  useEffect(() => {
    // Check if there are pending transactions
    const hasPendingTransactions = transactions.some((tx) => tx.status === "pending");
    if (!hasPendingTransactions) {
      return; // Skip polling if no pending transactions
    }
    // console.log("Cheking for updates...")
    const interval = setInterval(fetchAllTransactions, 5000); // Poll every 5 seconds

    return () => clearInterval(interval); // Cleanup interval on unmount
  }, [transactions]);

  const createTransaction = async (type: string, amount: number, details?: string) => {
    try {
      const response = await fetch(`${API_URL}/transactions`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          type,          // Transaction type (buy, sell, transfer)
          amount,        // Transaction amount
          details,       // Optional details
          status: "pending", // Default status
        }),
      });
      if (!response.ok) {
        throw new Error("Failed to create transaction");
      }
      const newTransaction = await response.json();
      console.log("Created transaction response:", newTransaction); // Debug log

      // Update state with formatted display details
    setTransactions((prev) => [
      {
        ...newTransaction,
        details:
          newTransaction.type === "transfer" ? `To: ${newTransaction.details}` : newTransaction.details,
      },
      ...prev,
    ]);
  } catch (error) {
    console.error("Failed to create transaction:", error);
    }
  };
  

  return (
    <div className="flex flex-col gap-8">
      <Card className="w-full backdrop-blur-xl bg-white/10 border-white/20 shadow-xl">
        <CardHeader>
          <CardTitle className="text-3xl font-bold text-center text-white">
             Dini - User Dashboard
          </CardTitle>
        </CardHeader>
        <CardContent className="grid gap-6">
          <div className="grid gap-4 md:grid-cols-3">
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
          createTransaction("transfer", amount, recipient);
        }}
      />
    </div>
  );
}
