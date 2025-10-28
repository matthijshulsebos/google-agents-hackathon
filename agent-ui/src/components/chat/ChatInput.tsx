import React, { useState } from 'react';
import { Send } from 'lucide-react';
import { useApp } from '../../context/AppContext';
import { useChatMessages } from '../../hooks/useChatMessages';

const ChatInput: React.FC = () => {
  const [message, setMessage] = useState('');
  const { addChatMessage, setIsTyping } = useApp();
  const { simulateBotResponse } = useChatMessages();

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    if (message.trim()) {
      // Add user message
      const userMsg = {
        id: `msg-${Date.now()}`,
        type: 'user' as const,
        content: message,
        timestamp: new Date(),
      };
      addChatMessage(userMsg);

      // Show typing indicator and simulate bot response
      setIsTyping(true);
      simulateBotResponse(message, addChatMessage, setIsTyping);

      // Clear input
      setMessage('');
    }
  };

  return (
    <form onSubmit={handleSubmit} className="border-t border-gray-200 p-4 bg-white">
      <div className="flex items-center gap-3">
        <input
          type="text"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          placeholder="Type your message here..."
          className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
        />
        <button
          type="submit"
          disabled={!message.trim()}
          className="px-6 py-3 bg-primary text-white rounded-lg hover:bg-primary-dark transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
        >
          <Send className="w-5 h-5" />
          <span className="font-medium">Send</span>
        </button>
      </div>
    </form>
  );
};

export default ChatInput;
