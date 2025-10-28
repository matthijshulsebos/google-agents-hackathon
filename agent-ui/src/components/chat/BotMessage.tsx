import React from 'react';
import { ChatMessage } from '../../types';
import { Bot } from 'lucide-react';
import SchedulePanel from './SchedulePanel';
import ProtocolPanel from './ProtocolPanel';
import MedicationPanel from './MedicationPanel';
import ExpandableAnswer from './ExpandableAnswer';

interface BotMessageProps {
  message: ChatMessage;
}

const BotMessage: React.FC<BotMessageProps> = ({ message }) => {
  return (
    <div className="flex gap-3">
      {/* Bot Avatar */}
      <div className="w-8 h-8 bg-primary rounded-full flex items-center justify-center flex-shrink-0">
        <Bot className="w-5 h-5 text-white" />
      </div>

      {/* Message Content */}
      <div className="flex-1 space-y-3">
        {/* Text Message with Expandable Answer */}
        {message.content && (
          <ExpandableAnswer
            summary={message.contentSummary}
            detailed={message.contentDetailed}
            fallback={message.content}
          />
        )}

        {/* Schedule Data Panel */}
        {message.scheduleData && (
          <SchedulePanel data={message.scheduleData} />
        )}

        {/* Protocol Data Panel */}
        {message.protocolData && (
          <ProtocolPanel data={message.protocolData} />
        )}

        {/* Medication Data Panel */}
        {message.medicationData && message.medicationData.length > 0 && (
          <MedicationPanel
            medications={message.medicationData}
            query={message.content}
          />
        )}
      </div>
    </div>
  );
};

export default BotMessage;
