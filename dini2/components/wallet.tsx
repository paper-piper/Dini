import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

interface WalletProps {
  balance: number
}

export function Wallet({ balance }: WalletProps) {
  return (
    <Card className="w-full backdrop-blur-xl bg-white/10 border-white/20">
      <CardHeader>
        <CardTitle className="text-xl font-bold text-white">Your Wallet</CardTitle>
      </CardHeader>
      <CardContent>
        <p className="text-3xl font-bold text-white">{balance.toFixed(2)} DINI</p>
      </CardContent>
    </Card>
  )
}

