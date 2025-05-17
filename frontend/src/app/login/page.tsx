"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import Image from "next/image";
import { FaUser, FaLock } from "react-icons/fa";
import { IoMdHeartEmpty } from "react-icons/io";
import { RiStethoscopeLine, RiHospitalLine, RiPulseLine } from "react-icons/ri";
import { IconType } from 'react-icons';

interface BackgroundIconProps {
  icon: IconType;
  x: string;
  y: string;
}

const BackgroundIcon = ({ icon: Icon, x, y }: BackgroundIconProps) => (
  <motion.div
    className="absolute text-blue-400 text-3xl"
    animate={{ 
      opacity: [0.3, 0.7, 0.3],
      scale: [1, 1.1, 1]
    }}
    transition={{
      duration: 2,
      repeat: Infinity,
      ease: "easeInOut",
      times: [0, 0.5, 1]
    }}
    style={{
      left: x,
      top: y,
    }}
  >
    <Icon />
  </motion.div>
);

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // Handle login logic here
    console.log("Login attempt with:", { email, password });
  };

  // Create a grid of background icons
  const icons = [IoMdHeartEmpty, RiStethoscopeLine, RiHospitalLine, RiPulseLine];
  const backgroundIcons = [];
  
  // Create a 8x6 grid of icons with exact positioning
  for (let i = 0; i < 8; i++) {
    for (let j = 0; j < 6; j++) {
      backgroundIcons.push({
        id: i * 6 + j,
        icon: icons[(i * 6 + j) % icons.length],
        x: `${i * 12.5}%`,  // Removed random offset
        y: `${j * 16.6}%`   // Removed random offset
      });
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-sky-100 via-white to-sky-50 p-4 relative overflow-hidden">
      {/* Background Pattern */}
      <div className="fixed inset-0 pointer-events-none">
        {backgroundIcons.map((item) => (
          <BackgroundIcon
            key={item.id}
            icon={item.icon}
            x={item.x}
            y={item.y}
          />
        ))}
      </div>

      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, ease: "easeOut" }}
        className="w-full max-w-[900px] flex overflow-hidden bg-white rounded-3xl shadow-2xl relative z-10"
      >
        {/* Left Section */}
        <div className="w-[40%] bg-white p-8 flex flex-col justify-center items-center relative">
          <motion.div
            initial={{ scale: 0.8 }}
            animate={{ scale: 1 }}
            transition={{ duration: 0.5, delay: 0.2 }}
            className="text-center"
          >
            <Image
              src="/images/logo.png"
              alt="SympAI Logo"
              width={150}
              height={50}
              priority
              className="mb-6 mx-auto"
            />
            <h2 className="text-[#2563EB] text-2xl font-bold mb-4">
              Welcome to SympAI 
            </h2>
            <p className="text-gray-600 text-sm">
              Your trusted healthcare AI assistant
            </p>
          </motion.div>
        </div>

        {/* Right Section */}
        <div className="flex-1 bg-gradient-to-b from-[#2563EB] to-[#1E40AF] p-8 flex flex-col justify-center relative">
          {/* White gradient overlay */}
          <div className="absolute bottom-0 right-0 w-[70%] h-[70%] bg-gradient-radial from-white/10 to-transparent opacity-20"></div>
          
          <div className="w-full max-w-md mx-auto relative z-10">
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.5 }}
            >
              <h1 className="text-white text-2xl font-semibold mb-2">
                WELCOME BACK !
              </h1>
              <p className="text-white/80 mb-8">
                Enter your Username and Password to continue
              </p>

              <form onSubmit={handleSubmit} className="space-y-6">
                <div>
                  <div className="relative">
                    <input
                      type="email"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      className="w-full bg-white/10 rounded-lg px-4 py-3 pl-10 text-white border border-white/20 placeholder-white/60 focus:outline-none focus:ring-2 focus:ring-white/30 focus:border-transparent transition-all duration-200"
                      placeholder="Enter Username"
                      required
                    />
                    <FaUser className="absolute left-3 top-1/2 -translate-y-1/2 text-white/60" />
                  </div>
                </div>

                <div>
                  <div className="relative">
                    <input
                      type="password"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      className="w-full bg-white/10 rounded-lg px-4 py-3 pl-10 text-white border border-white/20 placeholder-white/60 focus:outline-none focus:ring-2 focus:ring-white/30 focus:border-transparent transition-all duration-200"
                      placeholder="Enter Password"
                      required
                    />
                    <FaLock className="absolute left-3 top-1/2 -translate-y-1/2 text-white/60" />
                  </div>
                </div>

                <div className="flex items-center">
                  <input
                    type="checkbox"
                    id="remember"
                    className="w-4 h-4 rounded border-white/20 bg-white/10 text-emerald-500 focus:ring-emerald-500 focus:ring-offset-0"
                  />
                  <label htmlFor="remember" className="ml-2 text-white/80 text-sm">
                    Remember me
                  </label>
                </div>
                <motion.button
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  type="submit"
                  className="w-full bg-emerald-500 text-white rounded-lg py-3 font-medium hover:bg-emerald-600 transition-colors duration-200 shadow-lg"
                >
                  Login
                </motion.button>
              </form>
            </motion.div>
          </div>

          {/* Pattern overlay */}
          <div className="absolute inset-0 opacity-10 pointer-events-none">
            <div className="absolute inset-0 pattern-medical"></div>
          </div>
        </div>
      </motion.div>

      <style jsx>{`
        .pattern-medical {
          background-image: repeating-linear-gradient(
            0deg,
            transparent,
            transparent 50px,
            rgba(255, 255, 255, 0.1) 50px,
            rgba(255, 255, 255, 0.1) 100px
          ),
          repeating-linear-gradient(
            90deg,
            transparent,
            transparent 50px,
            rgba(255, 255, 255, 0.1) 50px,
            rgba(255, 255, 255, 0.1) 100px
          );
        }
        .bg-gradient-radial {
          background: radial-gradient(circle at bottom right, var(--tw-gradient-from), var(--tw-gradient-to));
        }
      `}</style>
    </div>
  );
}