import React from 'react';
import LeftSidebar from './LeftSidebar';
import MainContent from './MainContent';
import RightSidebar from './RightSidebar';

const DashboardLayout: React.FC = () => {
  return (
    <div className="flex h-screen bg-gray-50 overflow-hidden">
      {/* Left Sidebar */}
      <div className="w-64 flex-shrink-0">
        <LeftSidebar />
      </div>

      {/* Main Content */}
      <div className="flex-1 overflow-hidden">
        <MainContent />
      </div>

      {/* Right Sidebar */}
      <div className="w-80 flex-shrink-0">
        <RightSidebar />
      </div>
    </div>
  );
};

export default DashboardLayout;
