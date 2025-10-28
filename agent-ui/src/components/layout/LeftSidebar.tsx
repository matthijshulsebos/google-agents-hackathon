import React from 'react';
import NavMenu from '../navigation/NavMenu';
import UserProfileCard from '../navigation/UserProfileCard';
import { Bot } from 'lucide-react';

const LeftSidebar: React.FC = () => {
  return (
    <div className="h-full bg-white border-r border-gray-200 flex flex-col">
      {/* Header */}
      <div className="p-6 border-b border-gray-200">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-primary rounded-lg flex items-center justify-center">
            <Bot className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="text-lg font-bold text-gray-900">MedAssist</h1>
            <p className="text-xs text-gray-500">Nursing Assistant</p>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <div className="flex-1 overflow-y-auto py-4">
        <NavMenu />
      </div>

      {/* User Profile */}
      <div className="border-t border-gray-200">
        <UserProfileCard />
      </div>
    </div>
  );
};

export default LeftSidebar;
