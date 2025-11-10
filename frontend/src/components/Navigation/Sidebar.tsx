import React from 'react';
import { Image, Filter, Sparkles } from 'lucide-react';
import { Utils } from '../../services';

interface SidebarProps {
  activeModule: string;
  onModuleChange: (module: string) => void;
}

interface MenuItem {
  id: string;
  label: string;
  icon: React.ComponentType<{ className?: string }>;
  description: string;
}

const menuItems: MenuItem[] = [
  {
    id: 'analysis',
    label: '图片分析',
    icon: Image,
    description: '上传图片分析滤镜参数'
  },
  {
    id: 'filters',
    label: '图片滤镜',
    icon: Filter,
    description: '管理保存的滤镜效果'
  },
  {
    id: 'enhancement',
    label: '图片美化',
    icon: Sparkles,
    description: '应用滤镜美化图片'
  }
];

const Sidebar: React.FC<SidebarProps> = ({ activeModule, onModuleChange }) => {
  return (
    <div className="w-64 bg-white border-r border-gray-200 flex flex-col">
      {/* 头部 */}
      <div className="p-6 border-b border-gray-200">
        <h1 className="text-xl font-bold text-gray-900">Filter Parser</h1>
        <p className="text-sm text-gray-600 mt-1">图片滤镜处理平台</p>
      </div>

      {/* 菜单项 */}
      <nav className="flex-1 p-4">
        <ul className="space-y-2">
          {menuItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeModule === item.id;

            return (
              <li key={item.id}>
                <button
                  onClick={() => onModuleChange(item.id)}
                  className={Utils.cn(
                    'w-full flex items-start p-4 rounded-lg text-left transition-colors duration-200',
                    isActive
                      ? 'bg-primary-50 text-primary-700 border border-primary-200'
                      : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                  )}
                >
                  <Icon className={Utils.cn(
                    'w-5 h-5 mt-0.5 mr-3 flex-shrink-0',
                    isActive ? 'text-primary-600' : 'text-gray-400'
                  )} />
                  <div className="flex-1">
                    <div className={Utils.cn(
                      'font-medium',
                      isActive ? 'text-primary-900' : 'text-gray-900'
                    )}>
                      {item.label}
                    </div>
                    <div className={Utils.cn(
                      'text-sm mt-1',
                      isActive ? 'text-primary-600' : 'text-gray-500'
                    )}>
                      {item.description}
                    </div>
                  </div>
                </button>
              </li>
            );
          })}
        </ul>
      </nav>

      {/* 底部信息 */}
      <div className="p-4 border-t border-gray-200">
        <div className="text-xs text-gray-500 space-y-1">
          <p>版本: v2.0</p>
          <p>已保存滤镜: <span className="font-medium">0</span></p>
        </div>
      </div>
    </div>
  );
};

export default Sidebar;