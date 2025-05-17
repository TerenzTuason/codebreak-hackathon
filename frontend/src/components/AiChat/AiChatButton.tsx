'use client';

import { useState, useEffect, useRef } from 'react';
import { MessageCircle, X } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import AiChatWindow from './AiChatWindow';

export default function AiChatButton() {
  const [isOpen, setIsOpen] = useState(false);
  const [shouldSuggest, setShouldSuggest] = useState(false);
  const [suggestion, setSuggestion] = useState('');
  const [showWelcome, setShowWelcome] = useState(true);
  const idleTimer = useRef<NodeJS.Timeout>();
  const lastActivity = useRef<number>(Date.now());
  const welcomeMessages = [
    "Hi! What do you need?",
    "Need medical advice?",
    "Got health questions?",
    "Hi! How can I assist you?",
  ];
  const [currentWelcomeIndex, setCurrentWelcomeIndex] = useState(0);

  // Welcome message loop
  useEffect(() => {
    if (!isOpen) {
      const welcomeInterval = setInterval(() => {
        setShowWelcome(false);
        setTimeout(() => {
          setCurrentWelcomeIndex((prev) => (prev + 1) % welcomeMessages.length);
          setShowWelcome(true);
        }, 500);
      }, 5000); // Change message every 5 seconds

      return () => clearInterval(welcomeInterval);
    }
  }, [isOpen]);

  // Track user activity
  useEffect(() => {
    const updateLastActivity = () => {
      lastActivity.current = Date.now();
      setShouldSuggest(false);
      if (idleTimer.current) {
        clearTimeout(idleTimer.current);
      }
    };

    const events = ['mousemove', 'keydown', 'click', 'scroll'];
    events.forEach(event => {
      window.addEventListener(event, updateLastActivity);
    });

    // Check for idle time every 30 seconds
    const checkIdle = setInterval(() => {
      const idleTime = Date.now() - lastActivity.current;
      if (idleTime > 30000 && !isOpen) { // 30 seconds
        setShouldSuggest(true);
        // Set contextual suggestions based on current page or user history
        const suggestions = [
          "Need any help with your health concerns?",
          "I noticed you've been here a while. Can I assist you?",
          "Have questions about your symptoms?",
          `Good ${getTimeOfDay()}! How can I help you today?`
        ];
        setSuggestion(suggestions[Math.floor(Math.random() * suggestions.length)]);
      }
    }, 30000);

    return () => {
      events.forEach(event => {
        window.removeEventListener(event, updateLastActivity);
      });
      clearInterval(checkIdle);
      if (idleTimer.current) {
        clearTimeout(idleTimer.current);
      }
    };
  }, [isOpen]);

  const getTimeOfDay = () => {
    const hour = new Date().getHours();
    if (hour < 12) return 'morning';
    if (hour < 17) return 'afternoon';
    return 'evening';
  };

  // Hand wave animation variants
  const handWaveVariants = {
    wave: {
      rotate: [0, 14, -8, 14, -8, 14, 0],
      transition: {
        duration: 2.5,
        ease: "easeInOut",
        times: [0, 0.2, 0.4, 0.6, 0.8, 0.9, 1]
      }
    }
  };

  return (
    <div className="fixed bottom-0 sm:bottom-4 right-0 sm:right-4 z-50">
      <AnimatePresence>
        {!isOpen && showWelcome && (
          <motion.div
            initial={{ opacity: 0, y: 20, scale: 0.8 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 20, scale: 0.8 }}
            className="absolute bottom-[80px] right-4 p-4 bg-white rounded-lg shadow-lg w-[240px] sm:w-[280px]"
          >
            <div className="flex items-center gap-3">
              <motion.span
                variants={handWaveVariants}
                animate="wave"
                className="text-xl inline-block origin-bottom-right"
              >
                👋
              </motion.span>
              <p className="text-sm text-gray-700 flex-1">{welcomeMessages[currentWelcomeIndex]}</p>
            </div>
            <div className="absolute w-4 h-4 bg-white transform rotate-45 -bottom-2 right-6" />
          </motion.div>
        )}

        {shouldSuggest && !isOpen && !showWelcome && (
          <motion.div
            initial={{ opacity: 0, y: 20, scale: 0.8 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 20, scale: 0.8 }}
            className="absolute bottom-[80px] right-4 p-4 bg-white rounded-lg shadow-lg w-[240px] sm:w-[280px]"
          >
            <p className="text-sm text-gray-700">{suggestion}</p>
            <div className="absolute w-4 h-4 bg-white transform rotate-45 -bottom-2 right-6" />
          </motion.div>
        )}
      </AnimatePresence>

      {isOpen ? (
        <motion.div
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          exit={{ opacity: 0, scale: 0.8 }}
          className="relative sm:mb-4"
        >
          <AiChatWindow onClose={() => setIsOpen(false)} />
        </motion.div>
      ) : (
        <motion.button
          onClick={() => setIsOpen(true)}
          className="h-12 w-12 sm:h-14 sm:w-14 flex items-center justify-center rounded-full bg-blue-600 text-white shadow-lg hover:bg-blue-700 transition-all duration-200"
          whileHover={{ scale: 1.1 }}
          whileTap={{ scale: 0.9 }}
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{
            type: "spring",
            stiffness: 260,
            damping: 20
          }}
        >
          <MessageCircle className="h-6 w-6 sm:h-7 sm:w-7" />
          {(shouldSuggest || showWelcome) && (
            <motion.div
              className="absolute -top-1 -right-1 w-3 h-3 bg-red-500 rounded-full"
              animate={{
                scale: [1, 1.2, 1],
                opacity: [1, 0.8, 1]
              }}
              transition={{
                duration: 2,
                repeat: Infinity,
                ease: "easeInOut"
              }}
            />
          )}
        </motion.button>
      )}
    </div>
  );
} 