import React from 'react';
import { Utils } from '../../services';
import type { ParameterInfo } from '../../types';

interface ParameterCardProps {
  parameterName: string;
  parameterInfo: ParameterInfo;
  className?: string;
}

const ParameterCard: React.FC<ParameterCardProps> = ({
  parameterName,
  parameterInfo,
  className = ''
}) => {
  const getDirectionColor = (direction: string) => {
    const increaseKeywords = ['增加', '增强', '偏暖', '偏红', '提亮', '提升'];
    const isIncrease = increaseKeywords.some(keyword => direction.includes(keyword));

    return isIncrease
      ? 'text-green-600 bg-green-50 border-green-200'
      : 'text-blue-600 bg-blue-50 border-blue-200';
  };

  const getValueDisplay = (value: number, unit: string) => {
    const sign = value > 0 ? '+' : '';
    const roundedValue = Math.round(value * 10) / 10; // 保留一位小数
    return `${sign}${roundedValue}${unit}`;
  };

  const getProgressBarStyle = (value: number, unit: string) => {
    // 根据不同单位设置不同的范围
    let maxRange = 100;
    if (unit === 'K') maxRange = 500;
    if (unit === '°') maxRange = 180;

    const percentage = Math.min(Math.abs(value) / maxRange, 1) * 50; // 最多50%
    const isPositive = value > 0;

    if (isPositive) {
      return {
        left: '50%',
        width: `${percentage}%`,
        backgroundColor: value > 0 ? '#10B981' : '#3B82F6'
      };
    } else {
      return {
        right: '50%',
        width: `${percentage}%`,
        backgroundColor: '#3B82F6'
      };
    }
  };

  return (
    <div className={Utils.cn(
      'bg-white rounded-lg border border-gray-200 p-4 hover:shadow-md transition-shadow',
      className
    )}>
      <div className="space-y-3">
        {/* 参数名称和标识 */}
        <div className="flex items-center justify-between">
          <h4 className="text-base font-medium text-gray-900">
            {parameterInfo.name}
          </h4>
          <span className="text-xs text-gray-500 font-mono">
            {parameterName}
          </span>
        </div>

        {/* 方向和数值 */}
        <div className="flex items-center justify-between">
          <span className={Utils.cn(
            'px-2 py-1 rounded-md text-xs font-medium border',
            getDirectionColor(parameterInfo.direction)
          )}>
            {parameterInfo.direction}
          </span>
          <span className="text-lg font-bold text-gray-900">
            {getValueDisplay(parameterInfo.value, parameterInfo.unit)}
          </span>
        </div>

        {/* 进度条可视化 */}
        <div className="space-y-2">
          <div className="flex justify-between text-xs text-gray-500">
            <span>-{parameterInfo.unit === 'K' ? '500' : parameterInfo.unit === '°' ? '180' : '100'}</span>
            <span>0</span>
            <span>+{parameterInfo.unit === 'K' ? '500' : parameterInfo.unit === '°' ? '180' : '100'}</span>
          </div>
          <div className="relative h-2 bg-gray-200 rounded-full overflow-hidden">
            {/* 进度条 */}
            <div
              className="absolute top-0 h-full transition-all duration-300 rounded-full"
              style={getProgressBarStyle(parameterInfo.value, parameterInfo.unit)}
            />
            {/* 中心线 */}
            <div className="absolute left-1/2 top-0 w-0.5 h-full bg-gray-400 transform -translate-x-0.5" />
          </div>
        </div>

        {/* 参考标准 */}
        <div className="text-xs text-gray-600 bg-gray-50 rounded p-2">
          <span className="font-medium">参考: </span>
          {parameterInfo.reference}
        </div>
      </div>
    </div>
  );
};

export default ParameterCard;