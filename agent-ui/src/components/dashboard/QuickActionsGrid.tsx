import React from 'react';
import QuickActionCard from './QuickActionCard';
import { quickActions } from '../../data/mockData';

const QuickActionsGrid: React.FC = () => {
  return (
    <div>
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h3>
      <div className="grid grid-cols-5 gap-4">
        {quickActions.map((action) => (
          <QuickActionCard key={action.id} action={action} />
        ))}
      </div>
    </div>
  );
};

export default QuickActionsGrid;
