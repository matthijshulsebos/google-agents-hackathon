import React from 'react';
import MainHeader from '../dashboard/MainHeader';
import QuickActionsGrid from '../dashboard/QuickActionsGrid';
import InteractiveDisplay from '../dashboard/InteractiveDisplay';
import ChatInput from '../chat/ChatInput';

const MainContent: React.FC = () => {
  return (
    <div className="h-full flex flex-col bg-white">
      {/* Header */}
      <MainHeader />

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-6 space-y-6">
        {/* Quick Actions */}
        <QuickActionsGrid />

        {/* Chat/Interactive Display */}
        <InteractiveDisplay />
      </div>

      {/* Chat Input */}
      <ChatInput />
    </div>
  );
};

export default MainContent;
