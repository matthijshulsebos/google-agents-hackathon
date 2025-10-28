import React from 'react';
import { useApp } from '../../context/AppContext';
import AlertCard from './AlertCard';

const AlertsList: React.FC = () => {
  const { alerts } = useApp();

  return (
    <div>
      <h3 className="text-lg font-semibold text-gray-900 mb-3">Active Alerts</h3>
      <div className="space-y-3">
        {alerts.map((alert) => (
          <AlertCard key={alert.id} alert={alert} />
        ))}
      </div>
    </div>
  );
};

export default AlertsList;
