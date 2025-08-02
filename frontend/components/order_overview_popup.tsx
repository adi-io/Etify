import React, { useState } from "react";
import OrdersTable from "./order_overview";
import Modal from "./modal";

export default function OrderSummaryManager({ children }) {
    const [open, setOpen] = useState(false);
    return (
        <>
            <span
                onClick={() => setOpen(true)}
                className=" text-gray-400 cursor-pointer hover:text-white transition-colors"
            >
                {children}
            </span>
            <Modal open={open} onClose={() => setOpen(false)}>
                <OrdersTable />
            </Modal>
        </>
    );
}
