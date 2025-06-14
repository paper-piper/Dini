import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { format } from "date-fns";

export interface Transaction {
  id: string;
  type: "buy" | "sell" | "transfer" | "mine" | "receive";
  amount: number;
  timestamp: string;
  status: "pending" | "failed" | "approved";
  details?: string;
}

interface HistoryProps {
  transactions: Transaction[];
}

export function History({ transactions }: HistoryProps) {
  const [showAll, setShowAll] = useState(false);

  const getStatusEmoji = (status: string) => {
    switch (status) {
      case "pending":
        return "⏳ Pending"; // Pending
      case "failed":
        return "❌ Failed"; // Failed
      case "approved":
        return "✅ Approved"; // Approved
      default:
        return "";
    }
  };

  // Sort transactions by timestamp (most recent first)
  const sortedTransactions = [...transactions].sort(
    (a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
  );

  // Show only 5 most recent transactions unless expanded
  const displayedTransactions = showAll
    ? sortedTransactions
    : sortedTransactions.slice(0, 5);

  return (
    <Card className="w-full backdrop-blur-xl bg-white/10 border-white/20">
      <CardHeader>
        <CardTitle className="text-xl font-bold text-white">
          Transaction History
        </CardTitle>
      </CardHeader>
      <CardContent>
        <ul className="space-y-2">
          <li className="grid grid-cols-4 gap-4 text-white/70 font-bold">
            <span>Type</span>
            <span>Amount</span>
            <span>Date</span>
            <span>Status</span> {/* New Status Column */}
          </li>
          {displayedTransactions.map((transaction) => (
            <li
              key={transaction.id}
              className="grid grid-cols-4 gap-4 items-center text-white"
            >
              <span className="capitalize">
              {(["transfer", "receive"].includes(transaction.type) && transaction.details)
                ? `${transaction.type} (${transaction.details})`
                : transaction.type}
              </span>
              <span>{transaction.amount.toFixed(2)} DINI</span>
              <span className="text-sm text-white/70">
                {transaction.timestamp
                  ? format(new Date(transaction.timestamp), "dd/MM/yyyy, HH:mm:ss")
                  : "Invalid Date"}
              </span>
              <span>{getStatusEmoji(transaction.status)}</span> {/* Status Emoji */}
            </li>
          ))}
        </ul>
        {transactions.length > 5 && (
          <button
            onClick={() => setShowAll((prev) => !prev)}
            className="mt-4 border border-white text-white font-bold rounded-full px-4 py-2"
          >
            {showAll ? "Show Less" : "Show All"}
          </button>
        )}
      </CardContent>
    </Card>
  );
}
