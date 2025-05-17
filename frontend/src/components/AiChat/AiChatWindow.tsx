'use client';

import { useState, useRef, useEffect } from 'react';
import { Send, X, Maximize2, Mic, Camera, Image as ImageIcon } from 'lucide-react';
import Image from 'next/image';
import Link from 'next/link';
import { motion, AnimatePresence } from 'framer-motion';
import { useLoading } from '@/context/LoadingContext';

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
  const [messages, setMessages] = useState<Message[]>([
    { 
      text: "Hi 👋 How can I help you?", 
      isUser: false,
      metadata: {
        suggestions: [
          "I have a headache",
          "Check my symptoms",
          "Medical advice needed"
        ]
      }
    }
  ]);
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

  const handleSend = () => {
    if (!inputValue.trim()) return;
    
    setMessages(prev => [...prev, { text: inputValue, isUser: true }]);
    setInputValue('');
    
    setIsLoading(true);
    
    // Simulate AI response with smart suggestions
    setTimeout(() => {
      const newMessage: Message = {
        text: "I understand you're not feeling well. Let me help you better understand your symptoms.",
        isUser: false,
        metadata: {
          suggestions: [
            "Tell me more about when it started",
            "Rate your pain from 1-10",
            "Any other symptoms?"
          ]
        }
      };
      setMessages(prev => [...prev, newMessage]);
      setIsLoading(false);
    }, 1000);
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
    <div className="fixed bottom-0 right-0 sm:relative w-full sm:w-[400px] md:w-[500px] h-[100dvh] sm:h-[600px] bg-white sm:rounded-[24px] shadow-2xl flex flex-col overflow-hidden">
      {/* Header */}
      <motion.div 
        initial={{ y: -20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        className="bg-gradient-to-r from-blue-600 to-blue-500 p-3 sm:p-4 text-white"
      >
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
              <motion.div 
                className="absolute bottom-0 right-0 w-2.5 h-2.5 sm:w-3 sm:h-3 bg-green-400 rounded-full ring-2 ring-white"
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
      </motion.div>

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
              <motion.div
                whileHover={{ scale: 1.02 }}
                className={`max-w-[85%] sm:max-w-[80%] rounded-[16px] sm:rounded-[20px] p-3 sm:p-3.5 shadow-sm ${
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
                      width={200}
                      height={200}
                      className="rounded-lg"
                    />
                  </div>
                )}
                {message.type === 'voice' && message.metadata?.audioUrl && (
                  <div className="mb-2">
                    <audio controls src={message.metadata.audioUrl} className="w-full" />
                  </div>
                )}
                <p className="text-sm sm:text-base whitespace-pre-wrap">{message.text}</p>
                {message.metadata?.suggestions && (
                  <div className="mt-3 space-y-2">
                    {message.metadata.suggestions.map((suggestion, idx) => (
                      <button
                        key={idx}
                        onClick={() => {
                          setInputValue(suggestion);
                          setMessages(prev => [...prev, { text: suggestion, isUser: true }]);
                        }}
                        className={`w-full text-left px-3 py-2 rounded-lg text-sm ${
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
        className="p-4 border-t border-gray-100"
      >
        <div className="flex items-center gap-2 bg-white rounded-xl sm:rounded-2xl p-1.5 shadow-sm ring-1 ring-gray-100">
          <button
            onClick={handleVoiceInput}
            className={`p-2 rounded-lg transition-all ${
              isRecording ? 'bg-red-500 text-white' : 'text-gray-500 hover:bg-gray-100'
            }`}
          >
            <Mic className="h-5 w-5" />
          </button>
          <button
            onClick={() => fileInputRef.current?.click()}
            className="p-2 rounded-lg text-gray-500 hover:bg-gray-100 transition-all"
          >
            <Camera className="h-5 w-5" />
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
            className="flex-1 bg-transparent px-2 sm:px-3 focus:outline-none text-sm"
          />
          <motion.button
            whileTap={{ scale: 0.95 }}
            onClick={handleSend}
            disabled={!inputValue.trim()}
            className="p-1.5 sm:p-2 rounded-lg sm:rounded-xl bg-gradient-to-r from-blue-500 to-blue-600 text-white hover:from-blue-600 hover:to-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200"
          >
            <Send className="h-4 w-4 sm:h-5 sm:w-5" />
          </motion.button>
        </div>
        <div className="text-[10px] text-gray-400 text-right mt-2">
          Powered by SympAI
        </div>
      </motion.div>
    </div>
  );
} 