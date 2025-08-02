"use client";

import React, { useState, useEffect, ReactNode } from "react";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogHeader,
    DialogTitle,
    DialogTrigger,
} from "@/components/ui/dialog";
import { CheckCircle, Edit, Save, X, Loader2, Wallet } from "lucide-react";

type WalletAddressManagerProps = {
    children?: ReactNode;
    triggerText?: string;
};

const WalletAddressManager = ({
    children,
    triggerText = "Register Testnet Wallet",
}: WalletAddressManagerProps) => {
    const [walletAddress, setWalletAddress] = useState("");
    const [isEditing, setIsEditing] = useState(false);
    const [tempAddress, setTempAddress] = useState("");
    const [error, setError] = useState("");
    const [success, setSuccess] = useState("");
    const [isLoading, setIsLoading] = useState(true);
    const [isSaving, setIsSaving] = useState(false);
    const [isOpen, setIsOpen] = useState(false);

    // Simple ERC20 address validation (Ethereum address format)
    const isValidEthereumAddress = (address: string) => {
        const ethereumAddressRegex = /^0x[a-fA-F0-9]{40}$/;
        return ethereumAddressRegex.test(address);
    };

    // Get auth token from cookies
    const getAuthToken = () => {
        const cookies = document.cookie.split(";");
        for (const cookie of cookies) {
            const [name, value] = cookie.trim().split("=");
            // Look for Supabase auth token cookie (includes project reference)
            if (name.includes("-auth-token") && name.startsWith("sb-")) {
                try {
                    // Decode the base64 encoded token
                    const decodedToken = atob(value.replace("base64-", ""));
                    const tokenData = JSON.parse(decodedToken);
                    // Return the actual JWT access token
                    return tokenData.access_token;
                } catch (error) {
                    console.error("Error parsing auth token:", error);
                    return null;
                }
            }
        }
        return null;
    };

    // Fetch existing wallet address
    const fetchWalletAddress = async () => {
        try {
            setIsLoading(true);
            setError("");

            const token = getAuthToken();
            if (!token) {
                setError("Authentication token not found");
                setWalletAddress("");
                return;
            }

            const response = await fetch("/api/get_wallet", {
                method: "GET",
                headers: {
                    "Content-Type": "application/json",
                    Authorization: `Bearer ${token}`,
                },
                credentials: "include",
            });

            if (response.ok) {
                const data = await response.json();
                // Handle the response format from backend: {"wallet_address": value}
                if (data && data.wallet_address) {
                    setWalletAddress(data.wallet_address);
                } else {
                    setWalletAddress("");
                }
            } else {
                // If endpoint returns error, assume no address exists
                setWalletAddress("");
            }
        } catch (err) {
            console.error("Error fetching wallet address:", err);
            setError("Failed to load wallet address");
            setWalletAddress("");
        } finally {
            setIsLoading(false);
        }
    };

    // Update wallet address via API
    const updateWalletAddress = async (address: string) => {
        try {
            setIsSaving(true);
            setError("");

            const token = getAuthToken();
            if (!token) {
                setError("Authentication token not found");
                return;
            }

            const response = await fetch("/api/add_wallet", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    Authorization: `Bearer ${token}`,
                },
                credentials: "include",
                body: JSON.stringify({ erc20_address: address }),
            });

            if (response.ok) {
                // const data = await response.json();
                setWalletAddress(address);
                setIsEditing(false);
                setSuccess("Wallet address saved successfully!");
                setTimeout(() => setSuccess(""), 3000);
                // Optionally close dialog after successful save
                // setTimeout(() => setIsOpen(false), 1500);
            } else {
                const errorData = await response.json();
                setError(errorData?.message || "Failed to save wallet address");
            }
        } catch (err) {
            console.error("Error updating wallet address:", err);
            setError("Failed to save wallet address");
        } finally {
            setIsSaving(false);
        }
    };

    // Load wallet address when dialog opens
    useEffect(() => {
        if (isOpen) {
            fetchWalletAddress();
        }
    }, [isOpen]);

    // Reset states when dialog opens
    const handleOpenChange = (open: boolean) => {
        setIsOpen(open);
        if (open) {
            setError("");
            setSuccess("");
            setIsEditing(false);
            setTempAddress("");
        }
    };

    const handleSaveAddress = async () => {
        setError("");
        setSuccess("");

        if (!tempAddress.trim()) {
            setError("Please enter a wallet address");
            return;
        }

        if (!isValidEthereumAddress(tempAddress)) {
            setError(
                "Please enter a valid Ethereum address (0x followed by 40 hexadecimal characters)",
            );
            return;
        }

        await updateWalletAddress(tempAddress);
    };

    const handleEdit = () => {
        setTempAddress(walletAddress);
        setIsEditing(true);
        setError("");
        setSuccess("");
    };

    const handleCancel = () => {
        setTempAddress("");
        setIsEditing(false);
        setError("");
    };

    const handleAddNew = () => {
        setTempAddress("");
        setIsEditing(true);
        setError("");
        setSuccess("");
    };

    return (
        <Dialog open={isOpen} onOpenChange={handleOpenChange}>
            <DialogTrigger asChild>
                {children || (
                    <Button variant="outline" className="gap-2">
                        <Wallet className="h-4 w-4" />
                        {triggerText}
                    </Button>
                )}
            </DialogTrigger>

            <DialogContent className="sm:max-w-md bg-gray-800 border-gray-700">
                <DialogHeader>
                    <DialogTitle className="text-white">
                        Testnet ERC20 Wallet
                    </DialogTitle>
                    <DialogDescription className="text-gray-300">
                        Manage your testnet Ethereum wallet address
                    </DialogDescription>
                </DialogHeader>

                <div className="space-y-4">
                    {/* Loading State */}
                    {isLoading && (
                        <div className="flex items-center justify-center py-8">
                            <Loader2 className="h-6 w-6 animate-spin text-gray-400" />
                            <span className="ml-2 text-gray-400">
                                Loading wallet address...
                            </span>
                        </div>
                    )}

                    {!isLoading && (
                        <>
                            {/* Success Alert */}
                            {success && (
                                <Alert className="border-green-600 bg-green-900/20">
                                    <CheckCircle className="h-4 w-4 text-green-400" />
                                    <AlertDescription className="text-green-300">
                                        {success}
                                    </AlertDescription>
                                </Alert>
                            )}

                            {/* Error Alert */}
                            {error && (
                                <Alert className="border-red-600 bg-red-900/20">
                                    <AlertDescription className="text-red-300">
                                        {error}
                                    </AlertDescription>
                                </Alert>
                            )}

                            {/* Display existing address */}
                            {walletAddress && !isEditing && (
                                <div className="space-y-3">
                                    <Label className="text-sm font-medium text-gray-200">
                                        Your Wallet Address:
                                    </Label>
                                    <div className="p-3 bg-gray-700 rounded-md border border-gray-600">
                                        <code className="text-xs break-all text-gray-100">
                                            {walletAddress}
                                        </code>
                                    </div>
                                    <Button
                                        onClick={handleEdit}
                                        className="w-full"
                                        variant="outline"
                                        disabled={isSaving}
                                    >
                                        <Edit className="w-4 h-4 mr-2" />
                                        Modify Address
                                    </Button>
                                </div>
                            )}

                            {/* Add new or edit form */}
                            {(!walletAddress || isEditing) && (
                                <div className="space-y-3">
                                    <Label
                                        htmlFor="wallet-address"
                                        className="text-sm font-medium text-gray-200"
                                    >
                                        {walletAddress ? "Update" : "Enter"}{" "}
                                        Wallet Address:
                                    </Label>
                                    <Input
                                        id="wallet-address"
                                        type="text"
                                        placeholder="0x1234567890123456789012345678901234567890"
                                        value={tempAddress}
                                        onChange={(e) =>
                                            setTempAddress(e.target.value)
                                        }
                                        className="font-mono text-xs bg-gray-700 border-gray-600 text-gray-100 placeholder-gray-400"
                                        disabled={isSaving}
                                    />
                                    <div className="flex gap-2">
                                        <Button
                                            onClick={handleSaveAddress}
                                            className="flex-1"
                                            disabled={isSaving}
                                        >
                                            {isSaving ? (
                                                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                                            ) : (
                                                <Save className="w-4 h-4 mr-2" />
                                            )}
                                            {isSaving
                                                ? "Saving..."
                                                : "Save Address"}
                                        </Button>
                                        {walletAddress && isEditing && (
                                            <Button
                                                onClick={handleCancel}
                                                variant="outline"
                                                className="flex-1"
                                                disabled={isSaving}
                                            >
                                                <X className="w-4 h-4 mr-2" />
                                                Cancel
                                            </Button>
                                        )}
                                    </div>
                                </div>
                            )}

                            {/* Add new button when address exists and not editing */}
                            {walletAddress && !isEditing && (
                                <Button
                                    onClick={handleAddNew}
                                    variant="secondary"
                                    className="w-full"
                                    disabled={isSaving}
                                >
                                    Replace with New Address
                                </Button>
                            )}

                            {/* Helper text */}
                            <div className="text-xs text-gray-400 space-y-1">
                                <p>• Address must start with "0x"</p>
                                <p>
                                    • Address must be exactly 42 characters long
                                </p>
                                <p>
                                    • Only hexadecimal characters (0-9, a-f,
                                    A-F) allowed
                                </p>
                            </div>
                        </>
                    )}
                </div>
            </DialogContent>
        </Dialog>
    );
};

export default WalletAddressManager;
