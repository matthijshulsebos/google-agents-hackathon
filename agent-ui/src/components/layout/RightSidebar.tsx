import React from 'react';
import AlertsList from '../sidebar/AlertsList';
import UpcomingSchedule from '../sidebar/UpcomingSchedule';
import QuickReferences from '../sidebar/QuickReferences';

const RightSidebar: React.FC = () => {
  return (
    <div className="h-full bg-white border-l border-gray-200 overflow-y-auto">
      <div className="p-6 space-y-6">
        {/* Active Alerts */}
        <AlertsList />

        {/* Today's Schedule */}
        <UpcomingSchedule />

        {/* Quick References */}
        <QuickReferences />
      </div>
    </div>
  );
};

export default RightSidebar;
