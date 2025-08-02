import { parseUnits } from "viem";
import DSPYABI from "@/abi/TokenIssuerABI.json";
import GatewayABI from "@/abi/TransactionGatewayABI.json";

// Contract addresses (move these to env variables)
export const CONTRACTS = {
    DSPY_ADDRESS: "0xEbfd0F43a86278c9E08b9Ae76f5Caa901eC16322",
    USDC_ADDRESS: "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
    TRANSACTIONGATEWAY_ADDRESS: "0x2572C074DEbE6daff54cA99B9467a4cE19C2867B",
} as const;

export const TOKEN_ABI = DSPYABI;
export const GATEWAY_ABI = GatewayABI;

// Utility functions
export const stringToBytes32 = (str: string): `0x${string}` => {
    // Convert string to bytes32 format
    return `0x${str.padEnd(64, "0")}` as `0x${string}`;
};

export const parseTokenAmount = (amount: string, decimals: number = 18) => {
    return parseUnits(amount, decimals);
};
