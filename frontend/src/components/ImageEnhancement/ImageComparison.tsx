import React from 'react';
import { ArrowRight, Image as ImageIcon, Sparkles, RefreshCw } from 'lucide-react';
import { Loading } from '../UI';
import { Utils } from '../../services';
import type { UploadedImage, ParameterHistory } from '../../types';

interface ImageComparisonProps {
  originalImage: UploadedImage;
  originalImageUrl: string | null;
  enhancedImageUrl: string | null;
  selectedFilter: ParameterHistory | null;
  isProcessing: boolean;
  className?: string;
}

const ImageComparison: React.FC<ImageComparisonProps> = ({
  originalImage,
  originalImageUrl,
  enhancedImageUrl,
  selectedFilter,
  isProcessing,
  className = ''
}) => {

  return (
    <div className={Utils.cn('bg-white rounded-lg shadow-sm', className)}>
      {/* 头部信息 */}
      <div className="p-6 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold text-gray-900">
            图片对比
          </h3>

          {selectedFilter && (
            <div className="flex items-center space-x-2 text-sm text-gray-600">
              <Sparkles className="w-4 h-4" />
              <span>当前滤镜: {selectedFilter.name}</span>
            </div>
          )}
        </div>

        {/* 图片信息 */}
        <div className="mt-3 flex items-center space-x-4 text-sm text-gray-600">
          <div className="flex items-center space-x-1">
            <ImageIcon className="w-4 h-4" />
            <span>{originalImage.filename}</span>
          </div>
          <span>•</span>
          <span>{originalImage.dimensions[0]} × {originalImage.dimensions[1]}</span>
          <span>•</span>
          <span>{Utils.formatFileSize(originalImage.size)}</span>
        </div>
      </div>

      {/* 对比区域 */}
      <div className="p-6">
        {isProcessing ? (
          /* 处理中状态 */
          <div className="text-center py-12">
            <Loading size="lg" text="正在应用滤镜效果..." />
            <p className="text-gray-600 mt-4">
              正在处理图片，请稍候...
            </p>
          </div>
        ) : (
          /* 对比显示 */
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* 原图 */}
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <h4 className="font-medium text-gray-900">原图</h4>
                <span className="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded">
                  Original
                </span>
              </div>

              <div className="aspect-video bg-gradient-to-br from-gray-200 to-gray-400 rounded-lg overflow-hidden">
                {originalImageUrl ? (
                  <img
                    src={originalImageUrl}
                    alt={originalImage.filename}
                    className="w-full h-full object-cover"
                  />
                ) : (
                  <div className="w-full h-full flex items-center justify-center text-white">
                    <div className="text-center">
                      <ImageIcon className="w-12 h-12 mx-auto mb-2 opacity-70" />
                      <p className="text-sm opacity-90">原始图片</p>
                      <p className="text-xs opacity-70">{originalImage.filename}</p>
                    </div>
                  </div>
                )}
              </div>

              <div className="text-center">
                <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                  原始效果
                </span>
              </div>
            </div>

            {/* 箭头指示器 (仅在大屏幕显示) */}
            <div className="hidden lg:flex items-center justify-center">
              <div className="text-center">
                <ArrowRight className="w-8 h-8 text-gray-400 mx-auto mb-2" />
                <p className="text-xs text-gray-500">
                  {selectedFilter ? '滤镜效果' : '选择滤镜'}
                </p>
              </div>
            </div>

            {/* 处理后图片 */}
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <h4 className="font-medium text-gray-900">
                  {enhancedImageUrl ? '美化效果' : '等待处理'}
                </h4>
                {enhancedImageUrl && (
                  <span className="text-xs text-white bg-primary-500 px-2 py-1 rounded">
                    Enhanced
                  </span>
                )}
              </div>

              <div className="aspect-video bg-gradient-to-br from-gray-200 to-gray-400 rounded-lg overflow-hidden relative">
                {enhancedImageUrl ? (
                  /* 显示后端处理后的图片 */
                  <img
                    src={enhancedImageUrl}
                    alt="Enhanced image"
                    className="w-full h-full object-cover"
                  />
                ) : (
                  /* 等待处理状态 */
                  <div className="w-full h-full flex items-center justify-center text-gray-500">
                    <div className="text-center">
                      <RefreshCw className="w-12 h-12 mx-auto mb-2 opacity-50" />
                      <p className="text-sm">选择滤镜开始美化</p>
                      <p className="text-xs opacity-70">点击左侧滤镜进行处理</p>
                    </div>
                  </div>
                )}
              </div>

              <div className="text-center">
                {enhancedImageUrl ? (
                  <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-primary-100 text-primary-800">
                    <Sparkles className="w-3 h-3 mr-1" />
                    已应用滤镜
                  </span>
                ) : (
                  <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-600">
                    等待处理
                  </span>
                )}
              </div>
            </div>
          </div>
        )}

        {/* 滤镜参数信息 */}
        {selectedFilter && !isProcessing && (
          <div className="mt-6 pt-6 border-t border-gray-200">
            <h4 className="font-medium text-gray-900 mb-3">当前滤镜参数</h4>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
              {Object.entries(selectedFilter.parameters)
                .filter(([_, paramValue]) => {
                  if (typeof paramValue === 'object' && paramValue.value) {
                    return Math.abs(paramValue.value) >= 1;
                  }
                  if (typeof paramValue === 'number') {
                    return Math.abs(paramValue) >= 1;
                  }
                  return false;
                })
                .slice(0, 4)
                .map(([key, paramValue]) => {
                  const value = typeof paramValue === 'object' ? paramValue.value : paramValue;
                  const name = typeof paramValue === 'object' ? paramValue.name : key;
                  const unit = typeof paramValue === 'object' ? paramValue.unit : '';

                  const labels: Record<string, string> = {
                    brightness: '亮度',
                    contrast: '对比度',
                    saturation: '饱和度',
                    sharpness: '锐化',
                    temperature: '色温',
                    hue: '色调',
                    shadow: '阴影',
                    highlight: '高光'
                  };

                  const displayName = name || labels[key] || key;
                  const displayUnit = unit || (key === 'temperature' ? 'K' : key === 'hue' ? '°' : '%');

                  return (
                    <div key={key} className="text-center p-3 bg-gray-50 rounded-lg">
                      <p className="text-xs text-gray-600">{displayName}</p>
                      <p className="font-medium text-gray-900">
                        {value > 0 ? '+' : ''}{Math.round(value)}{displayUnit}
                      </p>
                    </div>
                  );
                })}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ImageComparison;