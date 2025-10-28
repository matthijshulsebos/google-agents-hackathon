import React from 'react';
import { ScheduleData } from '../../types';
import { Clock, Activity, Baby } from 'lucide-react';

const iconMap: Record<string, React.ElementType> = {
  Clock,
  Activity,
  Baby,
};

interface SchedulePanelProps {
  data: ScheduleData;
}

const SchedulePanel: React.FC<SchedulePanelProps> = ({ data }) => {
  return (
    <div className="bg-gray-50 border border-gray-200 rounded-xl p-5 max-w-3xl">
      {/* Header */}
      <h3 className="text-base font-semibold text-gray-900 mb-4">
        Today's Nursery Schedule - {data.date}
      </h3>

      {/* Shift Details */}
      <div className="grid grid-cols-3 gap-4 mb-5">
        <div>
          <p className="text-xs text-gray-500 mb-1">Shift:</p>
          <p className="text-sm font-semibold text-primary">{data.shiftTime}</p>
          <p className="text-xs text-gray-600">{data.shiftDuration}</p>
        </div>
        <div>
          <p className="text-xs text-gray-500 mb-1">Assigned Unit:</p>
          <p className="text-sm font-semibold text-primary">{data.assignedUnit}</p>
          <p className="text-xs text-gray-600">{data.unitDescription}</p>
        </div>
        <div>
          <p className="text-xs text-gray-500 mb-1">Patients:</p>
          <p className="text-sm font-semibold text-primary">{data.patients.total} infants</p>
          <p className="text-xs text-gray-600">
            {data.patients.critical} critical, {data.patients.stable} stable
          </p>
        </div>
      </div>

      {/* Key Procedures */}
      <div>
        <h4 className="text-sm font-semibold text-gray-900 mb-3">
          Key Nursery Procedures Today:
        </h4>
        <div className="space-y-3">
          {data.procedures.map((procedure) => {
            const Icon = iconMap[procedure.icon];
            return (
              <div
                key={procedure.id}
                className={`${procedure.bgColor} border border-gray-200 rounded-lg p-3 flex items-start gap-3`}
              >
                <div className={procedure.color}>
                  <Icon className="w-5 h-5" />
                </div>
                <div className="flex-1">
                  <h5 className={`text-sm font-semibold ${procedure.color} mb-1`}>
                    {procedure.title}
                  </h5>
                  <p className="text-xs text-gray-700">{procedure.description}</p>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};

export default SchedulePanel;
