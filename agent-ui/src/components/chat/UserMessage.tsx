import React from 'react';
import { ChatMessage } from '../../types';

interface UserMessageProps {
  message: ChatMessage;
}

const UserMessage: React.FC<UserMessageProps> = ({ message }) => {
  return (
    <div className="flex justify-end">
      <div className="bg-primary text-white rounded-2xl rounded-tr-none px-4 py-3 max-w-2xl">
        <p className="text-sm">{message.content}</p>
      </div>
    </div>
  );
};

export default UserMessage;
