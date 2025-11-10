import React, { useState } from 'react';
import { MoreVertical, Edit2, Trash2, Eye, Calendar } from 'lucide-react';
import { Button, Modal } from '../UI';
import { Utils } from '../../services';
import toast from 'react-hot-toast';
import type { ParameterHistory } from '../../types';

interface FilterCardProps {
  filter: ParameterHistory;
  isSelected: boolean;
  onSelect: () => void;
  onDelete: () => void;
  onRename: (newName: string) => void;
  className?: string;
}

const FilterCard: React.FC<FilterCardProps> = ({
  filter,
  isSelected,
  onSelect,
  onDelete,
  onRename,
  className = ''
}) => {
  const [showActions, setShowActions] = useState(false);
  const [showRenameModal, setShowRenameModal] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [newName, setNewName] = useState(filter.name);

  const handleRename = () => {
    const validation = Utils.validateParameterName(newName);
    if (!validation.valid) {
      toast.error(validation.message || '名称无效');
      return;
    }

    onRename(newName.trim());
    setShowRenameModal(false);
    toast.success('滤镜重命名成功');
  };

  const handleDelete = () => {
    onDelete();
    setShowDeleteModal(false);
    toast.success('滤镜已删除');
  };

  const getParameterSummary = () => {
    const significantParams = Object.entries(filter.parameters)
      .filter(([_, value]) => Math.abs(value) >= 5)
      .slice(0, 3);

    return significantParams.length > 0
      ? significantParams.map(([key, value]) => {
          const label = {
            brightness: '亮度',
            contrast: '对比度',
            saturation: '饱和度',
            sharpness: '锐化',
            temperature: '色温',
            hue: '色调',
            shadow: '阴影',
            highlight: '高光'
          }[key] || key;
          return `${label}${value > 0 ? '+' : ''}${Math.round(value)}`;
        }).join(', ')
      : '轻微调整';
  };

  const getFilterThumbnail = () => {
    // 生成基于参数的渐变色缩略图
    const { brightness, saturation, temperature } = filter.parameters;

    let hue = 200; // 默认蓝色
    if (temperature > 50) hue = 30; // 暖色调
    if (temperature < -50) hue = 220; // 冷色调

    const sat = Math.max(30, 50 + saturation * 0.5);
    const light = Math.max(40, Math.min(60, 50 + brightness * 0.3));

    return `hsl(${hue}, ${sat}%, ${light}%)`;
  };

  return (
    <>
      <div
        className={Utils.cn(
          'bg-white rounded-lg border-2 p-4 cursor-pointer transition-all duration-200 hover:shadow-md',
          isSelected
            ? 'border-primary-500 shadow-lg ring-2 ring-primary-200'
            : 'border-gray-200 hover:border-gray-300',
          className
        )}
        onClick={onSelect}
      >
        {/* 头部：名称和操作 */}
        <div className="flex items-center justify-between mb-3">
          <h3 className="font-medium text-gray-900 truncate flex-1 mr-2">
            {filter.name}
          </h3>
          <div className="relative">
            <button
              onClick={(e) => {
                e.stopPropagation();
                setShowActions(!showActions);
              }}
              className="p-1 text-gray-400 hover:text-gray-600 rounded"
            >
              <MoreVertical className="w-4 h-4" />
            </button>

            {/* 操作菜单 */}
            {showActions && (
              <div className="absolute right-0 top-8 bg-white border border-gray-200 rounded-lg shadow-lg z-10 min-w-32">
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    setShowActions(false);
                    onSelect();
                  }}
                  className="w-full px-3 py-2 text-left text-sm hover:bg-gray-50 flex items-center space-x-2"
                >
                  <Eye className="w-4 h-4" />
                  <span>预览</span>
                </button>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    setShowActions(false);
                    setNewName(filter.name);
                    setShowRenameModal(true);
                  }}
                  className="w-full px-3 py-2 text-left text-sm hover:bg-gray-50 flex items-center space-x-2"
                >
                  <Edit2 className="w-4 h-4" />
                  <span>重命名</span>
                </button>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    setShowActions(false);
                    setShowDeleteModal(true);
                  }}
                  className="w-full px-3 py-2 text-left text-sm hover:bg-gray-50 text-red-600 flex items-center space-x-2"
                >
                  <Trash2 className="w-4 h-4" />
                  <span>删除</span>
                </button>
              </div>
            )}
          </div>
        </div>

        {/* 滤镜缩略图 */}
        <div className="mb-3">
          <div
            className="w-full h-24 rounded-lg flex items-center justify-center text-white font-medium"
            style={{ backgroundColor: getFilterThumbnail() }}
          >
            <span className="text-sm opacity-90">滤镜预览</span>
          </div>
        </div>

        {/* 参数摘要 */}
        <div className="space-y-2">
          <p className="text-sm text-gray-600 line-clamp-2">
            {getParameterSummary()}
          </p>

          {/* 置信度和时间 */}
          <div className="flex items-center justify-between text-xs text-gray-500">
            <div className="flex items-center space-x-1">
              <Calendar className="w-3 h-3" />
              <span>{Utils.formatTime(filter.saved_time)}</span>
            </div>
            {filter.analysis_result && (
              <span className="font-medium">
                置信度 {(filter.analysis_result.confidence_score * 100).toFixed(0)}%
              </span>
            )}
          </div>
        </div>

        {/* 选中指示器 */}
        {isSelected && (
          <div className="mt-3 pt-3 border-t border-primary-200">
            <div className="flex items-center text-primary-600 text-sm">
              <Eye className="w-4 h-4 mr-1" />
              <span>已选中</span>
            </div>
          </div>
        )}
      </div>

      {/* 点击外部关闭菜单 */}
      {showActions && (
        <div
          className="fixed inset-0 z-5"
          onClick={() => setShowActions(false)}
        />
      )}

      {/* 重命名弹窗 */}
      <Modal
        isOpen={showRenameModal}
        onClose={() => setShowRenameModal(false)}
        title="重命名滤镜"
        size="sm"
      >
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              滤镜名称
            </label>
            <input
              type="text"
              value={newName}
              onChange={(e) => setNewName(e.target.value)}
              placeholder="请输入新的滤镜名称"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
              maxLength={20}
            />
            <p className="mt-1 text-xs text-gray-500">
              支持中英文、数字、下划线，最多20个字符
            </p>
          </div>

          <div className="flex justify-end space-x-3">
            <Button
              variant="outline"
              onClick={() => setShowRenameModal(false)}
            >
              取消
            </Button>
            <Button
              onClick={handleRename}
              disabled={!newName.trim() || newName === filter.name}
            >
              确认重命名
            </Button>
          </div>
        </div>
      </Modal>

      {/* 删除确认弹窗 */}
      <Modal
        isOpen={showDeleteModal}
        onClose={() => setShowDeleteModal(false)}
        title="删除滤镜"
        size="sm"
      >
        <div className="space-y-4">
          <div className="text-center">
            <div className="w-12 h-12 mx-auto mb-4 bg-red-100 rounded-full flex items-center justify-center">
              <Trash2 className="w-6 h-6 text-red-600" />
            </div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              确认删除滤镜
            </h3>
            <p className="text-gray-600">
              确定要删除滤镜 "<span className="font-medium">{filter.name}</span>" 吗？
            </p>
            <p className="text-sm text-red-600 mt-2">
              此操作无法撤销
            </p>
          </div>

          <div className="flex justify-end space-x-3">
            <Button
              variant="outline"
              onClick={() => setShowDeleteModal(false)}
            >
              取消
            </Button>
            <Button
              variant="danger"
              onClick={handleDelete}
            >
              确认删除
            </Button>
          </div>
        </div>
      </Modal>
    </>
  );
};

export default FilterCard;