"use client";

import { useState } from 'react';
import Image from 'next/image';
import Link from 'next/link';
import { FaBell } from 'react-icons/fa';

interface NavItem {
  label: string;
  href: string;
}

interface NavbarProps {
  activeTab: string;
  onTabChange: (tab: string) => void;
}

const navItems: NavItem[] = [
  { label: 'Overview', href: '/dashboard' },
  { label: 'Patients', href: '/dashboard/patients' },
  { label: 'Tasks', href: '/dashboard/tasks' },
];

export default function Navbar({ activeTab, onTabChange }: NavbarProps) {
  const [isNotificationsOpen, setIsNotificationsOpen] = useState(false);

  return (
    <nav className="bg-white shadow-md sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex items-center">
            <Link href="/dashboard" className="flex items-center space-x-2 flex-shrink-0">
              <Image
                src="/images/icon.png"
                alt="SympAI Icon"
                width={40}
                height={40}
                className="object-contain"
                priority
              />
              <span className="text-xl font-bold text-gray-900">SympAI</span>
            </Link>
            <div className="hidden md:flex space-x-8 ml-8">
              {navItems.map((item) => (
                <button
                  key={item.label}
                  onClick={() => onTabChange(item.label.toLowerCase())}
                  className={`px-3 py-2 text-sm font-medium transition-colors duration-200 ${
                    activeTab === item.label.toLowerCase()
                      ? 'text-blue-600 border-b-2 border-blue-600'
                      : 'text-gray-500 hover:text-gray-700 hover:border-b-2 hover:border-gray-300'
                  }`}
                >
                  {item.label}
                </button>
              ))}
            </div>
          </div>
          
          <div className="flex items-center space-x-4">
            <div className="relative">
              <button 
                className="text-gray-400 hover:text-gray-500 transition-colors duration-200"
                onClick={() => setIsNotificationsOpen(!isNotificationsOpen)}
              >
                <FaBell className="h-6 w-6" />
                <span className="absolute -top-1 -right-1 h-4 w-4 bg-red-500 rounded-full flex items-center justify-center">
                  <span className="text-white text-xs">3</span>
                </span>
              </button>
              
              {isNotificationsOpen && (
                <div className="absolute right-0 mt-2 w-80 bg-white rounded-lg shadow-lg py-2 border border-gray-100">
                  <div className="px-4 py-2 border-b border-gray-100">
                    <h3 className="text-sm font-semibold text-gray-800">Notifications</h3>
                  </div>
                  <div className="max-h-96 overflow-y-auto">
                    {/* Notification Items */}
                    <div className="px-4 py-3 hover:bg-gray-50 cursor-pointer">
                      <p className="text-sm text-gray-800">New patient appointment request</p>
                      <p className="text-xs text-gray-500 mt-1">5 minutes ago</p>
                    </div>
                    <div className="px-4 py-3 hover:bg-gray-50 cursor-pointer">
                      <p className="text-sm text-gray-800">Lab results available for Patient #12345</p>
                      <p className="text-xs text-gray-500 mt-1">1 hour ago</p>
                    </div>
                    <div className="px-4 py-3 hover:bg-gray-50 cursor-pointer">
                      <p className="text-sm text-gray-800">Medication reminder sent successfully</p>
                      <p className="text-xs text-gray-500 mt-1">2 hours ago</p>
                    </div>
                  </div>
                </div>
              )}
            </div>
            
            <div className="flex items-center">
              <button className="flex items-center space-x-3 group">
                <Image
                  src="/images/avatar-placeholder.png"
                  alt="User avatar"
                  width={32}
                  height={32}
                  className="rounded-full ring-2 ring-gray-200 group-hover:ring-blue-400 transition-all duration-200"
                />
                <span className="hidden md:block text-sm text-gray-700 group-hover:text-blue-600 transition-colors duration-200">
                  Dr. Smith
                </span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </nav>
  );
} 