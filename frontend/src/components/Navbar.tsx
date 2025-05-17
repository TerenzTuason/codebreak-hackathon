"use client";

import { useState } from 'react';
import Link from 'next/link';
import { User, LogOut, Menu, X } from 'lucide-react';
import { useRouter } from 'next/navigation';

interface NavItem {
  label: string;
  href: string;
}

interface NavbarProps {
  activeTab: string;
  onTabChange: (tab: string) => void;
  username?: string;
}

const navItems: NavItem[] = [
  { label: 'Home', href: '/dashboard' },
  { label: 'Health Records', href: '/dashboard/health-records' },
  { label: 'Queries', href: '/dashboard/queries' },
];

export default function Navbar({ activeTab, onTabChange, username = 'User' }: NavbarProps) {
  const [isProfileOpen, setIsProfileOpen] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const router = useRouter();

  const handleNavClick = (label: string) => {
    onTabChange(label.toLowerCase());
    if (label.toLowerCase() === 'home') {
      window.location.href = '/dashboard';
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('user');
    router.push('/login');
  };

  return (
    <nav className="bg-blue-600 shadow-md sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex items-center">
            <Link href="/dashboard" className="flex items-center space-x-2 flex-shrink-0">
              <span className="text-xl font-bold text-white">SympAI</span>
            </Link>
          </div>

          <div className="hidden md:flex-1 md:flex md:items-center md:justify-center">
            <div className="flex space-x-8">
              {navItems.map((item) => (
                <button
                  key={item.label}
                  onClick={() => handleNavClick(item.label)}
                  className={`px-3 py-2 text-sm font-medium transition-colors duration-200 ${
                    activeTab === item.label.toLowerCase()
                      ? 'text-white border-b-2 border-white'
                      : 'text-blue-100 hover:text-white hover:border-b-2 hover:border-blue-100'
                  }`}
                >
                  {item.label}
                </button>
              ))}
            </div>
          </div>
          
          <div className="relative">
            <button 
              className="flex items-center space-x-3 text-white hover:text-blue-100 transition-colors duration-200"
              onClick={() => setIsProfileOpen(!isProfileOpen)}
            >
              <User className="h-6 w-6" />
              <span className="hidden md:block text-sm">
                {username}
              </span>
            </button>
            
            {isProfileOpen && (
              <div className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg py-2 border border-gray-100">
                <div className="px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 cursor-pointer flex items-center">
                  <User className="h-4 w-4 mr-2" />
                  Profile
                </div>
                <div 
                  className="px-4 py-2 text-sm text-red-600 hover:bg-gray-100 cursor-pointer flex items-center"
                  onClick={handleLogout}
                >
                  <LogOut className="h-4 w-4 mr-2" />
                  Logout
                </div>
              </div>
            )}
          </div>

          <button
            className="md:hidden text-white hover:text-blue-100 transition-colors duration-200"
            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
          >
            {isMobileMenuOpen ? (
              <X className="h-6 w-6" />
            ) : (
              <Menu className="h-6 w-6" />
            )}
          </button>
        </div>

        {isMobileMenuOpen && (
          <div className="md:hidden">
            <div className="px-2 pt-2 pb-3 space-y-1">
              {navItems.map((item) => (
                <button
                  key={item.label}
                  onClick={() => {
                    handleNavClick(item.label);
                    setIsMobileMenuOpen(false);
                  }}
                  className={`block w-full text-left px-3 py-2 rounded-md text-base font-medium transition-colors duration-200 ${
                    activeTab === item.label.toLowerCase()
                      ? 'text-white bg-blue-700'
                      : 'text-blue-100 hover:text-white hover:bg-blue-700'
                  }`}
                >
                  {item.label}
                </button>
              ))}
            </div>
          </div>
        )}
      </div>
    </nav>
  );
} 