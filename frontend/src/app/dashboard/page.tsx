"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import Image from "next/image";
import { FaUser, FaCalendar, FaClipboardList, FaComments } from "react-icons/fa";
import Navbar from "@/components/Navbar";
import { AiChatButton } from "@/components/AiChat";

interface DashboardCardProps {
  title: string;
  value: string | number;
  icon: React.ReactNode;
  color: string;
}

const DashboardCard = ({ title, value, icon, color }: DashboardCardProps) => (
  <motion.div
    whileHover={{ scale: 1.02 }}
    className={`bg-white p-6 rounded-xl shadow-lg ${color} relative overflow-hidden`}
  >
    <div className="flex justify-between items-start">
      <div>
        <p className="text-gray-600 text-sm mb-1">{title}</p>
        <h3 className="text-2xl font-bold text-gray-800">{value}</h3>
      </div>
      <div className="text-2xl opacity-80">{icon}</div>
    </div>
    <div className="absolute bottom-0 right-0 w-32 h-32 bg-current opacity-5 rounded-full -mr-16 -mb-16"></div>
  </motion.div>
);

interface TaskItemProps {
  title: string;
  time: string;
  status: "pending" | "completed";
}

const TaskItem = ({ title, time, status }: TaskItemProps) => (
  <motion.div
    initial={{ opacity: 0, y: 10 }}
    animate={{ opacity: 1, y: 0 }}
    className="flex items-center justify-between p-3 bg-white rounded-lg shadow-sm mb-2"
  >
    <div className="flex items-center">
      <div className={`w-2 h-2 rounded-full ${status === "pending" ? "bg-yellow-400" : "bg-green-400"} mr-3`}></div>
      <span className="text-gray-800">{title}</span>
    </div>
    <span className="text-gray-500 text-sm">{time}</span>
  </motion.div>
);

export default function DashboardPage() {
  const [activeTab, setActiveTab] = useState("overview");

  return (
    <div className="min-h-screen bg-gradient-to-br from-sky-50 via-white to-sky-50">
      <Navbar activeTab={activeTab} onTabChange={setActiveTab} />

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <DashboardCard
            title="Total Patients"
            value="1,234"
            icon={<FaUser />}
            color="text-blue-500"
          />
          <DashboardCard
            title="Appointments Today"
            value="28"
            icon={<FaCalendar />}
            color="text-green-500"
          />
          <DashboardCard
            title="Pending Tasks"
            value="12"
            icon={<FaClipboardList />}
            color="text-yellow-500"
          />
          <DashboardCard
            title="Active Chats"
            value="5"
            icon={<FaComments />}
            color="text-purple-500"
          />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Recent Activity */}
          <div className="lg:col-span-2 bg-white rounded-xl shadow-lg p-6">
            <h2 className="text-xl font-semibold text-gray-800 mb-4">Recent Activity</h2>
            <div className="space-y-4">
              <TaskItem
                title="Review lab results for Patient #12345"
                time="10:30 AM"
                status="pending"
              />
              <TaskItem
                title="Schedule follow-up appointment"
                time="11:00 AM"
                status="completed"
              />
              <TaskItem
                title="Update patient records"
                time="2:15 PM"
                status="pending"
              />
              <TaskItem
                title="Send medication reminder"
                time="3:00 PM"
                status="completed"
              />
            </div>
          </div>

          {/* Quick Actions */}
          <div className="bg-white rounded-xl shadow-lg p-6">
            <h2 className="text-xl font-semibold text-gray-800 mb-4">Quick Actions</h2>
            <div className="space-y-3">
              <motion.button
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                className="w-full bg-blue-500 text-white rounded-lg py-3 font-medium hover:bg-blue-600 transition-colors duration-200 flex items-center justify-center space-x-2"
              >
                <FaComments className="w-5 h-5" />
                <span>Start New Chat</span>
              </motion.button>
              <motion.button
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                className="w-full bg-green-500 text-white rounded-lg py-3 font-medium hover:bg-green-600 transition-colors duration-200 flex items-center justify-center space-x-2"
              >
                <FaCalendar className="w-5 h-5" />
                <span>Schedule Appointment</span>
              </motion.button>
              <motion.button
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                className="w-full bg-purple-500 text-white rounded-lg py-3 font-medium hover:bg-purple-600 transition-colors duration-200 flex items-center justify-center space-x-2"
              >
                <FaClipboardList className="w-5 h-5" />
                <span>Create Task</span>
              </motion.button>
            </div>
          </div>
        </div>
      </main>

      {/* AI Chat Button */}
      <AiChatButton />
    </div>
  );
} 