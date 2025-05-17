'use client';

import { useState } from 'react';
import { MessageCircle, X } from 'lucide-react';
import AiChatWindow from './AiChatWindow';

export default function AiChatButton() {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className="fixed bottom-4 right-4 z-50">
      {isOpen ? (
        <div className="relative">
          <AiChatWindow onClose={() => setIsOpen(false)} />
        </div>
      ) : (
        <button
          onClick={() => setIsOpen(true)}
          className="flex h-14 w-14 items-center justify-center rounded-full bg-blue-600 text-white shadow-lg hover:bg-blue-700 transition-all duration-200 hover:scale-110"
        >
          <MessageCircle className="h-7 w-7" />
        </button>
      )}
    </div>
  );
} 