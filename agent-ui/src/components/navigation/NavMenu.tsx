import React from 'react';
import { useApp } from '../../context/AppContext';
import { navItems } from '../../data/mockData';
import { LayoutDashboard, Users, BookOpen, Package, Heart, GraduationCap } from 'lucide-react';

const iconMap: Record<string, React.ElementType> = {
  LayoutDashboard,
  Users,
  BookOpen,
  Package,
  Heart,
  GraduationCap,
};

const NavMenu: React.FC = () => {
  const { activeNav, setActiveNav } = useApp();

  return (
    <nav className="px-3 space-y-1">
      {navItems.map((item) => {
        const Icon = iconMap[item.icon];
        const isActive = activeNav === item.id;

        return (
          <button
            key={item.id}
            onClick={() => setActiveNav(item.id)}
            className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg transition-colors text-left ${
              isActive
                ? 'bg-primary text-white'
                : 'text-gray-700 hover:bg-gray-100'
            }`}
          >
            <Icon className="w-5 h-5 flex-shrink-0" />
            <span className="text-sm font-medium">{item.label}</span>
          </button>
        );
      })}
    </nav>
  );
};

export default NavMenu;
