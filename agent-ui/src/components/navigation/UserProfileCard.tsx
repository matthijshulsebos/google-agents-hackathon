import React from 'react';
import { useApp } from '../../context/AppContext';
import { Settings } from 'lucide-react';

const UserProfileCard: React.FC = () => {
  const { user } = useApp();

  return (
    <div className="p-4 flex items-center gap-3">
      <img
        src={user.avatar}
        alt={user.name}
        className="w-10 h-10 rounded-full"
      />
      <div className="flex-1 min-w-0">
        <p className="text-sm font-semibold text-gray-900 truncate">{user.name}</p>
        <p className="text-xs text-gray-500 truncate">{user.title}</p>
      </div>
      <button className="p-2 hover:bg-gray-100 rounded-lg transition-colors">
        <Settings className="w-5 h-5 text-gray-400" />
      </button>
    </div>
  );
};

export default UserProfileCard;
