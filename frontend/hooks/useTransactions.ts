import {
    useWriteContract,
    useWaitForTransactionReceipt,
    useReadContract,
    usePublicClient,
} from "wagmi";
import { parseUnits } from "viem";
import {
    CONTRACTS,
    TOKEN_ABI,
    GATEWAY_ABI,
    stringToBytes32,
} from "@/lib/contracts";
import { useState } from "react";

export function useTokenApproval() {
    const { writeContractAsync } = useWriteContract();
    const publicClient = usePublicClient();

    const approveToken = async (
        tokenAddress: `0x${string}`,
        amount: string,
        decimals: number = 6,
    ) => {
        const amountWei = parseUnits(amount, decimals);

        // @ts-ignore
        const hash = await writeContractAsync({
            address: tokenAddress,
            abi: TOKEN_ABI,
            functionName: "approve",
            args: [CONTRACTS.TRANSACTIONGATEWAY_ADDRESS, amountWei],
        });

        return hash;
    };

    const waitForApproval = async (hash: `0x${string}`) => {
        if (!publicClient) throw new Error("Public client not available");

        const receipt = await publicClient.waitForTransactionReceipt({
            hash,
            confirmations: 1,
            timeout: 60_000,
        });

        return receipt;
    };

    return {
        approveToken,
        waitForApproval,
    };
}

export function useDeposits() {
    const { writeContractAsync } = useWriteContract();
    const publicClient = usePublicClient();

    const depositUSDC = async (amount: string, frontendHash: string) => {
        const parsedAmount = parseUnits(amount, 6);
        const frontendHashBytes32 = stringToBytes32(frontendHash);

        // @ts-ignore
        const hash = await writeContractAsync({
            address: CONTRACTS.TRANSACTIONGATEWAY_ADDRESS,
            abi: GATEWAY_ABI,
            functionName: "depositUSDC",
            args: [parsedAmount, frontendHashBytes32],
        });

        return hash;
    };

    const depositDSPY = async (amount: string, frontendHash: string) => {
        const parsedAmount = parseUnits(amount, 9); // DSPY has 9 decimals
        const frontendHashBytes32 = stringToBytes32(frontendHash);

        // @ts-ignore
        const hash = await writeContractAsync({
            address: CONTRACTS.TRANSACTIONGATEWAY_ADDRESS,
            abi: GATEWAY_ABI,
            functionName: "depositDSPY",
            args: [parsedAmount, frontendHashBytes32],
        });

        return hash;
    };

    const waitForDeposit = async (hash: `0x${string}`) => {
        if (!publicClient) throw new Error("Public client not available");

        const receipt = await publicClient.waitForTransactionReceipt({
            hash,
            confirmations: 1,
            timeout: 60_000,
        });

        return receipt;
    };

    return {
        depositUSDC,
        depositDSPY,
        waitForDeposit,
    };
}

export function useTokenBalance(
    tokenAddress: `0x${string}`,
    userAddress: `0x${string}` | undefined,
) {
    const { data: balance, isLoading } = useReadContract({
        address: tokenAddress,
        abi: TOKEN_ABI,
        functionName: "balanceOf",
        args: userAddress ? [userAddress] : undefined,
        query: {
            enabled: !!userAddress,
        },
    });

    return { balance, isLoading };
}

export function useTokenAllowance(
    tokenAddress: `0x${string}`,
    userAddress: `0x${string}` | undefined,
) {
    const { data: allowance, isLoading } = useReadContract({
        address: tokenAddress,
        abi: TOKEN_ABI,
        functionName: "allowance",
        args: userAddress
            ? [userAddress, CONTRACTS.TRANSACTIONGATEWAY_ADDRESS]
            : undefined,
        query: {
            enabled: !!userAddress,
        },
    });

    return { allowance, isLoading };
}
