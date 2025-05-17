'use client';

import { useState } from 'react';
import { Send, X, Maximize2 } from 'lucide-react';
import Image from 'next/image';
import Link from 'next/link';

interface AiChatWindowProps {
  onClose: () => void;
}

interface QuickAction {
  text: string;
  icon?: string;
}

export default function AiChatWindow({ onClose }: AiChatWindowProps) {
  const [messages, setMessages] = useState<Array<{ text: string; isUser: boolean }>>([
    { text: "Hi 👋 How can I help you?", isUser: false }
  ]);
  const [inputValue, setInputValue] = useState('');

  const quickActions: QuickAction[] = [
    { text: "Track my order 📦" },
    { text: "How do I track my order (FAQ)?" }
  ];

  const handleSend = () => {
    if (!inputValue.trim()) return;
    
    setMessages(prev => [...prev, { text: inputValue, isUser: true }]);
    setInputValue('');
    
    // Simulate AI response
    setTimeout(() => {
      setMessages(prev => [...prev, { 
        text: "Let's take care of your order 📦\nPlease choose the right topic:", 
        isUser: false 
      }]);
    }, 1000);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="fixed bottom-0 right-0 sm:relative w-full sm:w-[400px] md:w-[500px] h-[100dvh] sm:h-[600px] bg-white sm:rounded-[24px] shadow-2xl flex flex-col overflow-hidden [&>button]:hidden">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-blue-500 p-3 sm:p-4 text-white">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2 sm:gap-3">
            <div className="relative">
              <div className="w-10 h-10 sm:w-12 sm:h-12 rounded-full overflow-hidden bg-white ring-2 ring-white/20">
                <Image
                  src="/images/chatavatar.png"
                  alt="Assistant"
                  width={48}
                  height={48}
                  className="object-contain"
                />
              </div>
              <div className="absolute bottom-0 right-0 w-2.5 h-2.5 sm:w-3 sm:h-3 bg-green-400 rounded-full ring-2 ring-white"></div>
            </div>
            <div>
              <h3 className="font-semibold text-base sm:text-lg">SympAI</h3>
              <p className="text-xs sm:text-sm text-white/80">Online • Ready to help</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Link
              href="/chat"
              className="hidden sm:flex hover:bg-white/10 rounded-full p-1.5 sm:p-2 transition-all items-center justify-center"
            >
              <Maximize2 className="h-5 w-5" />
            </Link>
            <button 
              onClick={onClose} 
              className="hover:bg-white/10 rounded-full p-1.5 sm:p-2 transition-all"
            >
              <X className="h-5 w-5" />
            </button>
          </div>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-3 sm:p-4 space-y-3 sm:space-y-4">
        {messages.map((message, index) => (
          <div
            key={index}
            className={`flex ${message.isUser ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-[85%] sm:max-w-[80%] rounded-[16px] sm:rounded-[20px] p-3 sm:p-3.5 shadow-sm ${
                message.isUser
                  ? 'bg-gradient-to-br from-blue-500 to-blue-600 text-white'
                  : 'bg-gray-100 text-gray-800'
              }`}
            >
              <p className="text-sm sm:text-base whitespace-pre-wrap">{message.text}</p>
            </div>
          </div>
        ))}

        {/* Quick Actions */}
        {messages.length === 2 && (
          <div className="space-y-2 mt-3 sm:mt-4">
            {quickActions.map((action, index) => (
              <button
                key={index}
                onClick={() => {
                  setMessages(prev => [...prev, { text: action.text, isUser: true }]);
                }}
                className="w-full text-left px-4 sm:px-5 py-2.5 sm:py-3 rounded-xl sm:rounded-2xl border border-blue-100 text-blue-600 hover:bg-blue-50 hover:border-blue-200 transition-all duration-200 text-sm sm:text-base"
              >
                {action.text}
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Input */}
      <div className="p-3 sm:p-4 bg-gray-50/50 border-t border-gray-100">
        <div className="flex items-center gap-2 bg-white rounded-xl sm:rounded-2xl p-1.5 shadow-sm ring-1 ring-gray-100">
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyDown={handleKeyPress}
            placeholder="Type your message..."
            className="flex-1 bg-transparent px-2 sm:px-3 focus:outline-none text-sm"
          />
          <button
            onClick={handleSend}
            disabled={!inputValue.trim()}
            className="p-1.5 sm:p-2 rounded-lg sm:rounded-xl bg-gradient-to-r from-blue-500 to-blue-600 text-white hover:from-blue-600 hover:to-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200"
          >
            <Send className="h-4 w-4 sm:h-5 sm:w-5" />
          </button>
        </div>
        <div className="text-[10px] text-gray-400 text-right mt-2">
          Powered by SympAI
        </div>
      </div>
    </div>
  );
} 