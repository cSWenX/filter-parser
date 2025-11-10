import React from 'react';
import { Filter, Zap } from 'lucide-react';
import { Button, Loading } from '../UI';
import { Utils } from '../../services';
import type { ParameterHistory } from '../../types';

interface FilterSelectorProps {
  filters: ParameterHistory[];
  selectedFilter: ParameterHistory | null;
  onSelectFilter: (filter: ParameterHistory) => void;
  isProcessing: boolean;
  className?: string;
}

const FilterSelector: React.FC<FilterSelectorProps> = ({
  filters,
  selectedFilter,
  onSelectFilter,
  isProcessing,
  className = ''
}) => {
  if (filters.length === 0) {
    return (
      <div className={Utils.cn('text-center py-8', className)}>
        <Filter className="w-12 h-12 mx-auto mb-4 text-gray-400" />
        <h4 className="text-lg font-medium text-gray-900 mb-2">
          暂无可用滤镜
        </h4>
        <p className="text-gray-600 text-sm mb-4">
          前往"图片分析"模块分析图片并保存滤镜
        </p>
      </div>
    );
  }

  const getFilterThumbnail = (filter: ParameterHistory) => {
    const { brightness, saturation, temperature } = filter.parameters;

    let hue = 200;
    if (temperature > 50) hue = 30;
    if (temperature < -50) hue = 220;

    const sat = Math.max(30, 50 + saturation * 0.5);
    const light = Math.max(40, Math.min(60, 50 + brightness * 0.3));

    return `hsl(${hue}, ${sat}%, ${light}%)`;
  };

  const getFilterSummary = (filter: ParameterHistory) => {
    const significantParams = Object.entries(filter.parameters)
      .filter(([_, value]) => Math.abs(value) >= 5)
      .slice(0, 2);

    return significantParams.length > 0
      ? significantParams.map(([key, value]) => {
          const labels: Record<string, string> = {
            brightness: '亮度',
            contrast: '对比度',
            saturation: '饱和度',
            temperature: '色温'
          };
          return `${labels[key] || key}${value > 0 ? '+' : ''}${Math.round(value)}`;
        }).join(', ')
      : '轻微调整';
  };

  return (
    <div className={className}>
      {isProcessing && (
        <div className="mb-4 p-3 bg-blue-50 rounded-lg">
          <Loading size="sm" text="正在应用滤镜..." />
        </div>
      )}

      <div className="space-y-3 max-h-96 overflow-y-auto">
        {filters.map((filter) => {
          const isSelected = selectedFilter?.id === filter.id;

          return (
            <div
              key={filter.id}
              className={Utils.cn(
                'p-3 rounded-lg border-2 cursor-pointer transition-all duration-200',
                isSelected
                  ? 'border-primary-500 bg-primary-50'
                  : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50',
                isProcessing && 'opacity-50 pointer-events-none'
              )}
              onClick={() => !isProcessing && onSelectFilter(filter)}
            >
              <div className="flex items-center space-x-3">
                {/* 滤镜缩略图 */}
                <div
                  className="w-10 h-10 rounded-md flex-shrink-0"
                  style={{ backgroundColor: getFilterThumbnail(filter) }}
                />

                {/* 滤镜信息 */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between">
                    <h4 className="font-medium text-gray-900 truncate">
                      {filter.name}
                    </h4>
                    {isSelected && (
                      <Zap className="w-4 h-4 text-primary-600 flex-shrink-0" />
                    )}
                  </div>
                  <p className="text-xs text-gray-600 truncate">
                    {getFilterSummary(filter)}
                  </p>
                  <div className="flex items-center justify-between mt-1">
                    <span className="text-xs text-gray-500">
                      {Utils.formatTime(filter.saved_time)}
                    </span>
                    {filter.analysis_result && (
                      <span className="text-xs text-gray-500">
                        置信度 {(filter.analysis_result.confidence_score * 100).toFixed(0)}%
                      </span>
                    )}
                  </div>
                </div>
              </div>

              {/* 应用按钮（仅在选中时显示） */}
              {isSelected && !isProcessing && (
                <div className="mt-3 pt-3 border-t border-primary-200">
                  <Button
                    variant="primary"
                    size="sm"
                    onClick={(e) => {
                      e.stopPropagation();
                      onSelectFilter(filter);
                    }}
                    className="w-full"
                  >
                    应用此滤镜
                  </Button>
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* 滤镜统计 */}
      <div className="mt-4 pt-4 border-t border-gray-200">
        <div className="text-xs text-gray-500 text-center">
          共 {filters.length} 个可用滤镜
        </div>
      </div>
    </div>
  );
};

export default FilterSelector;