"use client";

import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { BuyModal } from "@/components/buy-modal";
import { SellModal } from "@/components/sell-modal";
import { TransferModal } from "@/components/transfer-modal";
import { Wallet } from "@/components/wallet";
import { History } from "@/components/history";
import { Coins, ArrowLeftRight, WalletIcon, LogOut } from "lucide-react";
import { useUser } from "@/contexts/user-context";

const API_URL = "https://localhost:8000";

export default function Home() {
  const { user, logout } = useUser();
  const [buyOpen, setBuyOpen] = useState(false);
  const [sellOpen, setSellOpen] = useState(false);
  const [transferOpen, setTransferOpen] = useState(false);
  const [balance, setBalance] = useState(1000);
  const [transactions, setTransactions] = useState([]);

  const INITIAL_BALANCE = 0;

  const fetchAllTransactions = async () => {
    if (!user?.session_id) return;
    try {
      const response = await fetch(`${API_URL}/transactions`, {
        headers: {
          "Session-Id": user.session_id,
        },
      });
      if (!response.ok) throw new Error("Failed to fetch transactions");
      const data = await response.json();
      console.log("Fetched transactions:", data);

      setTransactions(data);

      const approvedTransactions = data.filter(tx => tx.status === "approved");
      const newBalance = approvedTransactions.reduce((balance, tx) => {
        if (tx.type === "buy") return balance + tx.amount;
        else if (tx.type === "sell" || tx.type === "transfer") return balance - tx.amount;
        return balance;
      }, INITIAL_BALANCE);
      setBalance(newBalance);
    } catch (error) {
      console.error("Error fetching transactions:", error);
    }
  };

    useEffect(() => {
      if (!user?.session_id) return;

      const interval = setInterval(() => {
        fetchAllTransactions();
      }, 5000); // Poll every 5 seconds

      // Clean up on unmount or when user changes
      return () => clearInterval(interval);
    }, [user?.session_id]);


  const createTransaction = async (type: string, amount: number, details?: string) => {
    if (!user?.session_id) {
      console.error("No active session");
      // You might want to redirect to login here
      return;
    }

    try {
      const response = await fetch(`${API_URL}/transactions`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Session-Id": user.session_id,
        },
        body: JSON.stringify({
          type,
          amount,
          details,
          status: "pending",
        }),
      });

      if (response.status === 401) {
        // Session expired
        console.error("Session expired");
        logout(); // Call your logout function to clear the invalid session
        return;
      }

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const newTransaction = await response.json();
      console.log("Created transaction:", newTransaction);

      // Refresh transactions to get updated balance
      fetchAllTransactions();
    } catch (error) {
      console.error("Transaction creation error:", error);
      // You might want to show an error message to the user here
    }
  };

  return (
    <div className="flex flex-col gap-8">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-white">Welcome, {user?.username}!</h1>
        <Button variant="ghost" className="text-white hover:bg-white/10" onClick={logout}>
          <LogOut className="h-5 w-5 mr-2" />
          Logout
        </Button>
      </div>
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
            setBuyOpen(false)
            createTransaction("buy", amount)
          }}
        />
        <SellModal
          open={sellOpen}
          onOpenChange={setSellOpen}
          onSell={(amount: number) => {
            setSellOpen(false)
            createTransaction("sell", amount)
          }}
        />
        <TransferModal
          open={transferOpen}
          onOpenChange={setTransferOpen}
          onTransfer={(recipient, amount) => {
            setTransferOpen(false)
            createTransaction("transfer", amount, recipient)
          }}
        />
      </div>
    </div>
  );
}
