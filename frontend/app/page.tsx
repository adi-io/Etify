"use client";

import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
    Select,
    SelectTrigger,
    SelectContent,
    SelectItem,
} from "@/components/ui/select";
import Navbar from "@/components/ui/navbar";
import WalletAddressManager from "@/components/manage-wallet";
import OrderSummaryManager from "@/components/order_overview_popup";
import { ConnectWallet } from "@/components/connect-wallet";
import { createClient } from "@/lib/supabase/client";
import { useRouter } from "next/navigation";
import { useState, useEffect } from "react";
import { useAccount } from "wagmi";
import {
    useTokenApproval,
    useDeposits,
    useTokenAllowance,
} from "@/hooks/useTransactions";
import { CONTRACTS } from "@/lib/contracts";
import { parseUnits, formatUnits } from "viem";
import { toast } from "sonner";

export default function SwapUI() {
    const [usdcAmount, setUsdcAmount] = useState("");
    const [estimatedSpyAmount, setEstimatedSpyAmount] = useState("");
    const [estimatedUsdcAmount, setEstimatedUsdcAmount] = useState("");
    const [spyAmount, setSpyAmount] = useState("");
    const [isLoading, setIsLoading] = useState(false);
    const [status, setStatus] = useState({ message: "", isOpen: null });
    const [isAuthenticated, setIsAuthenticated] = useState(false);
    const [isCheckingAuth, setIsCheckingAuth] = useState(true);
    const [transactionStatus, setTransactionStatus] = useState<
        "idle" | "approving" | "depositing" | "success" | "error"
    >("idle");
    const [tradeType, setTradeType] = useState("buy");
    const router = useRouter();
    const { address, isConnected } = useAccount();
    const { approveToken, waitForApproval } = useTokenApproval();
    const { depositUSDC, depositDSPY, waitForDeposit } = useDeposits();
    const { allowance } = useTokenAllowance(CONTRACTS.USDC_ADDRESS, address);
    const { allowance: dspyAllowance } = useTokenAllowance(
        CONTRACTS.DSPY_ADDRESS,
        address,
    );

    // Add DSPY token to wallet function
    const handleAddDSP = async () => {
        if (!isConnected) {
            toast.error("Please connect your wallet first");
            return;
        }

        try {
            // Add DSPY token to wallet
            await window.ethereum?.request({
                method: "wallet_watchAsset",
                params: {
                    type: "ERC20",
                    options: {
                        address: CONTRACTS.DSPY_ADDRESS,
                        symbol: "DSPY",
                        decimals: 9,
                        image: "", // Add your token logo URL if you have one
                    },
                },
            });
            toast.success("DSPY token added to wallet!");
        } catch (error) {
            console.error("Error adding token:", error);
            toast.error("Failed to add token to wallet");
        }
    };

    // Generate frontend hash
    const generateFrontendHash = () => {
        return crypto.randomUUID().replace(/-/g, "");
    };

    // Backend API calls
    const callBackendBuySpy = async (amount: string, frontendHash: string) => {
        try {
            const supabase = createClient();
            const {
                data: { session },
            } = await supabase.auth.getSession();

            if (!session?.access_token) {
                throw new Error("No auth token found");
            }

            const response = await fetch("/api/buy_spy", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    Authorization: `Bearer ${session.access_token}`,
                },
                body: JSON.stringify({
                    amount_of_usdc_sent: parseFloat(amount),
                    frontend_hash: frontendHash,
                }),
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || "Backend call failed");
            }

            return await response.json();
        } catch (error) {
            console.error("Backend API call failed:", error);
            throw error;
        }
    };

    const callBackendSellSpy = async (amount: string, frontendHash: string) => {
        try {
            const supabase = createClient();
            const {
                data: { session },
            } = await supabase.auth.getSession();

            if (!session?.access_token) {
                throw new Error("No auth token found");
            }

            const response = await fetch("/api/sell_spy", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    Authorization: `Bearer ${session.access_token}`,
                },
                body: JSON.stringify({
                    amount_of_dspy_sent: parseFloat(amount),
                    frontend_hash: frontendHash,
                }),
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || "Backend call failed");
            }

            return await response.json();
        } catch (error) {
            console.error("Backend API call failed:", error);
            throw error;
        }
    };

    const handleBuy = async () => {
        if (!isConnected || !address || !usdcAmount) {
            toast.error("Please connect wallet and enter amount");
            return;
        }

        let approvalTxHash: `0x${string}` | null = null;
        let depositTxHash: `0x${string}` | null = null;

        try {
            setTransactionStatus("approving");

            // Step 1: Generate frontend hash
            const frontendHash = generateFrontendHash();
            console.log("Generated frontend hash:", frontendHash);

            // Step 2: Call backend first to create order
            console.log("Calling backend /buy_spy...");
            toast.loading("Creating order...", { id: "transaction" });

            await callBackendBuySpy(usdcAmount, frontendHash);
            console.log("Backend order created successfully");

            // Step 3: Check if approval is needed
            const amountToSpend = parseUnits(usdcAmount, 6);
            const currentAllowance = (allowance as bigint) || BigInt(0);

            if (currentAllowance < amountToSpend) {
                console.log("Approval needed, requesting approval...");
                toast.loading(
                    "Please approve USDC spending in your wallet...",
                    { id: "transaction" },
                );

                // Submit approval transaction
                approvalTxHash = await approveToken(
                    CONTRACTS.USDC_ADDRESS,
                    usdcAmount,
                    6,
                );
                console.log("Approval transaction submitted:", approvalTxHash);

                toast.loading("Waiting for approval confirmation...", {
                    id: "transaction",
                    description: (
                        <a
                            href={`https://sepolia.basescan.org/tx/${approvalTxHash}`}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-blue-400 hover:text-blue-300 underline"
                        >
                            View on BaseScan ↗
                        </a>
                    ),
                });

                // Wait for approval confirmation
                const approvalReceipt = await waitForApproval(approvalTxHash);

                if (approvalReceipt.status !== "success") {
                    throw new Error("Approval transaction failed");
                }

                console.log("Approval confirmed on-chain");
            } else {
                console.log("Sufficient allowance already exists");
            }

            // Step 4: Execute deposit transaction
            setTransactionStatus("depositing");
            console.log("Executing deposit transaction...");
            toast.loading(
                "Please confirm deposit transaction in your wallet...",
                { id: "transaction" },
            );

            // Submit deposit transaction
            depositTxHash = await depositUSDC(usdcAmount, frontendHash);
            console.log("Deposit transaction submitted:", depositTxHash);

            toast.loading("Waiting for deposit confirmation...", {
                id: "transaction",
                description: (
                    <a
                        href={`https://sepolia.basescan.org/tx/${depositTxHash}`}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-blue-400 hover:text-blue-300 underline"
                    >
                        View on BaseScan ↗
                    </a>
                ),
            });

            // Wait for deposit confirmation
            const depositReceipt = await waitForDeposit(depositTxHash);

            if (depositReceipt.status !== "success") {
                throw new Error("Deposit transaction failed");
            }

            setTransactionStatus("success");
            console.log("All transactions confirmed on-chain!");

            // Show success toast with transaction links
            toast.success(
                "🎉 Transaction completed successfully! Your order is being processed.",
                {
                    id: "transaction",
                    duration: 10000,
                    description: (
                        <div className="space-y-2">
                            <p>
                                Buying {estimatedSpyAmount || "~"} DSPY with{" "}
                                {usdcAmount} USDC
                            </p>
                            <div className="flex flex-col gap-1 text-xs">
                                {approvalTxHash && (
                                    <a
                                        href={`https://sepolia.basescan.org/tx/${approvalTxHash}`}
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        className="text-blue-400 hover:text-blue-300 underline"
                                    >
                                        Approval: {approvalTxHash.slice(0, 10)}
                                        ...{approvalTxHash.slice(-8)} ↗
                                    </a>
                                )}
                                <a
                                    href={`https://sepolia.basescan.org/tx/${depositTxHash}`}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="text-blue-400 hover:text-blue-300 underline"
                                >
                                    Deposit: {depositTxHash.slice(0, 10)}...
                                    {depositTxHash.slice(-8)} ↗
                                </a>
                            </div>
                            <p className="text-gray-400">
                                Your DSPY tokens will arrive shortly.
                            </p>
                        </div>
                    ),
                },
            );

            // Clear the input after successful transaction
            setUsdcAmount("");
            setSpyAmount("");
        } catch (error) {
            console.error("Transaction failed:", error);
            setTransactionStatus("error");

            // Show error toast with transaction links if available
            const errorDescription = (
                <div className="space-y-2">
                    <p>
                        {error instanceof Error
                            ? error.message
                            : "Unknown error occurred"}
                    </p>
                    {(approvalTxHash || depositTxHash) && (
                        <div className="flex flex-col gap-1 text-xs">
                            {approvalTxHash && (
                                <a
                                    href={`https://sepolia.basescan.org/tx/${approvalTxHash}`}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="text-blue-400 hover:text-blue-300 underline"
                                >
                                    Approval: {approvalTxHash.slice(0, 10)}...
                                    {approvalTxHash.slice(-8)} ↗
                                </a>
                            )}
                            {depositTxHash && (
                                <a
                                    href={`https://sepolia.basescan.org/tx/${depositTxHash}`}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="text-blue-400 hover:text-blue-300 underline"
                                >
                                    Deposit: {depositTxHash.slice(0, 10)}...
                                    {depositTxHash.slice(-8)} ↗
                                </a>
                            )}
                        </div>
                    )}
                </div>
            );

            toast.error("Transaction failed", {
                id: "transaction",
                description: errorDescription,
                duration: 10000,
            });
        }
    };

    const handleSell = async () => {
        if (!isConnected || !address || !spyAmount) {
            toast.error("Please connect wallet and enter amount");
            return;
        }

        let approvalTxHash: `0x${string}` | null = null;
        let depositTxHash: `0x${string}` | null = null;

        try {
            setTransactionStatus("approving");

            // Step 1: Generate frontend hash
            const frontendHash = generateFrontendHash();
            console.log("Generated frontend hash:", frontendHash);

            // Step 2: Call backend first to create order
            console.log("Calling backend /sell_spy...");
            toast.loading("Creating sell order...", { id: "transaction" });

            await callBackendSellSpy(spyAmount, frontendHash);
            console.log("Backend order created successfully");

            // Step 3: Check if approval is needed for DSPY token
            const amountToSell = parseUnits(spyAmount, 9);
            const currentDspyAllowance = (dspyAllowance as bigint) || BigInt(0);

            if (currentDspyAllowance < amountToSell) {
                console.log("Approval needed, requesting approval...");
                toast.loading(
                    "Please approve DSPY spending in your wallet...",
                    { id: "transaction" },
                );

                approvalTxHash = await approveToken(
                    CONTRACTS.DSPY_ADDRESS,
                    spyAmount,
                    9,
                );
                console.log("Approval transaction submitted:", approvalTxHash);

                toast.loading("Waiting for approval confirmation...", {
                    id: "transaction",
                    description: (
                        <a
                            href={`https://sepolia.basescan.org/tx/${approvalTxHash}`}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-blue-400 hover:text-blue-300 underline"
                        >
                            View on BaseScan ↗
                        </a>
                    ),
                });

                const approvalReceipt = await waitForApproval(approvalTxHash);

                if (approvalReceipt.status !== "success") {
                    throw new Error("Approval transaction failed");
                }

                console.log("Approval confirmed on-chain");
            } else {
                console.log("Sufficient allowance already exists");
            }

            // Step 4: Execute deposit transaction
            setTransactionStatus("depositing");
            console.log("Executing deposit transaction...");
            toast.loading(
                "Please confirm deposit transaction in your wallet...",
                { id: "transaction" },
            );

            depositTxHash = await depositDSPY(spyAmount, frontendHash);
            console.log("Deposit transaction submitted:", depositTxHash);

            toast.loading("Waiting for deposit confirmation...", {
                id: "transaction",
                description: (
                    <a
                        href={`https://sepolia.basescan.org/tx/${depositTxHash}`}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-blue-400 hover:text-blue-300 underline"
                    >
                        View on BaseScan ↗
                    </a>
                ),
            });

            const depositReceipt = await waitForDeposit(depositTxHash);

            if (depositReceipt.status !== "success") {
                throw new Error("Deposit transaction failed");
            }

            setTransactionStatus("success");
            console.log("All transactions confirmed on-chain!");

            toast.success("🎉 Sell order completed successfully!", {
                id: "transaction",
                duration: 10000,
                description: (
                    <div className="space-y-2">
                        <p>
                            Selling {spyAmount} DSPY for ~
                            {estimatedUsdcAmount || "?"} USDC
                        </p>
                        <div className="flex flex-col gap-1 text-xs">
                            {approvalTxHash && (
                                <a
                                    href={`https://sepolia.basescan.org/tx/${approvalTxHash}`}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="text-blue-400 hover:text-blue-300 underline"
                                >
                                    Approval: {approvalTxHash.slice(0, 10)}...
                                    {approvalTxHash.slice(-8)} ↗
                                </a>
                            )}
                            <a
                                href={`https://sepolia.basescan.org/tx/${depositTxHash}`}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="text-blue-400 hover:text-blue-300 underline"
                            >
                                Deposit: {depositTxHash.slice(0, 10)}...
                                {depositTxHash.slice(-8)} ↗
                            </a>
                        </div>
                        <p className="text-gray-400">
                            Your USDC will arrive shortly after processing.
                        </p>
                    </div>
                ),
            });

            // Clear the input after successful transaction
            setUsdcAmount("");
            setSpyAmount("");
        } catch (error) {
            console.error("Transaction failed:", error);
            setTransactionStatus("error");

            const errorDescription = (
                <div className="space-y-2">
                    <p>
                        {error instanceof Error
                            ? error.message
                            : "Unknown error occurred"}
                    </p>
                    {(approvalTxHash || depositTxHash) && (
                        <div className="flex flex-col gap-1 text-xs">
                            {approvalTxHash && (
                                <a
                                    href={`https://sepolia.basescan.org/tx/${approvalTxHash}`}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="text-blue-400 hover:text-blue-300 underline"
                                >
                                    Approval: {approvalTxHash.slice(0, 10)}...
                                    {approvalTxHash.slice(-8)} ↗
                                </a>
                            )}
                            {depositTxHash && (
                                <a
                                    href={`https://sepolia.basescan.org/tx/${depositTxHash}`}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="text-blue-400 hover:text-blue-300 underline"
                                >
                                    Deposit: {depositTxHash.slice(0, 10)}...
                                    {depositTxHash.slice(-8)} ↗
                                </a>
                            )}
                        </div>
                    )}
                </div>
            );

            toast.error("Transaction failed", {
                id: "transaction",
                description: errorDescription,
                duration: 10000,
            });
        }
    };

    const fetchSpyPrice = async (amount: string) => {
        if (!amount || isNaN(Number(amount))) {
            setEstimatedSpyAmount("");
            return;
        }

        setIsLoading(true);
        try {
            const response = await fetch(`/api/get_spy_price?amount=${amount}`);
            if (response.ok) {
                const data = await response.json();
                setEstimatedSpyAmount(data || "");
            } else {
                console.error("Failed to fetch SPY price");
                setEstimatedSpyAmount("");
            }
        } catch (error) {
            console.error("Error fetching SPY price:", error);
            setEstimatedSpyAmount("");
        } finally {
            setIsLoading(false);
        }
    };

    const fetchSpySellPrice = async (amount: string) => {
        if (!amount || isNaN(Number(amount))) {
            setEstimatedUsdcAmount("");
            return;
        }

        setIsLoading(true);
        try {
            const response = await fetch(
                `/api/get_spy_sell_price?amount=${amount}`,
            );
            if (response.ok) {
                const data = await response.json();
                setEstimatedUsdcAmount(data || "");
            } else {
                console.error("Failed to fetch SPY sell price");
                setEstimatedUsdcAmount("");
            }
        } catch (error) {
            console.error("Error fetching SPY sell price:", error);
            setEstimatedUsdcAmount("");
        } finally {
            setIsLoading(false);
        }
    };

    // Helper functions for UI
    const getButtonText = () => {
        if (!isConnected) return "Connect Wallet First";
        if (transactionStatus === "approving")
            return "Approving & Creating Order...";
        if (transactionStatus === "depositing") return "Processing Deposit...";
        if (transactionStatus === "success")
            return "Transactions initiated successfully!";
        if (transactionStatus === "error") return "Transaction Failed - Retry";
        return tradeType === "buy" ? "Buy SPY" : "Sell SPY";
    };

    const isButtonDisabled = () => {
        const amount = tradeType === "buy" ? usdcAmount : spyAmount;
        return (
            !isConnected ||
            !amount ||
            ["approving", "depositing"].includes(transactionStatus)
        );
    };

    // Reset transaction status after success/error
    useEffect(() => {
        if (transactionStatus === "success" || transactionStatus === "error") {
            const timer = setTimeout(() => setTransactionStatus("idle"), 5000);
            return () => clearTimeout(timer);
        }
    }, [transactionStatus]);

    const handleUsdcChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const value = e.target.value;
        // Only allow numbers and decimal point
        if (value === "" || /^\d*\.?\d*$/.test(value)) {
            setUsdcAmount(value);
        }
    };

    const handleSpyChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const value = e.target.value;
        if (value === "" || /^\d*\.?\d*$/.test(value)) {
            setSpyAmount(value);
        }
    };

    useEffect(() => {
        if (tradeType === "buy") {
            const timeoutId = setTimeout(() => {
                fetchSpyPrice(usdcAmount);
            }, 500); // Debounce API calls

            return () => clearTimeout(timeoutId);
        }
    }, [usdcAmount, tradeType]);

    // New useEffect for SPY amount changes (sell flow)
    useEffect(() => {
        if (tradeType === "sell") {
            const timeoutId = setTimeout(() => {
                fetchSpySellPrice(spyAmount);
            }, 500); // Debounce API calls

            return () => clearTimeout(timeoutId);
        }
    }, [spyAmount, tradeType]);

    // Clear opposite field when trade type changes
    useEffect(() => {
        if (tradeType === "buy") {
            setSpyAmount(""); // Clear DSPY amount when switching to buy
        } else {
            setUsdcAmount(""); // Clear USDC amount when switching to sell
        }
    }, [tradeType]);

    const fetchStatus = async () => {
        try {
            const response = await fetch("/api/status");
            if (response.ok) {
                const data = await response.json();
                // Make sure your backend returns both `message` and `is_open`
                setStatus({
                    message: data.message || "[Failed to fetch status]",
                    isOpen: data.is_open,
                });
            } else {
                setStatus({
                    message: "[Failed to fetch status]",
                    isOpen: null,
                });
            }
        } catch (error) {
            setStatus({ message: "[Failed to fetch status]", isOpen: null });
        }
    };

    // Auth state listener
    useEffect(() => {
        const supabase = createClient();

        // Check initial auth state
        const checkInitialAuth = async () => {
            try {
                const {
                    data: { user },
                    error,
                } = await supabase.auth.getUser();
                if (error || !user) {
                    router.push("/auth/login");
                    return;
                }
                setIsAuthenticated(true);
            } catch (error) {
                console.error("Auth check error:", error);
                router.push("/auth/login");
            } finally {
                setIsCheckingAuth(false);
            }
        };

        checkInitialAuth();

        // Listen for auth state changes
        const {
            data: { subscription },
        } = supabase.auth.onAuthStateChange((event, session) => {
            if (event === "SIGNED_IN" && session) {
                setIsAuthenticated(true);
                setIsCheckingAuth(false);
            } else if (event === "SIGNED_OUT") {
                setIsAuthenticated(false);
                router.push("/auth/login");
            }
        });

        return () => subscription.unsubscribe();
    }, [router]);

    useEffect(() => {
        // Only fetch status if authenticated
        if (!isAuthenticated) return;

        // Fetch status immediately on component mount
        fetchStatus();

        // Set up interval to fetch status every minute (60000ms)
        const statusInterval = setInterval(fetchStatus, 60000);

        return () => clearInterval(statusInterval);
    }, [isAuthenticated]);

    // Show loading spinner while checking authentication
    if (isCheckingAuth) {
        return (
            <div className="min-h-screen bg-[#10151c] flex items-center justify-center">
                <div className="text-white">Loading...</div>
            </div>
        );
    }

    // Don't render anything if not authenticated (redirect is in progress)
    if (!isAuthenticated) {
        return null;
    }
    return (
        <div className="min-h-screen bg-[#10151c] flex flex-col items-center justify-start pt-4 relative px-4 sm:px-0">
            {/* Background Illustration */}
            <div className="absolute bottom-0 left-0 w-full h-1/3 bg-gradient-to-t from-[#10151c] to-transparent pointer-events-none z-0" />

            {/* Navbar */}
            <Navbar
                walletAddressManager={
                    <WalletAddressManager>
                        <span className="text-gray-400 cursor-pointer hover:text-white transition-colors">
                            Register Testnet Wallet
                        </span>
                    </WalletAddressManager>
                }
                orderSummaryManager={
                    <OrderSummaryManager>
                        <span className="text-gray-400 cursor-pointer hover:text-white transition-colors">
                            Order Summary
                        </span>
                    </OrderSummaryManager>
                }
                connectWallet={<ConnectWallet />}
                handleAddDSP={handleAddDSP}
            />

            {/* Main Swap Card */}
            <Card className="w-[420px] mt-12 z-10 bg-[#181f2a] border-none shadow-xl">
                <CardContent className="p-6">
                    {/* Trade Type Toggle */}
                    <Tabs
                        value={tradeType}
                        onValueChange={setTradeType}
                        className="mb-6"
                    >
                        <TabsList className="flex gap-2 bg-[#10151c] rounded-lg p-1">
                            <TabsTrigger
                                value="buy"
                                className="flex-1 data-[state=active]:bg-green-400 data-[state=active]:text-[#10151c]"
                            >
                                Buy DSPY
                            </TabsTrigger>
                            <TabsTrigger
                                value="sell"
                                className="flex-1 data-[state=active]:bg-red-400 data-[state=active]:text-[#10151c]"
                            >
                                Sell DSPY
                            </TabsTrigger>
                        </TabsList>
                    </Tabs>

                    {/* Token Inputs */}
                    <div className="space-y-4">
                        <div>
                            <label className="text-gray-400 text-sm mb-1 block">
                                {tradeType === "buy" ? "Sending" : "Receiving"}
                            </label>
                            <div className="flex items-center bg-[#232b3b] rounded-lg px-3 py-2">
                                <Select>
                                    <SelectTrigger className="bg-transparent border-none text-white">
                                        USDC
                                    </SelectTrigger>
                                    <SelectContent>
                                        <SelectItem value="usdc">
                                            USDC
                                        </SelectItem>
                                    </SelectContent>
                                </Select>
                                <Input
                                    type="text"
                                    placeholder="0.00"
                                    value={
                                        tradeType === "sell" &&
                                        estimatedUsdcAmount
                                            ? `~ ${estimatedUsdcAmount}`
                                            : usdcAmount
                                    }
                                    onChange={handleUsdcChange}
                                    readOnly={tradeType === "sell"}
                                    className="ml-auto w-32 bg-transparent text-right text-white border-none outline-none"
                                />
                            </div>
                        </div>
                        <div>
                            <label className="text-gray-400 text-sm mb-1 block">
                                {tradeType === "sell" ? "Sending" : "Receiving"}
                            </label>
                            <div className="flex items-center bg-[#232b3b] rounded-lg px-3 py-2">
                                <Select>
                                    <SelectTrigger className="bg-transparent border-none text-white">
                                        SPY ETF
                                    </SelectTrigger>
                                    <SelectContent>
                                        <SelectItem value="SPY">
                                            DSPY
                                        </SelectItem>
                                    </SelectContent>
                                </Select>
                                <Input
                                    type="text"
                                    placeholder="0.00"
                                    value={
                                        tradeType === "buy" &&
                                        estimatedSpyAmount
                                            ? `~ ${estimatedSpyAmount}`
                                            : spyAmount
                                    }
                                    onChange={handleSpyChange}
                                    readOnly={tradeType === "buy"}
                                    className="ml-auto w-32 bg-transparent text-right text-white border-none outline-none"
                                />
                            </div>
                        </div>
                    </div>

                    {/* Connect/Trade Button */}
                    <Button
                        className={`w-full mt-6 font-bold ${
                            transactionStatus === "success"
                                ? "bg-green-600 text-white"
                                : transactionStatus === "error"
                                  ? "bg-red-500 text-white hover:bg-red-400"
                                  : tradeType === "buy"
                                    ? "bg-green-400 text-[#10151c] hover:bg-green-300"
                                    : "bg-red-400 text-[#10151c] hover:bg-red-300"
                        }`}
                        onClick={tradeType === "buy" ? handleBuy : handleSell}
                        disabled={isButtonDisabled()}
                    >
                        {getButtonText()}
                    </Button>
                </CardContent>
            </Card>

            {/* Chart Cards */}
            <div className="flex gap-4 mt-8 z-10">
                <Card className="w-64 bg-[#181f2a] border-none">
                    <CardContent className="p-4">
                        <div className="flex items-center gap-2">
                            <span className="bg-blue-500 rounded-full w-6 h-6"></span>
                            <span className="text-white font-bold">SPY</span>
                        </div>
                        <div
                            className={`mt-2 text-x ${
                                status.isOpen === true
                                    ? "text-green-400"
                                    : status.isOpen === false
                                      ? "text-red-400"
                                      : "text-pink-400"
                            }`}
                        >
                            {status.message}
                        </div>
                    </CardContent>
                </Card>
            </div>
        </div>
    );
}
