'use client';

import React, { useState, useRef, useEffect } from 'react';
import { Send, X, Maximize2 } from 'lucide-react';
import Image from 'next/image';
import Link from 'next/link';
import { motion, AnimatePresence } from 'framer-motion';
import { useLoading } from '@/context/LoadingContext';
import { usePathname } from 'next/navigation';

interface AiChatWindowProps {
  onClose: () => void;
}

interface AiResponse {
  intent: string;
  confidence: number;
  tier: number;
  message: string;
  suggested_response?: string;
  automated: boolean;
  priority?: 'URGENT' | 'HIGH';
  escalation_contact?: {
    name: string;
    email: string;
    phone: string;
  };
  required_data?: string[];
}

interface Message {
  text: string;
  isUser: boolean;
  type?: 'text' | 'voice' | 'image';
  metadata?: {
    imageUrl?: string;
    audioUrl?: string;
    suggestions?: string[];
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

export default function AiChatWindow({ onClose }: AiChatWindowProps) {
  const pathname = usePathname();
  
  const getInitialMessage = (): Message => {
    if (pathname === '/health-records') {
      return {
        text: "Hi! I can help you understand your health records or answer any questions about your medical history. What would you like to know?",
        isUser: false,
        metadata: {
          suggestions: [
            "Explain my current medications",
            "What do my blood test results mean?",
            "Summarize my medical history",
            "Any concerning patterns in my family history?"
          ]
        }
      };
    }
    
    // Default message for other pages
    return {
      text: "Hi 👋 How can I help you?",
      isUser: false,
      metadata: {
        suggestions: [
          "I have a headache",
          "Check my symptoms",
          "Medical advice needed"
        ]
      }
    };
  };

  const [messages, setMessages] = useState<Message[]>([getInitialMessage()]);
  const [inputValue, setInputValue] = useState('');
  const { setIsLoading } = useLoading();
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const getTierBasedSuggestions = (tier: number): string[] => {
    switch(tier) {
      case 4:
        return [
          "Contact emergency services",
          "Call legal department",
          "Request urgent callback"
        ];
      case 3:
        return [
          "Schedule specialist consultation",
          "Submit additional information",
          "Request priority review"
        ];
      case 2:
        return [
          "Provide more details",
          "Schedule follow-up",
          "Check status later"
        ];
      case 1:
        return [
          "Could you provide more details?",
          "Let me connect you with a human agent",
          "Would you like to rephrase your question?"
        ];
      default:
        return [
          "Ask another question",
          "Book an appointment",
          "Check other services"
        ];
    }
  };

  const handleSend = async () => {
    if (!inputValue.trim()) return;
    
    // Add user message
    setMessages((prev: Message[]) => [...prev, { text: inputValue, isUser: true }]);
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

      const data: AiResponse = await response.json();

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
          suggestions: getTierBasedSuggestions(data.tier),
          tier: data.tier,
          priority: data.priority,
          escalation_contact: data.escalation_contact,
          required_data: data.required_data,
          intent: data.intent
        }
      };

      setMessages((prev: Message[]) => [...prev, newMessage]);
    } catch {
      // Handle error case
      setMessages((prev: Message[]) => [...prev, {
        text: "I apologize, but I'm having trouble connecting to the server. Please try again later.",
        isUser: false,
        metadata: {
          suggestions: [
            "Try again",
            "Contact support",
            "Check system status"
          ]
        }
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
    <div className="fixed bottom-0 right-0 sm:relative w-full sm:w-[320px] md:w-[360px] h-[100dvh] sm:h-[500px] bg-white sm:rounded-[20px] shadow-2xl flex flex-col overflow-hidden">
      {/* Header */}
      <motion.div 
        initial={{ y: -20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        className="bg-gradient-to-r from-blue-600 to-blue-500 p-2.5 sm:p-3 text-white"
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="relative">
              <div className="w-8 h-8 sm:w-10 sm:h-10 rounded-full overflow-hidden bg-white ring-2 ring-white/20">
                <Image
                  src="/images/chatavatar.png"
                  alt="Assistant"
                  width={40}
                  height={40}
                  className="object-contain"
                />
              </div>
              <motion.div 
                className="absolute bottom-0 right-0 w-2 h-2 sm:w-2.5 sm:h-2.5 bg-green-400 rounded-full ring-2 ring-white"
                animate={{
                  scale: [1, 1.2, 1],
                  opacity: [1, 0.7, 1],
                }}
                transition={{
                  duration: 2,
                  repeat: Infinity,
                  ease: "easeInOut"
                }}
              />
            </div>
            <div>
              <h3 className="font-semibold text-sm sm:text-base">SympAI</h3>
              <p className="text-[10px] sm:text-xs text-white/80">Online • Ready to help</p>
            </div>
          </div>
          <div className="flex items-center gap-1.5">
            <Link
              href="/chat"
              className="hidden sm:flex hover:bg-white/10 rounded-full p-1.5 transition-all items-center justify-center"
            >
              <Maximize2 className="h-4 w-4" />
            </Link>
            <button 
              onClick={onClose} 
              className="hover:bg-white/10 rounded-full p-1.5 transition-all"
            >
              <X className="h-4 w-4" />
            </button>
          </div>
        </div>
      </motion.div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-3 space-y-3">
        <AnimatePresence>
          {messages.map((message, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className={`flex ${message.isUser ? 'justify-end' : 'justify-start'}`}
            >
              <div className={`max-w-[85%] rounded-2xl p-3 ${
                message.isUser
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-900'
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
                  
                  <p className="whitespace-pre-wrap text-sm">{message.text}</p>

                  {/* Escalation contact info */}
                  {message.metadata?.escalation_contact && (
                    <div className="mt-2 text-xs bg-white/10 rounded-lg p-2">
                      <p className="font-medium">Contact Information:</p>
                      <p>{message.metadata.escalation_contact.name}</p>
                      <p>{message.metadata.escalation_contact.email}</p>
                      <p>{message.metadata.escalation_contact.phone}</p>
                    </div>
                  )}

                  {/* Quick suggestions */}
                  {!message.isUser && message.metadata?.suggestions && (
                    <div className="mt-3 space-y-2">
                      {message.metadata.suggestions.map((suggestion, idx) => (
                        <button
                          key={idx}
                          onClick={() => {
                            setInputValue(suggestion);
                            handleSend();
                          }}
                          className="block w-full text-left text-xs bg-white/10 hover:bg-white/20 rounded-lg px-3 py-2 transition-colors"
                        >
                          {suggestion}
                        </button>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            </motion.div>
          ))}
          <div ref={messagesEndRef} />
        </AnimatePresence>
      </div>

      {/* Input area */}
      <div className="p-3 bg-gray-50 border-t">
        <div className="flex items-center gap-2">
          <div className="flex-1 bg-white rounded-xl border shadow-sm text-black">
            <input
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyDown={handleKeyPress}
              placeholder="Type your message..."
              className="w-full px-3 py-2 rounded-xl focus:outline-none"
            />
          </div>
          <button
            onClick={handleSend}
            disabled={!inputValue.trim()}
            className="p-2 rounded-xl bg-blue-600 text-white hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
          >
            <Send className="h-5 w-5" />
          </button>
        </div>
      </div>
    </div>
  );
} 