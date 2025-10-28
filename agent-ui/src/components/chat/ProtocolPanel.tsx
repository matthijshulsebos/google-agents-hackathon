import React from 'react';
import { ProtocolData } from '../../types';
import { AlertTriangle } from 'lucide-react';

interface ProtocolPanelProps {
  data: ProtocolData;
}

const ProtocolPanel: React.FC<ProtocolPanelProps> = ({ data }) => {
  return (
    <div className="bg-gray-50 border border-gray-200 rounded-xl p-5 max-w-3xl">
      {/* Header */}
      <div className="flex items-center gap-2 mb-4">
        <AlertTriangle className="w-5 h-5 text-red-600" />
        <h3 className="text-base font-semibold text-gray-900">{data.title}</h3>
      </div>

      {/* Protocols */}
      <div className="space-y-3">
        {data.protocols.map((protocol) => (
          <div
            key={protocol.id}
            className={`${protocol.bgColor} border-l-4 ${protocol.borderColor} rounded-lg p-4`}
          >
            <h5 className="text-sm font-bold text-gray-900 mb-2">
              {protocol.title}
            </h5>
            <p className="text-xs text-gray-700 leading-relaxed">
              {protocol.description}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
};

export default ProtocolPanel;
