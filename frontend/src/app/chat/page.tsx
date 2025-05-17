'use client';

import { useState } from 'react';
import { Send } from 'lucide-react';
import Image from 'next/image';
import Navbar from "@/components/Navbar";
import { useLoading } from '@/context/LoadingContext';

interface QuickAction {
  text: string;
  icon?: string;
}

export default function ChatPage() {
  const [messages, setMessages] = useState<Array<{ text: string; isUser: boolean }>>([
    { text: "Hi 👋 How can I help you?", isUser: false }
  ]);
  const [inputValue, setInputValue] = useState('');
  const { setIsLoading } = useLoading();

  const quickActions: QuickAction[] = [
    { text: "Track my order 📦" },
    { text: "How do I track my order (FAQ)?" }
  ];

  const handleSend = () => {
    if (!inputValue.trim()) return;
    
    setMessages(prev => [...prev, { text: inputValue, isUser: true }]);
    setInputValue('');
    
    // Show loading state while waiting for response
    setIsLoading(true);
    
    // Simulate AI response
    setTimeout(() => {
      setMessages(prev => [...prev, { 
        text: "Let's take care of your order 📦\nPlease choose the right topic:", 
        isUser: false 
      }]);
      setIsLoading(false);
    }, 1000);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      <Navbar activeTab="" onTabChange={() => {}} />

      {/* Chat Container */}
      <div className="flex-1 max-w-6xl w-full mx-auto p-4">
        <div className="bg-white rounded-2xl shadow-lg h-[calc(100vh-12rem)] flex flex-col overflow-hidden">
          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {messages.map((message, index) => (
              <div
                key={index}
                className={`flex ${message.isUser ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[600px] rounded-[20px] p-4 shadow-sm ${
                    message.isUser
                      ? 'bg-gradient-to-br from-blue-500 to-blue-600 text-white'
                      : 'bg-gray-100 text-gray-800'
                  }`}
                >
                  <p className="text-base whitespace-pre-wrap">{message.text}</p>
                </div>
              </div>
            ))}

            {/* Quick Actions */}
            {messages.length === 2 && (
              <div className="space-y-2 mt-4 max-w-[600px]">
                {quickActions.map((action, index) => (
                  <button
                    key={index}
                    onClick={() => {
                      setMessages(prev => [...prev, { text: action.text, isUser: true }]);
                    }}
                    className="w-full text-left px-5 py-3 rounded-2xl border border-blue-100 text-blue-600 hover:bg-blue-50 hover:border-blue-200 transition-all duration-200"
                  >
                    {action.text}
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* Input */}
          <div className="p-4 bg-gray-50/50 border-t border-gray-100">
            <div className="max-w-6xl mx-auto">
              <div className="flex items-center gap-2 bg-white rounded-2xl p-2 shadow-sm ring-1 ring-gray-100">
                <input
                  type="text"
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  onKeyDown={handleKeyPress}
                  placeholder="Type your message..."
                  className="flex-1 bg-transparent px-3 py-2 focus:outline-none text-base"
                />
                <button
                  onClick={handleSend}
                  disabled={!inputValue.trim()}
                  className="p-2 rounded-xl bg-gradient-to-r from-blue-500 to-blue-600 text-white hover:from-blue-600 hover:to-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200"
                >
                  <Send className="h-5 w-5" />
                </button>
              </div>
              <div className="text-[10px] text-gray-400 text-right mt-2">
                Powered by SympAI
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
} 