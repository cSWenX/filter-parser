import React, { useState, useEffect } from 'react';
import { Filter, Search, Eye, ChevronDown, ChevronUp, Settings } from 'lucide-react';
import { Button } from '../UI';
import { storageService } from '../../services';
import type { ParameterHistory } from '../../types';

interface FilterGalleryProps {
  className?: string;
}

// 预览基础图片的URL - 使用您提供的图片
const BASE_PREVIEW_IMAGE = '/images/preview-base.jpg';

const FilterGallery: React.FC<FilterGalleryProps> = ({ className = '' }) => {
  const [savedFilters, setSavedFilters] = useState<ParameterHistory[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedFilterId, setSelectedFilterId] = useState<string | null>(null);

  // 加载保存的滤镜
  useEffect(() => {
    const filters = storageService.getParameterHistory();
    setSavedFilters(filters);
  }, []);

  // 过滤搜索结果
  const filteredFilters = savedFilters.filter(filter =>
    filter.name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  // 将滤镜分组，每行5个
  const filterRows = [];
  for (let i = 0; i < filteredFilters.length; i += 5) {
    filterRows.push(filteredFilters.slice(i, i + 5));
  }

  const handleDeleteFilter = (filterId: string) => {
    const success = storageService.deleteParameterHistory(filterId);
    if (success) {
      setSavedFilters(prev => prev.filter(f => f.id !== filterId));
      if (selectedFilterId === filterId) {
        setSelectedFilterId(null);
      }
    }
  };

  const handleRenameFilter = (filterId: string, newName: string) => {
    const success = storageService.updateParameterHistory(filterId, { name: newName });
    if (success) {
      setSavedFilters(prev =>
        prev.map(f => f.id === filterId ? { ...f, name: newName } : f)
      );
    }
  };

  const toggleFilterDetails = (filterId: string) => {
    setSelectedFilterId(prev => prev === filterId ? null : filterId);
  };

  const generateFilterCSS = (parameters: any) => {
    const filters = [];

    if (typeof parameters.brightness === 'object' && parameters.brightness.value) {
      filters.push(`brightness(${100 + parameters.brightness.value}%)`);
    }
    if (typeof parameters.contrast === 'object' && parameters.contrast.value) {
      filters.push(`contrast(${100 + parameters.contrast.value}%)`);
    }
    if (typeof parameters.saturation === 'object' && parameters.saturation.value) {
      filters.push(`saturate(${100 + parameters.saturation.value}%)`);
    }
    if (typeof parameters.hue === 'object' && parameters.hue.value) {
      filters.push(`hue-rotate(${parameters.hue.value}deg)`);
    }
    if (typeof parameters.sharpness === 'object' && parameters.sharpness.value) {
      // CSS filter doesn't have sharpness, but we can simulate with contrast
      const sharpnessBoost = Math.min(parameters.sharpness.value * 0.5, 20);
      filters.push(`contrast(${100 + sharpnessBoost}%)`);
    }
    if (typeof parameters.temperature === 'object' && parameters.temperature.value) {
      // Simulate temperature with sepia and hue-rotate
      const tempValue = parameters.temperature.value;
      if (tempValue > 0) {
        filters.push(`sepia(${Math.min(tempValue / 10, 30)}%)`);
      } else {
        filters.push(`hue-rotate(${tempValue / 10}deg)`);
      }
    }

    return filters.length > 0 ? filters.join(' ') : 'none';
  };

  const selectedFilter = savedFilters.find(f => f.id === selectedFilterId);

  return (
    <div className={className}>
      <div className="space-y-6">
        {/* 头部 */}
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-2">滤镜画廊</h2>
          <p className="text-gray-600">
            管理和预览您保存的滤镜效果
          </p>
        </div>

        {/* 搜索栏 */}
        <div className="bg-white rounded-lg shadow-sm p-6">
          <div className="relative max-w-md mx-auto">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="搜索滤镜..."
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            />
          </div>
        </div>

        {/* 滤镜网格 */}
        <div className="bg-white rounded-lg shadow-sm p-6">
          {filterRows.length === 0 ? (
            <div className="text-center py-12">
              <Filter className="w-16 h-16 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                {searchQuery ? '未找到匹配的滤镜' : '还没有保存的滤镜'}
              </h3>
              <p className="text-gray-600">
                {searchQuery
                  ? '尝试使用不同的关键词搜索'
                  : '在图片分析页面分析图片后可以保存滤镜参数'
                }
              </p>
            </div>
          ) : (
            <div className="space-y-8">
              {filterRows.map((row, rowIndex) => (
                <div key={rowIndex}>
                  {/* 滤镜行 */}
                  <div className="grid grid-cols-5 gap-4">
                    {row.map((filter) => (
                      <div key={filter.id} className="space-y-2">
                        {/* 滤镜预览卡片 */}
                        <div className="group relative">
                          <div className="aspect-square bg-gray-100 rounded-lg overflow-hidden border-2 border-gray-200 hover:border-primary-300 transition-colors">
                            {/* 预览图片 */}
                            <div className="w-full h-full relative">
                              <img
                                src="/images/preview-desserts.jpg"
                                alt="预览基础图片"
                                className="w-full h-full object-cover"
                                style={{ filter: generateFilterCSS(filter.parameters) }}
                              />
                              {/* 悬停遮罩 */}
                              <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-20 transition-all duration-200 flex items-center justify-center">
                                <Button
                                  variant="outline"
                                  size="sm"
                                  onClick={() => toggleFilterDetails(filter.id)}
                                  className="opacity-0 group-hover:opacity-100 transition-opacity bg-white"
                                >
                                  <Eye className="w-4 h-4 mr-1" />
                                  详情
                                </Button>
                              </div>
                            </div>
                          </div>

                          {/* 滤镜名称 */}
                          <div className="text-center">
                            <h4 className="font-medium text-gray-900 text-sm truncate">
                              {filter.name}
                            </h4>
                            <p className="text-xs text-gray-500">
                              {new Date(filter.savedTime).toLocaleDateString()}
                            </p>
                          </div>
                        </div>
                      </div>
                    ))}

                    {/* 填充空白位置 */}
                    {Array.from({ length: 5 - row.length }).map((_, index) => (
                      <div key={`empty-${index}`} />
                    ))}
                  </div>

                  {/* 展开的详情面板 */}
                  {selectedFilter && row.some(f => f.id === selectedFilterId) && (
                    <div className="mt-6 border-t pt-6">
                      <div className="bg-gray-50 rounded-lg p-6">
                        {/* 详情头部 */}
                        <div className="flex items-center justify-between mb-4">
                          <h3 className="text-lg font-semibold text-gray-900 flex items-center">
                            <Settings className="w-5 h-5 mr-2" />
                            {selectedFilter.name} - 详细信息
                          </h3>
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => setSelectedFilterId(null)}
                          >
                            <ChevronUp className="w-4 h-4" />
                            收起
                          </Button>
                        </div>

                        {/* 对比图片 */}
                        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
                          {/* 原图 */}
                          <div className="space-y-3">
                            <h4 className="font-medium text-gray-900">原图</h4>
                            <div className="aspect-video bg-gray-100 rounded-lg overflow-hidden">
                              <img
                                src="/images/preview-desserts.jpg"
                                alt="原图"
                                className="w-full h-full object-cover"
                              />
                            </div>
                            <div className="text-center">
                              <span className="inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-gray-200 text-gray-700">
                                原始效果
                              </span>
                            </div>
                          </div>

                          {/* 滤镜效果 */}
                          <div className="space-y-3">
                            <h4 className="font-medium text-gray-900">滤镜效果</h4>
                            <div className="aspect-video bg-gray-100 rounded-lg overflow-hidden">
                              <img
                                src="/images/preview-desserts.jpg"
                                alt="滤镜效果"
                                className="w-full h-full object-cover"
                                style={{ filter: generateFilterCSS(selectedFilter.parameters) }}
                              />
                            </div>
                            <div className="text-center">
                              <span className="inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-primary-100 text-primary-700">
                                {selectedFilter.name} 效果
                              </span>
                            </div>
                          </div>
                        </div>

                        {/* 参数详情 */}
                        <div>
                          <h4 className="font-medium text-gray-900 mb-3">滤镜参数</h4>
                          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-3">
                            {Object.entries(selectedFilter.parameters)
                              .filter(([_, paramValue]) => {
                                if (typeof paramValue === 'object' && paramValue.value) {
                                  return Math.abs(paramValue.value) >= 0.1;
                                }
                                return false;
                              })
                              .map(([key, paramValue]) => {
                                const value = typeof paramValue === 'object' ? paramValue.value : 0;
                                const name = typeof paramValue === 'object' ? paramValue.name : key;
                                const unit = typeof paramValue === 'object' ? paramValue.unit : '';

                                return (
                                  <div key={key} className="bg-white rounded-lg p-3 border border-gray-200">
                                    <div className="text-xs text-gray-600 mb-1">{name}</div>
                                    <div className="font-medium text-gray-900">
                                      {value > 0 ? '+' : ''}{value.toFixed(1)}{unit}
                                    </div>
                                  </div>
                                );
                              })}
                          </div>
                        </div>

                        {/* 操作按钮 */}
                        <div className="mt-6 flex justify-end space-x-3">
                          <Button
                            variant="outline"
                            onClick={() => {
                              // TODO: 实现编辑功能
                              console.log('编辑滤镜:', selectedFilter.id);
                            }}
                          >
                            编辑滤镜
                          </Button>
                          <Button
                            variant="outline"
                            onClick={() => handleDeleteFilter(selectedFilter.id)}
                            className="text-red-600 border-red-200 hover:bg-red-50"
                          >
                            删除滤镜
                          </Button>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>

        {/* 统计信息 */}
        <div className="bg-white rounded-lg shadow-sm p-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="text-center">
              <div className="text-2xl font-bold text-gray-900">{savedFilters.length}</div>
              <div className="text-sm text-gray-600">总滤镜数量</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-gray-900">{filteredFilters.length}</div>
              <div className="text-sm text-gray-600">搜索结果</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-gray-900">{Math.ceil(filteredFilters.length / 5)}</div>
              <div className="text-sm text-gray-600">显示行数</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default FilterGallery;