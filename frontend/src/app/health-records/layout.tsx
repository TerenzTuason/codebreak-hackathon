"use client";

import { useState, useEffect } from 'react';
import Navbar from '@/components/Navbar';

export default function HealthRecordsLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const [activeTab, setActiveTab] = useState('health records');
  const [username, setUsername] = useState('User');

  useEffect(() => {
    // Get username from localStorage
    const storedUser = localStorage.getItem('user');
    if (storedUser) {
      const user = JSON.parse(storedUser);
      setUsername(user.name || 'User');
    }
  }, []);

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar
        activeTab={activeTab}
        onTabChange={setActiveTab}
        username={username}
      />
      <main className="min-h-[calc(100vh-4rem)]">
        {children}
      </main>
    </div>
  );
} 