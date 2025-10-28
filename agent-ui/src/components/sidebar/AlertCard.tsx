import React from 'react';
import { Alert } from '../../types';
import { AlertCircle } from 'lucide-react';

interface AlertCardProps {
  alert: Alert;
}

const AlertCard: React.FC<AlertCardProps> = ({ alert }) => {
  const severityStyles = {
    critical: {
      bg: 'bg-critical-bg',
      text: 'text-critical-text',
      icon: 'text-critical-text',
    },
    warning: {
      bg: 'bg-warning-bg',
      text: 'text-warning-text',
      icon: 'text-warning-text',
    },
    info: {
      bg: 'bg-info-bg',
      text: 'text-info-text',
      icon: 'text-info-text',
    },
  };

  const styles = severityStyles[alert.severity];

  return (
    <div className={`${styles.bg} rounded-lg p-4 border border-gray-200`}>
      <div className="flex items-start gap-3">
        <div className={styles.icon}>
          <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
        </div>
        <div className="flex-1 min-w-0">
          <h4 className={`text-sm font-semibold ${styles.text} mb-1`}>
            {alert.title}
          </h4>
          <p className="text-xs text-gray-700">{alert.description}</p>
        </div>
      </div>
    </div>
  );
};

export default AlertCard;
