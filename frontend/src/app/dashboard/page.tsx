"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { FaUser, FaClock, FaEnvelope, FaPhone, FaMapMarkerAlt } from "react-icons/fa";
import { useRouter } from "next/navigation";
import { AiChatButton } from "@/components/AiChat";

interface ChatItemProps {
  query: string;
  timestamp: string;
  response: string;
}

interface UserInfo {
  name: string;
  email: string;
  phone: string;
  location: string;
  username: string;
}

interface InfoItemProps {
  icon: React.ReactNode;
  label: string;
  value: string;
}

const ChatItem = ({ query, timestamp, response }: ChatItemProps) => (
  <motion.div
    initial={{ opacity: 0, y: 10 }}
    animate={{ opacity: 1, y: 0 }}
    className="bg-white rounded-lg shadow-sm p-4 mb-4 w-full"
  >
    <div className="flex items-center justify-between mb-2">
      <span className="text-sm text-gray-500 flex items-center">
        <FaClock className="mr-2" /> {timestamp}
      </span>
    </div>
    <p className="text-gray-800 font-medium mb-2 break-words">{query}</p>
    <p className="text-gray-600 text-sm bg-gray-50 p-3 rounded break-words">{response}</p>
  </motion.div>
);

const InfoItem = ({ icon, label, value }: InfoItemProps) => (
  <div className="flex items-center space-x-3">
    {icon}
    <div>
      <p className="text-sm text-gray-500">{label}</p>
      <p className="text-gray-800">{value}</p>
    </div>
  </div>
);

export default function DashboardPage() {
  const [userInfo, setUserInfo] = useState<UserInfo | null>(null);
  const router = useRouter();

  useEffect(() => {
    // Check if user is logged in
    const userDataStr = localStorage.getItem('user');
    if (!userDataStr) {
      router.push('/login');
      return;
    }

    const userData = JSON.parse(userDataStr);
    setUserInfo(userData);
  }, [router]);

  // Mock recent chats
  const recentChats = [
    {
      query: "What are the symptoms of seasonal allergies?",
      timestamp: "2 hours ago",
      response: "Common symptoms include sneezing, runny nose, itchy eyes, and congestion. These typically occur during specific seasons when certain pollens are present."
    },
    {
      query: "How to treat mild dehydration?",
      timestamp: "5 hours ago",
      response: "Recommend oral rehydration with water and electrolytes. Monitor fluid intake and symptoms. If severe symptoms develop, seek immediate medical attention."
    },
    {
      query: "What's the recommended dosage for ibuprofen?",
      timestamp: "Yesterday",
      response: "For adults, the standard dosage is 200-400mg every 4-6 hours. Do not exceed 1200mg in 24 hours without consulting a healthcare provider."
    }
  ];

  if (!userInfo) {
    return null; // or a loading spinner
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-sky-50 via-white to-sky-50">
      <main className="container mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-8">
        <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
          {/* Personal Information */}
          <div className="bg-white rounded-xl shadow-lg p-4 sm:p-6 order-2 xl:order-1">
            <h2 className="text-xl font-semibold text-gray-800 mb-4 sm:mb-6">Personal Information</h2>
            <div className="grid gap-4">
              <InfoItem
                icon={<FaUser className="w-5 h-5 text-blue-500 flex-shrink-0" />}
                label="Name"
                value={userInfo.name}
              />
              <InfoItem
                icon={<FaEnvelope className="w-5 h-5 text-blue-500 flex-shrink-0" />}
                label="Email"
                value={userInfo.email}
              />
              <InfoItem
                icon={<FaPhone className="w-5 h-5 text-blue-500 flex-shrink-0" />}
                label="Phone"
                value={userInfo.phone}
              />
              <InfoItem
                icon={<FaMapMarkerAlt className="w-5 h-5 text-blue-500 flex-shrink-0" />}
                label="Location"
                value={userInfo.location}
              />
            </div>
          </div>

          {/* Recent Queries */}
          <div className="xl:col-span-2 bg-white rounded-xl shadow-lg p-4 sm:p-6 order-1 xl:order-2">
            <h2 className="text-xl font-semibold text-gray-800 mb-4 sm:mb-6">Recent Queries</h2>
            <div className="space-y-4">
              {recentChats.map((chat, index) => (
                <ChatItem
                  key={index}
                  query={chat.query}
                  timestamp={chat.timestamp}
                  response={chat.response}
                />
              ))}
            </div>
          </div>
        </div>
      </main>

      {/* AI Chat Button */}
      <AiChatButton />
    </div>
  );
} 