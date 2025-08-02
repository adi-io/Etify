import React from "react";

export default function Modal({ open, onClose, children }) {
    if (!open) return null;
    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70">
            <div className="relative bg-gray-900 w-full h-full max-w-full max-h-screen sm:max-w-3xl sm:h-auto sm:rounded-lg overflow-auto shadow-lg">
                <button
                    onClick={onClose}
                    className="absolute top-4 right-4 text-gray-400 hover:text-white z-10 text-2xl"
                    aria-label="Close"
                >
                    ×
                </button>
                {children}
            </div>
        </div>
    );
}
