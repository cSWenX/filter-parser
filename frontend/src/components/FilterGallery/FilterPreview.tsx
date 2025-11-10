import React from 'react';
import { Target, Calendar, TrendingUp, Palette } from 'lucide-react';
import { Button } from '../UI';
import { Utils } from '../../services';
import type { ParameterHistory, FilterParameters } from '../../types';

interface FilterPreviewProps {
  filter: ParameterHistory;
  className?: string;
}

const FilterPreview: React.FC<FilterPreviewProps> = ({
  filter,
  className = ''
}) => {
  const generatePreviewImage = () => {
    // 基于滤镜参数生成预览图样式
    const { brightness, contrast, saturation, temperature, hue } = filter.parameters;

    // 计算CSS滤镜值
    const cssFilters = [
      `brightness(${100 + brightness}%)`,
      `contrast(${100 + contrast}%)`,
      `saturate(${100 + saturation}%)`,
      `hue-rotate(${hue}deg)`
    ].join(' ');

    return cssFilters;
  };

  const getParameterColor = (value: number) => {
    if (Math.abs(value) < 5) return 'text-gray-600';
    return value > 0 ? 'text-green-600' : 'text-blue-600';
  };

  const getParameterBadgeColor = (value: number) => {
    if (Math.abs(value) < 5) return 'bg-gray-100 text-gray-600';
    return value > 0 ? 'bg-green-100 text-green-700' : 'bg-blue-100 text-blue-700';
  };

  const formatParameterValue = (key: string, value: number) => {
    const units = {
      brightness: '%',
      contrast: '%',
      saturation: '%',
      sharpness: '%',
      temperature: 'K',
      hue: '°',
      shadow: '%',
      highlight: '%'
    };

    const unit = units[key as keyof typeof units] || '';
    const sign = value > 0 ? '+' : '';
    return `${sign}${Math.round(value * 10) / 10}${unit}`;
  };

  const getParameterLabel = (key: string) => {
    const labels = {
      brightness: '亮度',
      contrast: '对比度',
      saturation: '饱和度',
      sharpness: '锐化',
      temperature: '色温',
      hue: '色调',
      shadow: '阴影',
      highlight: '高光'
    };
    return labels[key as keyof typeof labels] || key;
  };

  return (
    <div className={Utils.cn('bg-white rounded-lg shadow-sm border border-gray-200', className)}>
      {/* 头部信息 */}
      <div className="p-6 border-b border-gray-200">
        <h3 className="text-lg font-semibold text-gray-900 mb-2">
          {filter.name}
        </h3>

        <div className="flex items-center space-x-4 text-sm text-gray-600">
          <div className="flex items-center space-x-1">
            <Calendar className="w-4 h-4" />
            <span>{Utils.formatTime(filter.saved_time)}</span>
          </div>

          {filter.analysis_result && (
            <div className="flex items-center space-x-1">
              <Target className="w-4 h-4" />
              <span>置信度 {(filter.analysis_result.confidence_score * 100).toFixed(0)}%</span>
            </div>
          )}
        </div>
      </div>

      {/* 预览图片 */}
      <div className="p-6 border-b border-gray-200">
        <h4 className="font-medium text-gray-900 mb-3">效果预览</h4>

        <div className="grid grid-cols-1 gap-4">
          {/* 原图 */}
          <div className="text-center">
            <div className="w-full h-32 bg-gradient-to-br from-gray-300 to-gray-500 rounded-lg mb-2 flex items-center justify-center">
              <span className="text-white text-sm font-medium">原图</span>
            </div>
            <p className="text-xs text-gray-500">示例图片（原始效果）</p>
          </div>

          {/* 滤镜效果图 */}
          <div className="text-center">
            <div
              className="w-full h-32 bg-gradient-to-br from-gray-300 to-gray-500 rounded-lg mb-2 flex items-center justify-center"
              style={{ filter: generatePreviewImage() }}
            >
              <span className="text-white text-sm font-medium">滤镜效果</span>
            </div>
            <p className="text-xs text-gray-500">应用滤镜后的效果</p>
          </div>
        </div>
      </div>

      {/* 参数详情 */}
      <div className="p-6">
        <h4 className="font-medium text-gray-900 mb-4 flex items-center">
          <Palette className="w-4 h-4 mr-2" />
          参数详情
        </h4>

        <div className="space-y-3">
          {Object.entries(filter.parameters).map(([key, value]) => (
            <div key={key} className="flex items-center justify-between">
              <span className="text-sm text-gray-700">
                {getParameterLabel(key)}
              </span>
              <div className="flex items-center space-x-2">
                <span className={Utils.cn(
                  'text-sm font-medium',
                  getParameterColor(value)
                )}>
                  {formatParameterValue(key, value)}
                </span>
                <span className={Utils.cn(
                  'px-2 py-1 rounded-full text-xs font-medium',
                  getParameterBadgeColor(value)
                )}>
                  {Math.abs(value) < 5 ? '轻微' : value > 0 ? '增强' : '减弱'}
                </span>
              </div>
            </div>
          ))}
        </div>

        {/* 参数总结 */}
        <div className="mt-6 p-4 bg-gray-50 rounded-lg">
          <h5 className="font-medium text-gray-900 mb-2 flex items-center">
            <TrendingUp className="w-4 h-4 mr-2" />
            效果总结
          </h5>
          <p className="text-sm text-gray-600">
            {Utils.getParameterSummary(filter.parameters)}
          </p>
        </div>

        {/* 应用建议 */}
        {filter.analysis_result?.suggestions && (
          <div className="mt-4 p-4 bg-blue-50 rounded-lg">
            <h5 className="font-medium text-blue-900 mb-2">应用建议</h5>
            <ul className="text-sm text-blue-800 space-y-1">
              {filter.analysis_result.suggestions.map((suggestion, index) => (
                <li key={index} className="flex items-start">
                  <span className="text-blue-600 mr-2">•</span>
                  <span>{suggestion}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* 操作按钮 */}
        <div className="mt-6 pt-4 border-t border-gray-200">
          <div className="flex space-x-3">
            <Button
              variant="primary"
              className="flex-1"
              onClick={() => {
                // 切换到美化模块并应用此滤镜
                console.log('Apply filter:', filter.id);
              }}
            >
              应用到图片
            </Button>
            <Button
              variant="outline"
              onClick={() => {
                // 复制参数
                const paramsText = Object.entries(filter.parameters)
                  .map(([key, value]) => `${getParameterLabel(key)}: ${formatParameterValue(key, value)}`)
                  .join('\n');

                navigator.clipboard.writeText(paramsText).then(() => {
                  console.log('参数已复制');
                }).catch(() => {
                  console.error('复制失败');
                });
              }}
            >
              复制参数
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default FilterPreview;