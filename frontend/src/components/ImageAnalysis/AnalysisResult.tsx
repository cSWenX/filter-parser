import React, { useState } from 'react';
import { Copy, Download, Save, Clock, Target, Share2 } from 'lucide-react';
import { Button } from '../UI';
import ParameterCard from './ParameterCard';
import { Utils } from '../../services';
import toast from 'react-hot-toast';
import type { ImageAnalysisResult } from '../../types';

interface AnalysisResultProps {
  result: ImageAnalysisResult;
  onSaveFilter: () => void;
  className?: string;
}

const AnalysisResult: React.FC<AnalysisResultProps> = ({
  result,
  onSaveFilter,
  className = ''
}) => {
  const handleCopyParameters = async () => {
    try {
      const parametersText = Object.entries(result.parameters)
        .map(([key, param]) => `${param.name}: ${param.direction} ${param.value}${param.unit}`)
        .join('\n');

      const fullText = `图片滤镜参数分析结果\n\n${parametersText}\n\n分析时间: ${result.analysis_time}秒\n置信度: ${(result.confidence_score * 100).toFixed(1)}%`;

      await navigator.clipboard.writeText(fullText);
      toast.success('参数已复制到剪贴板');
    } catch (error) {
      toast.error('复制失败，请手动选择文本');
    }
  };

  const handleDownloadTxt = () => {
    const parametersText = Object.entries(result.parameters)
      .map(([key, param]) => `${param.name}: ${param.direction} ${param.value}${param.unit} (${param.reference})`)
      .join('\n');

    const fullText = `图片滤镜参数分析结果\n` +
      `===================\n\n` +
      `图片ID: ${result.image_id}\n` +
      `分析时间: ${result.analysis_time}秒\n` +
      `置信度: ${(result.confidence_score * 100).toFixed(1)}%\n` +
      `生成时间: ${new Date(result.timestamp).toLocaleString('zh-CN')}\n\n` +
      `参数详情:\n${parametersText}\n\n` +
      `应用建议:\n${result.suggestions.map(s => `• ${s}`).join('\n')}`;

    const filename = `滤镜参数_${result.image_id}_${new Date().toISOString().slice(0, 10)}.txt`;
    Utils.downloadText(fullText, filename);
    toast.success('参数文件已下载');
  };

  const significantChanges = Object.entries(result.parameters).filter(
    ([_, param]) => param.value >= 5
  );

  const getConfidenceColor = (score: number) => {
    if (score >= 0.8) return 'text-green-600 bg-green-50';
    if (score >= 0.6) return 'text-yellow-600 bg-yellow-50';
    return 'text-red-600 bg-red-50';
  };

  return (
    <div className={Utils.cn('space-y-6', className)}>
      {/* 分析摘要卡片 */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900">分析结果</h3>
          <div className="flex items-center space-x-3">
            <div className="flex items-center space-x-2 text-sm text-gray-600">
              <Clock className="w-4 h-4" />
              <span>{result.analysis_time}秒</span>
            </div>
            <div className={Utils.cn(
              'flex items-center space-x-2 px-3 py-1 rounded-full text-sm font-medium',
              getConfidenceColor(result.confidence_score)
            )}>
              <Target className="w-4 h-4" />
              <span>置信度 {(result.confidence_score * 100).toFixed(1)}%</span>
            </div>
          </div>
        </div>

        {/* 操作按钮组 */}
        <div className="flex flex-wrap gap-3 mb-6">
          <Button
            variant="primary"
            onClick={onSaveFilter}
            className="flex items-center space-x-2"
          >
            <Save className="w-4 h-4" />
            <span>保存为滤镜</span>
          </Button>

          <Button
            variant="outline"
            onClick={handleCopyParameters}
            className="flex items-center space-x-2"
          >
            <Copy className="w-4 h-4" />
            <span>复制参数</span>
          </Button>

          <Button
            variant="outline"
            onClick={handleDownloadTxt}
            className="flex items-center space-x-2"
          >
            <Download className="w-4 h-4" />
            <span>导出TXT</span>
          </Button>
        </div>

        {/* 应用建议 */}
        {result.suggestions.length > 0 && (
          <div className="bg-blue-50 rounded-lg p-4">
            <h4 className="font-medium text-blue-900 mb-2 flex items-center">
              <Share2 className="w-4 h-4 mr-2" />
              应用建议
            </h4>
            <ul className="space-y-1">
              {result.suggestions.map((suggestion, index) => (
                <li key={index} className="text-blue-800 text-sm">
                  • {suggestion}
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>

      {/* 参数详情卡片网格 */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {Object.entries(result.parameters).map(([paramName, paramInfo]) => (
          <ParameterCard
            key={paramName}
            parameterName={paramName}
            parameterInfo={paramInfo}
          />
        ))}
      </div>

      {/* 无显著变化提示 */}
      {significantChanges.length === 0 && (
        <div className="bg-gray-50 rounded-lg p-6 text-center">
          <div className="w-16 h-16 mx-auto mb-4 text-gray-400">
            <svg className="w-full h-full" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <h4 className="text-lg font-medium text-gray-900 mb-2">接近原始效果</h4>
          <p className="text-gray-600">
            该图片未检测到显著滤镜参数调整，可能接近原始拍摄效果
          </p>
        </div>
      )}
    </div>
  );
};

export default AnalysisResult;