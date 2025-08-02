import { Menu } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Sheet, SheetContent, SheetTrigger } from "@/components/ui/sheet";

export default function Navbar({
    walletAddressManager,
    orderSummaryManager,
    connectWallet,
    handleAddDSP,
    signOutUrl = "/auth/logout",
}) {
    return (
        <nav className="w-full flex justify-between items-center px-8 py-4 bg-[#181f2a] rounded-md">
            {/* Desktop navbar */}
            <div className="flex items-center gap-8">
                <a href="/" className="font-bold text-white text-lg">
                    Etify
                </a>
                <div className="hidden md:flex items-center gap-8">
                    {walletAddressManager}
                    {orderSummaryManager}
                </div>
            </div>
            <div className="hidden md:flex items-center gap-4">
                {connectWallet}
                <Button
                    variant="ghost"
                    className="text-green-400 border border-green-400"
                    onClick={handleAddDSP}
                >
                    Add DSPY to Wallet
                </Button>
                <Button
                    variant="ghost"
                    className="text-green-400 border border-green-400"
                    asChild
                >
                    <a href={signOutUrl}>Sign out</a>
                </Button>
            </div>

            {/* Mobile hamburger menu */}
            <div className="md:hidden">
                <Sheet>
                    <SheetTrigger asChild>
                        <Button
                            variant="ghost"
                            size="icon"
                            className="shrink-0"
                        >
                            <Menu className="size-5" color="#fff" />
                            <span className="sr-only">
                                Toggle navigation menu
                            </span>
                        </Button>
                    </SheetTrigger>
                    <SheetContent
                        side="right"
                        className="bg-[#181f2a] text-gray-100 px-6 py-8"
                    >
                        <nav className="flex flex-col gap-6 text-lg font-medium">
                            <a
                                href="/"
                                className="font-bold text-xl text-white mb-2"
                            >
                                Etify
                            </a>
                            <div className="flex flex-col gap-2">
                                {walletAddressManager}
                                {orderSummaryManager}
                            </div>
                            <div className="flex flex-col gap-4 mt-4">
                                {connectWallet}
                                <Button
                                    variant="ghost"
                                    className="text-green-400 border border-green-400"
                                    onClick={handleAddDSP}
                                >
                                    Add DSPY to Wallet
                                </Button>
                                <Button
                                    variant="ghost"
                                    className="text-green-400 border border-green-400"
                                    asChild
                                >
                                    <a href={signOutUrl}>Sign out</a>
                                </Button>
                            </div>
                        </nav>
                    </SheetContent>
                </Sheet>
            </div>
        </nav>
    );
}
