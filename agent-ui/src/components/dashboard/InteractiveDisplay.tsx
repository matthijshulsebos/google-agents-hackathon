import React, { useEffect, useRef } from 'react';
import { useApp } from '../../context/AppContext';
import BotMessage from '../chat/BotMessage';
import UserMessage from '../chat/UserMessage';
import TypingIndicator from '../chat/TypingIndicator';

const InteractiveDisplay: React.FC = () => {
  const { chatMessages, isTyping } = useApp();
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [chatMessages, isTyping]);

  return (
    <div className="space-y-4">
      {chatMessages.map((message) => (
        message.type === 'bot' ? (
          <BotMessage key={message.id} message={message} />
        ) : (
          <UserMessage key={message.id} message={message} />
        )
      ))}
      {isTyping && <TypingIndicator />}
      <div ref={messagesEndRef} />
    </div>
  );
};

export default InteractiveDisplay;
