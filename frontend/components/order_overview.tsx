import React, { useState, useMemo, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";

const OrdersTable = () => {
    const [ordersData, setOrdersData] = useState([]);
    const [filter, setFilter] = useState("buy");
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState("");

    // Get auth token from cookies
    const getAuthToken = () => {
        const cookies = document.cookie.split(";");
        for (const cookie of cookies) {
            const [name, value] = cookie.trim().split("=");
            if (name.includes("-auth-token") && name.startsWith("sb-")) {
                try {
                    const decodedToken = atob(value.replace("base64-", ""));
                    const tokenData = JSON.parse(decodedToken);
                    return tokenData.access_token;
                } catch (error) {
                    console.error("Error parsing auth token:", error);
                    return null;
                }
            }
        }
        return null;
    };

    // Fetch orders data from API
    const fetchOrders = async () => {
        try {
            setIsLoading(true);
            setError("");
            const token = getAuthToken();
            if (!token) {
                setError("Authentication token not found");
                return;
            }

            const response = await fetch("/api/get_all_orders", {
                method: "GET",
                headers: {
                    "Content-Type": "application/json",
                    Authorization: `Bearer ${token}`,
                },
                credentials: "include",
            });

            if (response.ok) {
                const data = await response.json();
                setOrdersData(data.orders || []);
            } else {
                const errorData = await response.json().catch(() => ({}));
                setError(
                    errorData.error ||
                        `Failed to fetch orders: ${response.status}`,
                );
            }
        } catch (err) {
            console.error("Error fetching orders:", err);
            setError("Failed to load orders");
        } finally {
            setIsLoading(false);
        }
    };

    useEffect(() => {
        fetchOrders();
        // eslint-disable-next-line
    }, []);

    const getOrderType = (order) => {
        if (order.event === "BUY_ORDER_FILLED_TOKEN_MINTED") {
            return "buy";
        }
        if (
            order.event.includes("BURNING") ||
            order.event.includes("REDEMPTION") ||
            order.event.includes("SELL_ORDER")
        ) {
            return "sell";
        }
        return "unknown";
    };

    const filteredOrders = useMemo(() => {
        return ordersData.filter((order) => getOrderType(order) === filter);
    }, [filter, ordersData]);

    const formatCurrency = (value) => {
        if (value === null || value === undefined) return "-";
        return new Intl.NumberFormat("en-US", {
            style: "currency",
            currency: "USD",
            minimumFractionDigits: 2,
            maximumFractionDigits: 6,
        }).format(value);
    };

    const formatDate = (dateString) => {
        return new Date(dateString).toLocaleString();
    };

    const formatHash = (hash) => {
        return hash.substring(0, 8) + "...";
    };

    return (
        <div className="w-full max-w-7xl mx-auto p-2 sm:p-4 bg-gray-900 min-h-screen sm:min-h-0">
            <Card className="bg-gray-800 border-gray-700">
                <CardHeader>
                    <CardTitle className="text-2xl font-bold text-white">
                        Trading Orders
                    </CardTitle>
                    <div className="flex flex-col sm:flex-row gap-2 mt-4">
                        <Button
                            variant={filter === "buy" ? "default" : "outline"}
                            onClick={() => setFilter("buy")}
                            className={`w-full sm:w-auto px-4 py-2 ${filter === "buy" ? "bg-green-600 hover:bg-green-700 text-white" : "border-gray-600 text-gray-300 hover:bg-gray-700 hover:text-white"}`}
                            disabled={isLoading}
                        >
                            Buy Orders (
                            {
                                ordersData.filter(
                                    (o) => getOrderType(o) === "buy",
                                ).length
                            }
                            )
                        </Button>
                        <Button
                            variant={filter === "sell" ? "default" : "outline"}
                            onClick={() => setFilter("sell")}
                            className={`w-full sm:w-auto px-4 py-2 ${filter === "sell" ? "bg-red-600 hover:bg-red-700 text-white" : "border-gray-600 text-gray-300 hover:bg-gray-700 hover:text-white"}`}
                            disabled={isLoading}
                        >
                            Sell Orders (
                            {
                                ordersData.filter(
                                    (o) => getOrderType(o) === "sell",
                                ).length
                            }
                            )
                        </Button>
                        <Button
                            variant="outline"
                            onClick={fetchOrders}
                            className="w-full sm:w-auto px-4 py-2 border-gray-600 text-gray-300 hover:bg-gray-700 hover:text-white"
                            disabled={isLoading}
                        >
                            {isLoading ? "Loading..." : "Refresh"}
                        </Button>
                    </div>
                </CardHeader>
                <CardContent className="bg-gray-800">
                    {error && (
                        <div className="mb-4 p-4 bg-red-900 border border-red-700 rounded-md">
                            <p className="text-red-300">{error}</p>
                        </div>
                    )}
                    {isLoading && (
                        <div className="text-center py-8 text-gray-400">
                            Loading orders...
                        </div>
                    )}
                    <div className="overflow-x-auto">
                        <table className="w-full border-collapse min-w-[700px] text-xs sm:text-sm">
                            <thead>
                                <tr className="border-b border-gray-600">
                                    <th className="text-left p-2 sm:p-3 font-semibold text-gray-200">
                                        Order ID
                                    </th>
                                    <th className="text-left p-2 sm:p-3 font-semibold text-gray-200">
                                        Type
                                    </th>
                                    <th className="text-left p-2 sm:p-3 font-semibold text-gray-200">
                                        Event
                                    </th>
                                    <th className="text-left p-2 sm:p-3 font-semibold text-gray-200">
                                        Date
                                    </th>
                                    {filter === "buy" && (
                                        <>
                                            <th className="text-left p-2 sm:p-3 font-semibold text-gray-200">
                                                User sent USDC
                                            </th>
                                            <th className="text-left p-2 sm:p-3 font-semibold text-gray-200">
                                                ETF purchase price
                                            </th>
                                            <th className="text-left p-2 sm:p-3 font-semibold text-gray-200">
                                                Token minting fee
                                            </th>
                                            <th className="text-left p-2 sm:p-3 font-semibold text-gray-200">
                                                Net order value (BUY)
                                            </th>
                                            <th className="text-left p-2 sm:p-3 font-semibold text-gray-200">
                                                ETF bought
                                            </th>
                                        </>
                                    )}
                                    {filter === "sell" && (
                                        <>
                                            <th className="text-left p-2 sm:p-3 font-semibold text-gray-200">
                                                User sent DSPY
                                            </th>
                                            <th className="text-left p-2 sm:p-3 font-semibold text-gray-200">
                                                Total sell value
                                            </th>
                                            <th className="text-left p-2 sm:p-3 font-semibold text-gray-200">
                                                Token redemption fee
                                            </th>
                                            <th className="text-left p-2 sm:p-3 font-semibold text-gray-200">
                                                Net order value (SELL)
                                            </th>
                                        </>
                                    )}
                                </tr>
                            </thead>
                            <tbody>
                                {filteredOrders.map((order, index) => {
                                    const orderType = getOrderType(order);
                                    return (
                                        <tr
                                            key={order.frontend_hash}
                                            className={`border-b border-gray-700 hover:bg-gray-700 ${index % 2 === 0 ? "bg-gray-800" : "bg-gray-750"}`}
                                        >
                                            <td className="p-2 sm:p-3 font-mono text-xs sm:text-sm text-gray-300">
                                                {formatHash(
                                                    order.frontend_hash,
                                                )}
                                            </td>
                                            <td className="p-2 sm:p-3">
                                                <Badge
                                                    variant={
                                                        orderType === "buy"
                                                            ? "default"
                                                            : orderType ===
                                                                "sell"
                                                              ? "destructive"
                                                              : "secondary"
                                                    }
                                                    className={
                                                        orderType === "buy"
                                                            ? "bg-green-600 hover:bg-green-700 text-white"
                                                            : orderType ===
                                                                "sell"
                                                              ? "bg-red-600 hover:bg-red-700 text-white"
                                                              : "bg-gray-600 hover:bg-gray-700 text-white"
                                                    }
                                                >
                                                    {orderType.toUpperCase()}
                                                </Badge>
                                            </td>
                                            <td className="p-2 sm:p-3 text-xs sm:text-sm text-gray-300">
                                                {order.event}
                                            </td>
                                            <td className="p-2 sm:p-3 text-xs sm:text-sm text-gray-300">
                                                {formatDate(order.created_at)}
                                            </td>
                                            {filter === "buy" && (
                                                <>
                                                    <td className="p-2 sm:p-3 text-gray-300">
                                                        {formatCurrency(
                                                            order.usdc_received_from_user,
                                                        )}
                                                    </td>
                                                    <td className="p-2 sm:p-3 text-gray-300">
                                                        {formatCurrency(
                                                            order.dspy_average_minting_price,
                                                        )}
                                                    </td>
                                                    <td className="p-2 sm:p-3 text-gray-300">
                                                        {formatCurrency(
                                                            order.user_spy_buy_order_fee,
                                                        )}
                                                    </td>
                                                    <td className="p-2 sm:p-3 text-gray-300">
                                                        {formatCurrency(
                                                            order.user_spy_net_buy_order_value,
                                                        )}
                                                    </td>
                                                    <td className="p-2 sm:p-3 text-gray-300">
                                                        {order.dspy_mint_filled_quantity
                                                            ? order.dspy_mint_filled_quantity.toFixed(
                                                                  6,
                                                              )
                                                            : "-"}
                                                    </td>
                                                </>
                                            )}
                                            {filter === "sell" && (
                                                <>
                                                    <td className="p-2 sm:p-3 text-gray-300">
                                                        {order.dspy_received_from_user ||
                                                            "-"}
                                                    </td>
                                                    <td className="p-2 sm:p-3 text-gray-300">
                                                        {formatCurrency(
                                                            order.user_spy_sell_order_value_usd,
                                                        )}
                                                    </td>
                                                    <td className="p-2 sm:p-3 text-gray-300">
                                                        {formatCurrency(
                                                            order.user_spy_sell_order_fee_usd,
                                                        )}
                                                    </td>
                                                    <td className="p-2 sm:p-3 text-gray-300">
                                                        {formatCurrency(
                                                            order.user_spy_sell_net_order_value_usd,
                                                        )}
                                                    </td>
                                                </>
                                            )}
                                        </tr>
                                    );
                                })}
                            </tbody>
                        </table>
                    </div>
                    {filteredOrders.length === 0 && !isLoading && !error && (
                        <div className="text-center py-8 text-gray-400">
                            No orders found for the selected filter.
                        </div>
                    )}
                </CardContent>
            </Card>
        </div>
    );
};

export default OrdersTable;
