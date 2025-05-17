'use client';

import { useState } from 'react';
import { MessageCircle, X } from 'lucide-react';
import AiChatWindow from './AiChatWindow';

export default function AiChatButton() {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className="fixed bottom-0 sm:bottom-4 right-0 sm:right-4 z-50">
      {isOpen ? (
        <div className="relative sm:mb-4">
          <AiChatWindow onClose={() => setIsOpen(false)} />
        </div>
      ) : (
        <button
          onClick={() => setIsOpen(true)}
          className="flex h-12 w-12 sm:h-14 sm:w-14 items-center justify-center rounded-full bg-blue-600 text-white shadow-lg hover:bg-blue-700 transition-all duration-200 hover:scale-110 m-4 sm:m-0"
        >
          <MessageCircle className="h-6 w-6 sm:h-7 sm:w-7" />
        </button>
      )}
    </div>
  );
} 