import React, { useState } from 'react';
import { Toaster } from 'react-hot-toast';
import { Sidebar } from './components/Navigation';
import { ImageAnalysis } from './components/ImageAnalysis';
import { FilterGallery } from './components/FilterGallery';
import { ImageEnhancement } from './components/ImageEnhancement';

function App() {
  const [activeModule, setActiveModule] = useState('analysis');

  const renderActiveModule = () => {
    switch (activeModule) {
      case 'analysis':
        return <ImageAnalysis className="flex-1" />;
      case 'filters':
        return <FilterGallery className="flex-1" />;
      case 'enhancement':
        return <ImageEnhancement className="flex-1" />;
      default:
        return <ImageAnalysis className="flex-1" />;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex">
      {/* 左侧菜单栏 */}
      <Sidebar
        activeModule={activeModule}
        onModuleChange={setActiveModule}
      />

      {/* 主内容区域 */}
      <div className="flex-1 flex flex-col">
        {/* 主内容 */}
        <main className="flex-1 p-6 overflow-auto">
          {renderActiveModule()}
        </main>

        {/* 底部信息 */}
        <footer className="border-t border-gray-200 bg-white px-6 py-4">
          <div className="flex items-center justify-between text-sm text-gray-600">
            <div>
              Filter Parser v2.0 - 图片滤镜参数分析和美化平台
            </div>
            <div className="flex items-center space-x-4">
              <span>当前模块: {
                activeModule === 'analysis' ? '图片分析' :
                activeModule === 'filters' ? '图片滤镜' :
                activeModule === 'enhancement' ? '图片美化' : '未知'
              }</span>
            </div>
          </div>
        </footer>
      </div>

      {/* Toast 通知 */}
      <Toaster
        position="top-right"
        toastOptions={{
          duration: 4000,
          style: {
            background: '#363636',
            color: '#fff',
          },
          success: {
            duration: 3000,
            iconTheme: {
              primary: '#10B981',
              secondary: '#fff',
            },
          },
          error: {
            duration: 5000,
            iconTheme: {
              primary: '#EF4444',
              secondary: '#fff',
            },
          },
        }}
      />
    </div>
  );
}

export default App;