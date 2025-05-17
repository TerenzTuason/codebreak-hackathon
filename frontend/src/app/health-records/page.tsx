"use client";

import { useState, useEffect } from 'react';
import { User } from 'lucide-react';

interface HealthRecord {
  bloodType: string;
  allergies: string[];
  currentMedications: string[];
  pastSurgeries: string[];
  familyHistory: string[];
}

interface PredefinedHistory {
  date: string;
  visitType: string;
  notes: string;
}

interface UserData {
  name: string;
  healthRecords: HealthRecord;
  predefinedHistories: PredefinedHistory[];
}

export default function HealthRecords() {
  const [userData, setUserData] = useState<UserData | null>(null);

  useEffect(() => {
    const storedUser = localStorage.getItem('user');
    if (storedUser) {
      const user = JSON.parse(storedUser);
      setUserData(user);
    }
  }, []);

  if (!userData) {
    return (
      <div className="flex items-center justify-center min-h-[calc(100vh-4rem)]">
        <div className="text-gray-600">Loading health records...</div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="bg-white shadow-lg rounded-xl overflow-hidden">
        {/* Header */}
        <div className="px-6 py-4 border-b border-gray-200 bg-blue-600">
          <div className="flex items-center space-x-3">
            <User className="h-8 w-8 text-white" />
            <h1 className="text-2xl font-bold text-white">{userData.name}'s Health Records</h1>
          </div>
        </div>

        {/* Health Information */}
        <div className="p-6 grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="space-y-6">
            <div>
              <h2 className="text-xl font-semibold text-blue-600 mb-4">Basic Health Information</h2>
              <div className="bg-blue-50 p-4 rounded-xl border border-blue-100">
                <p className="mb-2"><span className="font-medium text-blue-700">Blood Type:</span> <span className="text-blue-600">{userData.healthRecords.bloodType}</span></p>
              </div>
            </div>

            <div>
              <h2 className="text-xl font-semibold text-blue-600 mb-4">Allergies</h2>
              <div className="bg-blue-50 p-4 rounded-xl border border-blue-100">
                <ul className="list-disc list-inside space-y-1">
                  {userData.healthRecords.allergies.map((allergy, index) => (
                    <li key={index} className="text-blue-600">{allergy}</li>
                  ))}
                </ul>
              </div>
            </div>

            <div>
              <h2 className="text-xl font-semibold text-blue-600 mb-4">Current Medications</h2>
              <div className="bg-blue-50 p-4 rounded-xl border border-blue-100">
                <ul className="list-disc list-inside space-y-1">
                  {userData.healthRecords.currentMedications.map((medication, index) => (
                    <li key={index} className="text-blue-600">{medication}</li>
                  ))}
                </ul>
              </div>
            </div>
          </div>

          <div className="space-y-6">
            <div>
              <h2 className="text-xl font-semibold text-blue-600 mb-4">Past Surgeries</h2>
              <div className="bg-blue-50 p-4 rounded-xl border border-blue-100">
                <ul className="list-disc list-inside space-y-1">
                  {userData.healthRecords.pastSurgeries.map((surgery, index) => (
                    <li key={index} className="text-blue-600">{surgery}</li>
                  ))}
                </ul>
              </div>
            </div>

            <div>
              <h2 className="text-xl font-semibold text-blue-600 mb-4">Family History</h2>
              <div className="bg-blue-50 p-4 rounded-xl border border-blue-100">
                <ul className="list-disc list-inside space-y-1">
                  {userData.healthRecords.familyHistory.map((condition, index) => (
                    <li key={index} className="text-blue-600">{condition}</li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        </div>

        {/* Medical History */}
        <div className="p-6 border-t border-gray-200 bg-gray-50">
          <h2 className="text-xl font-semibold text-blue-600 mb-4">Medical Visit History</h2>
          <div className="space-y-4">
            {userData.predefinedHistories.map((history, index) => (
              <div key={index} className="bg-white p-4 rounded-xl border border-blue-100 shadow-sm">
                <div className="flex justify-between items-start mb-2">
                  <h3 className="font-medium text-blue-600">{history.visitType}</h3>
                  <span className="text-sm text-blue-500">{history.date}</span>
                </div>
                <p className="text-gray-600">{history.notes}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
} 