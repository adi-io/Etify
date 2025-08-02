"use client";

import { useAccount, useConnect, useDisconnect } from 'wagmi'
import { Button } from '@/components/ui/button'
import { useState } from 'react'

export function ConnectWallet() {
  const { address, isConnected } = useAccount()
  const { connect, connectors, isPending } = useConnect()
  const { disconnect } = useDisconnect()
  const [showConnectors, setShowConnectors] = useState(false)

  if (isConnected) {
    return (
      <Button
        variant="ghost"
        className="text-green-400 border border-green-400"
        onClick={() => disconnect()}
      >
        {address?.slice(0, 6)}...{address?.slice(-4)}
      </Button>
    )
  }

  return (
    <div className="relative">
      <Button
        variant="ghost"
        className="text-green-400 border border-green-400"
        onClick={() => setShowConnectors(!showConnectors)}
        disabled={isPending}
      >
        {isPending ? 'Connecting...' : 'Connect Wallet'}
      </Button>
      
      {showConnectors && (
        <div className="absolute top-full right-0 mt-2 bg-[#181f2a] border border-gray-600 rounded-lg p-2 min-w-[200px] z-50">
          {connectors.map((connector) => (
            <Button
              key={connector.uid}
              variant="ghost"
              className="w-full text-left justify-start text-white hover:bg-[#232b3b]"
              onClick={() => {
                connect({ connector })
                setShowConnectors(false)
              }}
              disabled={isPending}
            >
              {connector.name}
            </Button>
          ))}
        </div>
      )}
    </div>
  )
}
