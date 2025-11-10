import React, { useState } from 'react';
import { Save, Copy, Download, Clock, Target } from 'lucide-react';
import { Button, Modal } from '../UI';
import { Utils } from '../../services';
import toast from 'react-hot-toast';
import type { ImageAnalysisResult, FilterParameters } from '../../types';

interface SaveFilterModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSave: (name: string) => void;
  analysisResult: ImageAnalysisResult;
}

const SaveFilterModal: React.FC<SaveFilterModalProps> = ({
  isOpen,
  onClose,
  onSave,
  analysisResult
}) => {
  const [filterName, setFilterName] = useState('');
  const [nameError, setNameError] = useState('');

  const handleSave = () => {
    const validation = Utils.validateParameterName(filterName);
    if (!validation.valid) {
      setNameError(validation.message || '');
      return;
    }

    onSave(filterName.trim());
    setFilterName('');
    setNameError('');
    onClose();
  };

  const getParameterSummary = () => {
    const significantParams = Object.entries(analysisResult.parameters)
      .filter(([_, param]) => param.value >= 5)
      .slice(0, 3);

    return significantParams.length > 0
      ? significantParams.map(([_, param]) => `${param.name}${param.value > 0 ? '+' : ''}${Math.round(param.value)}`).join(', ')
      : '轻微调整';
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="保存为滤镜" size="md">
      <div className="space-y-6">
        {/* 滤镜预览信息 */}
        <div className="bg-gray-50 rounded-lg p-4">
          <h4 className="font-medium text-gray-900 mb-2">滤镜效果预览</h4>
          <div className="text-sm text-gray-600 space-y-1">
            <p><span className="font-medium">主要调整:</span> {getParameterSummary()}</p>
            <p><span className="font-medium">置信度:</span> {(analysisResult.confidence_score * 100).toFixed(1)}%</p>
            <p><span className="font-medium">分析时间:</span> {analysisResult.analysis_time}秒</p>
          </div>
        </div>

        {/* 滤镜命名 */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            滤镜名称 <span className="text-red-500">*</span>
          </label>
          <input
            type="text"
            value={filterName}
            onChange={(e) => {
              setFilterName(e.target.value);
              setNameError('');
            }}
            placeholder="请输入滤镜名称（如：暖色风景、冷色人像等）"
            className={Utils.cn(
              'w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500',
              nameError ? 'border-red-300' : 'border-gray-300'
            )}
            maxLength={20}
          />
          {nameError && (
            <p className="mt-1 text-sm text-red-600">{nameError}</p>
          )}
          <p className="mt-1 text-xs text-gray-500">
            支持中英文、数字、下划线，最多20个字符
          </p>
        </div>

        {/* 操作按钮 */}
        <div className="flex justify-end space-x-3">
          <Button variant="outline" onClick={onClose}>
            取消
          </Button>
          <Button
            onClick={handleSave}
            disabled={!filterName.trim()}
            className="flex items-center space-x-2"
          >
            <Save className="w-4 h-4" />
            <span>保存滤镜</span>
          </Button>
        </div>
      </div>
    </Modal>
  );
};

export default SaveFilterModal;