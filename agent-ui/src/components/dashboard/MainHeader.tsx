import React from 'react';
import { useApp } from '../../context/AppContext';
import { Bell, HelpCircle } from 'lucide-react';

const MainHeader: React.FC = () => {
  const { user } = useApp();
  const firstName = user.name.split(' ')[0];

  return (
    <div className="border-b border-gray-200 px-6 py-4">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">
            Good morning, {firstName}!
          </h2>
          <p className="text-sm text-gray-500 mt-1">
            How can I assist you today?
          </p>
        </div>

        <div className="flex items-center gap-2">
          {/* Notification Bell */}
          <button className="relative p-2 hover:bg-gray-100 rounded-lg transition-colors">
            <Bell className="w-5 h-5 text-gray-600" />
            <span className="absolute top-1 right-1 w-5 h-5 bg-red-500 text-white text-xs rounded-full flex items-center justify-center font-semibold">
              3
            </span>
          </button>

          {/* Help */}
          <button className="p-2 hover:bg-gray-100 rounded-lg transition-colors">
            <HelpCircle className="w-5 h-5 text-gray-400" />
          </button>
        </div>
      </div>
    </div>
  );
};

export default MainHeader;
