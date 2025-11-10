import React from 'react';
import { Copy, Download, Share2 } from 'lucide-react';
import { Button } from '../UI';
import { Utils } from '../../services';
import toast from 'react-hot-toast';
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
      ? 'text-green-600 bg-green-50'
      : 'text-blue-600 bg-blue-50';
  };

  const getValueDisplay = (value: number, unit: string) => {
    if (unit === 'K') {
      return `${value > 0 ? '+' : ''}${Math.round(value)}${unit}`;
    }
    return `${value > 0 ? '+' : ''}${Math.round(value)}${unit}`;
  };

  return (
    <div className={Utils.cn('bg-white rounded-lg border border-gray-200 p-4', className)}>
      <div className="space-y-3">
        {/* 参数名称 */}
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-medium text-gray-900">
            {parameterInfo.name}
          </h3>
          <span className="text-sm text-gray-500">
            {parameterName}
          </span>
        </div>

        {/* 方向和数值 */}
        <div className="flex items-center space-x-3">
          <span className={Utils.cn(
            'px-2 py-1 rounded-full text-xs font-medium',
            getDirectionColor(parameterInfo.direction)
          )}>
            {parameterInfo.direction}
          </span>
          <span className="text-xl font-bold text-gray-900">
            {getValueDisplay(parameterInfo.value, parameterInfo.unit)}
          </span>
        </div>

        {/* 参考标准 */}
        <div className="text-sm text-gray-600">
          <span className="font-medium">参考标准: </span>
          {parameterInfo.reference}
        </div>

        {/* 数值条 */}
        <div className="space-y-2">
          <div className="flex justify-between text-xs text-gray-500">
            <span>-100{parameterInfo.unit}</span>
            <span>0</span>
            <span>+100{parameterInfo.unit}</span>
          </div>
          <div className="relative h-2 bg-gray-200 rounded-full overflow-hidden">
            <div
              className="absolute top-0 h-full bg-primary-500 transition-all duration-300"
              style={{
                left: parameterInfo.value < 0 ? `${50 + (parameterInfo.value / 100) * 50}%` : '50%',
                right: parameterInfo.value > 0 ? `${50 - (parameterInfo.value / 100) * 50}%` : '50%'
              }}
            />
            {/* 中心线 */}
            <div className="absolute left-1/2 top-0 w-0.5 h-full bg-gray-400 transform -translate-x-0.5" />
          </div>
        </div>
      </div>
    </div>
  );
};

export default ParameterCard;