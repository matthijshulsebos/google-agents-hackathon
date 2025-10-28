import React from 'react';
import { quickReferences } from '../../data/mockData';
import { Thermometer, Calculator, Phone } from 'lucide-react';

const iconMap: Record<string, React.ElementType> = {
  Thermometer,
  Calculator,
  Phone,
};

const QuickReferences: React.FC = () => {
  return (
    <div>
      <h3 className="text-lg font-semibold text-gray-900 mb-3">Quick References</h3>
      <div className="space-y-2">
        {quickReferences.map((ref) => {
          const Icon = iconMap[ref.icon];
          return (
            <button
              key={ref.id}
              className="w-full flex items-center gap-3 p-3 hover:bg-gray-50 rounded-lg transition-colors text-left"
            >
              <div className={ref.iconColor}>
                <Icon className="w-5 h-5" />
              </div>
              <span className="text-sm font-medium text-gray-900">{ref.title}</span>
            </button>
          );
        })}
      </div>
    </div>
  );
};

export default QuickReferences;
