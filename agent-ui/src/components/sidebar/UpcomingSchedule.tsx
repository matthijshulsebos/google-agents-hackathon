import React from 'react';
import { useApp } from '../../context/AppContext';
import { Milk, Heart, ArrowRightLeft } from 'lucide-react';

const iconMap: Record<string, React.ElementType> = {
  Milk,
  Heart,
  ArrowRightLeft,
};

const UpcomingSchedule: React.FC = () => {
  const { schedule } = useApp();

  return (
    <div>
      <h3 className="text-lg font-semibold text-gray-900 mb-3">Today's Schedule</h3>
      <div className="space-y-3">
        {schedule.map((item) => {
          const Icon = iconMap[item.icon];
          return (
            <div key={item.id} className="flex items-start gap-3">
              <div className={item.iconColor}>
                <Icon className="w-5 h-5" />
              </div>
              <div className="flex-1">
                <div className="flex items-baseline justify-between">
                  <h4 className="text-sm font-semibold text-gray-900">
                    {item.title}
                  </h4>
                  <span className={`text-xs font-medium ${item.iconColor}`}>
                    {item.time}
                  </span>
                </div>
                <p className="text-xs text-gray-500 mt-0.5">{item.description}</p>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default UpcomingSchedule;
