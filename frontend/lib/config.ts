import { http, createConfig } from "wagmi";
import { base } from "wagmi/chains";
import { injected, metaMask, safe, walletConnect } from "wagmi/connectors";

// const projectId = '<WALLETCONNECT_PROJECT_ID>'

export const config = createConfig({
    chains: [base],
    connectors: [
        injected(),
        // walletConnect({ projectId }),
        metaMask(),
        safe(),
    ],
    transports: {
        [base.id]: http(),
    },
});
