'use client';

import React, { useState, useRef, useEffect } from 'react';
import { Send, X, Maximize2, Mic, Camera, Image as ImageIcon } from 'lucide-react';
import Image from 'next/image';
import Link from 'next/link';
import { motion, AnimatePresence } from 'framer-motion';
import { useLoading } from '@/context/LoadingContext';
import { usePathname } from 'next/navigation';

interface AiChatWindowProps {
  onClose: () => void;
}

interface QuickAction {
  text: string;
  icon?: string;
  type?: 'default' | 'voice' | 'image';
}

interface Message {
  text: string;
  isUser: boolean;
  type?: 'text' | 'voice' | 'image';
  metadata?: {
    imageUrl?: string;
    audioUrl?: string;
    suggestions?: string[];
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
  const [isRecording, setIsRecording] = useState(false);
  const [showImageUpload, setShowImageUpload] = useState(false);
  const { setIsLoading } = useLoading();
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (!inputValue.trim()) return;
    
    // Add user message
    setMessages((prev: Message[]) => [...prev, { text: inputValue, isUser: true }]);
    setInputValue('');
    
    setIsLoading(true);
    
    try {
      // Call the AI prediction endpoint
      const response = await fetch('http://127.0.0.1:5000/predict', {
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
      let newMessage: Message = {
        text: data.tier === 0 ? data.message : data.suggested_response,
        isUser: false,
        metadata: {
          suggestions: []
        }
      };

      // Add suggestions based on confidence level
      if (data.tier === 1) {
        newMessage.metadata!.suggestions = [
          "Could you provide more details?",
          "Let me connect you with a human agent",
          "Would you like to rephrase your question?"
        ];
      }

      setMessages((prev: Message[]) => [...prev, newMessage]);
    } catch (error) {
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

  const handleVoiceInput = () => {
    if (!isRecording) {
      setIsRecording(true);
      // Start recording logic here
      // For demo, we'll simulate a recording
      setTimeout(() => {
        setIsRecording(false);
        setMessages(prev => [...prev, {
          text: "Voice message recorded",
          isUser: true,
          type: 'voice',
          metadata: {
            audioUrl: '/demo-audio.mp3'
          }
        }]);
      }, 2000);
    } else {
      setIsRecording(false);
      // Stop recording logic here
    }
  };

  const handleImageUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => {
        setMessages(prev => [...prev, {
          text: "Image uploaded",
          isUser: true,
          type: 'image',
          metadata: {
            imageUrl: reader.result as string
          }
        }]);
      };
      reader.readAsDataURL(file);
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
              <motion.div
                whileHover={{ scale: 1.02 }}
                className={`max-w-[85%] rounded-[14px] sm:rounded-[16px] p-2.5 sm:p-3 shadow-sm ${
                  message.isUser
                    ? 'bg-gradient-to-br from-blue-500 to-blue-600 text-white'
                    : 'bg-gray-100 text-gray-800'
                }`}
              >
                {message.type === 'image' && message.metadata?.imageUrl && (
                  <div className="mb-2">
                    <Image
                      src={message.metadata.imageUrl}
                      alt="Uploaded"
                      width={160}
                      height={160}
                      className="rounded-lg"
                    />
                  </div>
                )}
                {message.type === 'voice' && message.metadata?.audioUrl && (
                  <div className="mb-2">
                    <audio controls src={message.metadata.audioUrl} className="w-full" />
                  </div>
                )}
                <p className="text-xs sm:text-sm whitespace-pre-wrap">{message.text}</p>
                {message.metadata?.suggestions && (
                  <div className="mt-2 space-y-1.5">
                    {message.metadata.suggestions.map((suggestion, idx) => (
                      <button
                        key={idx}
                        onClick={() => {
                          setInputValue(suggestion);
                          setMessages(prev => [...prev, { text: suggestion, isUser: true }]);
                        }}
                        className={`w-full text-left px-2.5 py-1.5 rounded-lg text-xs sm:text-sm ${
                          message.isUser
                            ? 'bg-white/10 hover:bg-white/20'
                            : 'bg-white hover:bg-gray-50'
                        } transition-all duration-200`}
                      >
                        {suggestion}
                      </button>
                    ))}
                  </div>
                )}
              </motion.div>
            </motion.div>
          ))}
        </AnimatePresence>
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <motion.div
        initial={{ y: 20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        className="p-3 border-t border-gray-100"
      >
        <div className="flex items-center gap-1.5 bg-white rounded-xl p-1 shadow-sm ring-1 ring-gray-100">
          <button
            onClick={handleVoiceInput}
            className={`p-1.5 rounded-lg transition-all ${
              isRecording ? 'bg-red-500 text-white' : 'text-gray-500 hover:bg-gray-100'
            }`}
          >
            <Mic className="h-4 w-4" />
          </button>
          <button
            onClick={() => fileInputRef.current?.click()}
            className="p-1.5 rounded-lg text-gray-500 hover:bg-gray-100 transition-all"
          >
            <Camera className="h-4 w-4" />
          </button>
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleImageUpload}
            accept="image/*"
            className="hidden"
          />
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyDown={handleKeyPress}
            placeholder="Type your message..."
            className="flex-1 bg-transparent px-2 focus:outline-none text-xs sm:text-sm text-black"
          />
          <motion.button
            whileTap={{ scale: 0.95 }}
            onClick={handleSend}
            disabled={!inputValue.trim()}
            className="p-1.5 rounded-lg bg-gradient-to-r from-blue-500 to-blue-600 text-white hover:from-blue-600 hover:to-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200"
          >
            <Send className="h-3.5 w-3.5 sm:h-4 sm:w-4" />
          </motion.button>
        </div>
        <div className="text-[8px] sm:text-[10px] text-gray-400 text-right mt-1.5">
          Powered by SympAI
        </div>
      </motion.div>
    </div>
  );
} 