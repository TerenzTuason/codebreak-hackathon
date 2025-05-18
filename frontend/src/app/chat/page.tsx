'use client';

import { useState, useRef, useEffect } from 'react';
import { Send } from 'lucide-react';
import Navbar from "@/components/Navbar";
import { useLoading } from '@/context/LoadingContext';
import { motion, AnimatePresence } from 'framer-motion';

interface Message {
  text: string;
  isUser: boolean;
  type?: 'text' | 'voice' | 'image';
  metadata?: {
    imageUrl?: string;
    audioUrl?: string;
    tier?: number;
    priority?: 'URGENT' | 'HIGH';
    escalation_contact?: {
      name: string;
      email: string;
      phone: string;
    };
    required_data?: string[];
    intent?: string;
  };
}

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([
    { text: "Hi 👋 How can I help you?", isUser: false }
  ]);
  const [inputValue, setInputValue] = useState('');
  const { setIsLoading } = useLoading();
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (!inputValue.trim()) return;
    
    // Add user message
    setMessages(prev => [...prev, { text: inputValue, isUser: true }]);
    setInputValue('');
    
    setIsLoading(true);
    
    try {
      // Call the AI prediction endpoint
      const response = await fetch('https://ai-training-kappa.vercel.app/predict', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: inputValue
        })
      });

      const data = await response.json();

      // Create AI response message
      let responseText = data.tier === 0 ? data.message : (data.suggested_response || data.message);
      
      // For higher tiers, add context about escalation
      if (data.tier >= 2) {
        responseText = `${responseText}\n\n${data.message}`;
        
        if (data.escalation_contact) {
          responseText += `\n\nA specialist (${data.escalation_contact.name}) will contact you shortly.`;
          if (data.priority === 'URGENT') {
            responseText += ' This is marked as URGENT.';
          }
        }
      }

      const newMessage: Message = {
        text: responseText,
        isUser: false,
        metadata: {
          tier: data.tier,
          priority: data.priority,
          escalation_contact: data.escalation_contact,
          required_data: data.required_data,
          intent: data.intent
        }
      };

      setMessages(prev => [...prev, newMessage]);
    } catch {
      // Handle error case
      setMessages(prev => [...prev, {
        text: "I apologize, but I'm having trouble connecting to the server. Please try again later.",
        isUser: false
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      <Navbar activeTab="chat" onTabChange={() => {}} />

      {/* Chat Container */}
      <div className="flex-1 max-w-6xl w-full mx-auto p-4">
        <div className="bg-white rounded-2xl shadow-lg h-[calc(100vh-12rem)] flex flex-col overflow-hidden">
          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            <AnimatePresence>
              {messages.map((message, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -20 }}
                  className={`flex ${message.isUser ? 'justify-end' : 'justify-start'}`}
                >
                  <div className={`max-w-[600px] rounded-[20px] p-4 ${
                    message.isUser
                      ? 'bg-gradient-to-br from-blue-500 to-blue-600 text-white'
                      : 'bg-gray-100 text-gray-800'
                  }`}>
                    {/* Message text with tier-based styling */}
                    <div className="space-y-2">
                      {message.metadata?.tier !== undefined && message.metadata.tier > 1 && (
                        <div className={`text-xs font-medium rounded-full px-2 py-0.5 inline-block mb-2 ${
                          message.metadata.priority === 'URGENT'
                            ? 'bg-red-100 text-red-700'
                            : message.metadata.priority === 'HIGH'
                            ? 'bg-orange-100 text-orange-700'
                            : 'bg-blue-100 text-blue-700'
                        }`}>
                          {message.metadata.priority || `Tier ${message.metadata.tier}`}
                        </div>
                      )}
                      
                      <p className="text-base whitespace-pre-wrap">{message.text}</p>

                      {/* Escalation contact info */}
                      {message.metadata?.escalation_contact && (
                        <div className="mt-2 text-xs bg-white/10 rounded-lg p-2">
                          <p className="font-medium">Contact Information:</p>
                          <p>{message.metadata.escalation_contact.name}</p>
                          <p>{message.metadata.escalation_contact.email}</p>
                          <p>{message.metadata.escalation_contact.phone}</p>
                        </div>
                      )}
                    </div>
                  </div>
                </motion.div>
              ))}
              <div ref={messagesEndRef} />
            </AnimatePresence>
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