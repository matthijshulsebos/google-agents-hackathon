import React from 'react';
import { QuickAction } from '../../types';
import { Calendar, Pill, ClipboardList, Activity, AlertTriangle } from 'lucide-react';
import { useApp } from '../../context/AppContext';
import { useChatMessages } from '../../hooks/useChatMessages';

const iconMap: Record<string, React.ElementType> = {
  Calendar,
  Pill,
  ClipboardList,
  Activity,
  AlertTriangle,
};

interface QuickActionCardProps {
  action: QuickAction;
}

const QuickActionCard: React.FC<QuickActionCardProps> = ({ action }) => {
  const Icon = iconMap[action.icon];
  const { addChatMessage } = useApp();
  const { simulateBotResponse } = useChatMessages();

  const handleClick = () => {
    let userMessage = '';

    switch (action.id) {
      case 'schedule':
        userMessage = "I clicked on Schedule Info. Can you tell me about today's schedule and any special procedures for the nursery?";
        break;
      case 'medication':
        userMessage = "Show me the medication guide for today.";
        break;
      case 'supply':
        userMessage = "I need to check the supply inventory.";
        break;
      case 'patient':
        userMessage = "What about emergency protocols for the nursery? And can you show me patient status updates?";
        break;
      case 'emergency':
        userMessage = "What about emergency protocols for the nursery? And can you show me patient status updates?";
        break;
    }

    // Add user message
    const userMsg = {
      id: `msg-${Date.now()}`,
      type: 'user' as const,
      content: userMessage,
      timestamp: new Date(),
    };
    addChatMessage(userMsg);

    // Simulate bot response
    simulateBotResponse(userMessage, addChatMessage, () => {});
  };

  return (
    <button
      onClick={handleClick}
      className={`${action.bgColor} p-4 rounded-xl border-2 border-transparent hover:border-gray-300 transition-all group`}
    >
      <div className="flex flex-col items-center text-center gap-3">
        <div className={`${action.iconColor} group-hover:scale-110 transition-transform`}>
          <Icon className="w-8 h-8" />
        </div>
        <span className="text-sm font-medium text-gray-900">{action.label}</span>
      </div>
    </button>
  );
};

export default QuickActionCard;
