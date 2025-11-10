import React, { useState } from 'react';
import { Upload, Image as ImageIcon, Sparkles, Save } from 'lucide-react';
import { Button, Loading } from '../UI';
import AnalysisResult from './AnalysisResult';
import SaveFilterModal from './SaveFilterModal';
import { ImageUpload } from '../shared';
import { useAppStore } from '../../store/useAppStore';
import { apiService, storageService } from '../../services';
import toast from 'react-hot-toast';
import type { ImageAnalysisResult } from '../../types';

interface ImageAnalysisProps {
  className?: string;
}

const ImageAnalysis: React.FC<ImageAnalysisProps> = ({ className = '' }) => {
  const {
    currentImage,
    analysisResult,
    processingStatus,
    setCurrentImage,
    setProcessingStatus,
    setAnalysisResult,
    setError
  } = useAppStore();

  const [showSaveModal, setShowSaveModal] = useState(false);

  const handleImageUpload = async (file: File) => {
    try {
      setProcessingStatus('uploading');
      setError(null);

      // 上传图片
      const uploadResult = await apiService.uploadImage(file);

      // 创建图片对象
      const uploadedImage = {
        id: uploadResult.image_id,
        filename: uploadResult.filename,
        url: '',
        size: uploadResult.file_size,
        dimensions: uploadResult.dimensions,
        upload_time: new Date().toISOString()
      };

      setCurrentImage(uploadedImage);
      setProcessingStatus('analyzing');

      // 分析图片参数
      const analysisResponse = await apiService.analyzeImage(uploadResult.image_id);

      // 构造分析结果
      const result: ImageAnalysisResult = {
        image_id: analysisResponse.image_id,
        parameters: analysisResponse.parameters,
        analysis_time: analysisResponse.analysis_time,
        confidence_score: analysisResponse.confidence_score,
        suggestions: analysisResponse.suggestions,
        timestamp: new Date().toISOString()
      };

      setAnalysisResult(result);
      setProcessingStatus('completed');

      toast.success('图片分析完成！');
    } catch (error) {
      console.error('Upload or analysis error:', error);
      setError(error instanceof Error ? error.message : '处理失败，请重试');
      setProcessingStatus('error');
      toast.error('处理失败，请重试');
    }
  };

  const handleSaveFilter = async (filterName: string) => {
    if (!analysisResult) return;

    try {
      // 优化的滤镜参数转换逻辑
      const filterParameters = convertAnalysisToFilterParameters(analysisResult.parameters);

      // 保存到本地存储
      const savedFilter = storageService.saveParameterHistory(
        filterName,
        filterParameters,
        {
          confidence_score: analysisResult.confidence_score,
          suggestions: analysisResult.suggestions,
          source: 'enhanced_analysis',
          timestamp: new Date().toISOString()
        }
      );

      toast.success(`滤镜"${filterName}"已保存成功！`);
    } catch (error) {
      console.error('Save filter error:', error);
      toast.error(error instanceof Error ? error.message : '保存失败');
    }
  };

  // 增强的参数转换方法
  const convertAnalysisToFilterParameters = (analysisParameters: any) => {
    const filterParameters = {
      brightness: 0,
      contrast: 0,
      saturation: 0,
      sharpness: 0,
      temperature: 0,
      hue: 0,
      shadow: 0,
      highlight: 0
    };

    // 智能参数映射表
    const parameterMapping = {
      brightness: {
        positive_keywords: ['增加', '提亮', '提升', '增强'],
        negative_keywords: ['降低', '减少', '压暗', '减弱'],
        neutral_keywords: ['适中', '平衡', '正常'],
        scale_factor: 1.0 // 直接使用分析结果的值
      },
      contrast: {
        positive_keywords: ['增加', '提升', '增强', '强化'],
        negative_keywords: ['降低', '减少', '柔化', '减弱'],
        neutral_keywords: ['适中', '平衡', '正常'],
        scale_factor: 1.0
      },
      saturation: {
        positive_keywords: ['增加', '提升', '增强', '鲜艳'],
        negative_keywords: ['降低', '减少', '淡化', '减弱'],
        neutral_keywords: ['适中', '平衡', '正常'],
        scale_factor: 1.0
      },
      sharpness: {
        positive_keywords: ['增强', '锐化', '清晰', '提升'],
        negative_keywords: ['降低', '模糊', '柔化', '减弱'],
        neutral_keywords: ['适中', '平衡', '正常'],
        scale_factor: 1.0
      },
      temperature: {
        positive_keywords: ['偏暖', '暖色', '黄调', '橙调'],
        negative_keywords: ['偏冷', '冷色', '蓝调', '青调'],
        neutral_keywords: ['中性', '平衡', '正常'],
        scale_factor: 1.0
      },
      hue: {
        positive_keywords: ['调整', '偏移', '校正'],
        negative_keywords: ['调整', '偏移', '校正'],
        neutral_keywords: ['适中', '平衡', '正常'],
        scale_factor: 1.0
      },
      shadow: {
        positive_keywords: ['提亮', '增加', '提升', '恢复'],
        negative_keywords: ['压暗', '降低', '减少'],
        neutral_keywords: ['适中', '平衡', '正常'],
        scale_factor: 1.0
      },
      highlight: {
        positive_keywords: ['提亮', '增加', '提升'],
        negative_keywords: ['降低', '减少', '压制', '恢复'],
        neutral_keywords: ['适中', '平衡', '正常'],
        scale_factor: 1.0
      }
    };

    // 处理每个参数
    Object.entries(analysisParameters).forEach(([key, param]) => {
      if (key in filterParameters && param && typeof param === 'object') {
        const direction = param.direction || '';
        const value = parseFloat(param.value) || 0;
        const mapping = parameterMapping[key as keyof typeof parameterMapping];

        if (mapping) {
          // 检查方向关键词
          let adjustedValue = 0;

          if (mapping.neutral_keywords.some(keyword => direction.includes(keyword))) {
            // 中性值，不需要调整
            adjustedValue = 0;
          } else if (mapping.positive_keywords.some(keyword => direction.includes(keyword))) {
            // 正向调整
            adjustedValue = Math.abs(value) * mapping.scale_factor;
          } else if (mapping.negative_keywords.some(keyword => direction.includes(keyword))) {
            // 负向调整
            adjustedValue = -Math.abs(value) * mapping.scale_factor;
          } else {
            // 无法识别方向，基于数值符号
            adjustedValue = value * mapping.scale_factor;
          }

          // 应用阈值限制
          adjustedValue = Math.max(-100, Math.min(100, adjustedValue));

          // 对小数值进行四舍五入
          filterParameters[key as keyof typeof filterParameters] =
            Math.abs(adjustedValue) < 0.5 ? 0 : Number(adjustedValue.toFixed(1));
        }
      }
    });

    // 特殊处理色温参数（K值转换为百分比）
    if (analysisParameters.temperature && analysisParameters.temperature.value) {
      const tempValue = parseFloat(analysisParameters.temperature.value);
      if (Math.abs(tempValue) > 50) {
        // 色温值过大，需要缩放
        filterParameters.temperature = Number((tempValue / 100).toFixed(1));
      }
    }

    // 特殊处理色调参数（角度值处理）
    if (analysisParameters.hue && analysisParameters.hue.value) {
      const hueValue = parseFloat(analysisParameters.hue.value);
      // 确保色调值在合理范围内 (-30° to +30°)
      filterParameters.hue = Math.max(-30, Math.min(30, Number(hueValue.toFixed(1))));
    }

    return filterParameters;
  };

  return (
    <div className={className}>
      <div className="space-y-6">
        {/* 模块头部 */}
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-2">图片分析</h2>
          <p className="text-gray-600">
            上传图片，自动分析滤镜参数，支持保存为自定义滤镜
          </p>
        </div>

        <div className="grid grid-cols-1 xl:grid-cols-2 gap-8">
          {/* 左侧：图片上传 */}
          <div className="space-y-6">
            <div className="bg-white rounded-lg shadow-sm p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                上传图片
              </h3>
              <ImageUpload onUpload={handleImageUpload} />
            </div>

            {/* 当前图片信息 */}
            {currentImage && (
              <div className="bg-white rounded-lg shadow-sm p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">
                  图片信息
                </h3>
                <div className="flex items-center space-x-4">
                  <div className="flex-shrink-0">
                    <ImageIcon className="w-10 h-10 text-gray-400" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-900 truncate">
                      {currentImage.filename}
                    </p>
                    <div className="text-sm text-gray-500 space-y-1">
                      <p>尺寸: {currentImage.dimensions[0]} × {currentImage.dimensions[1]}</p>
                      <p>大小: {(currentImage.size / 1024).toFixed(1)} KB</p>
                    </div>
                  </div>
                </div>

                {processingStatus === 'analyzing' && (
                  <div className="mt-4 pt-4 border-t border-gray-200">
                    <Loading size="sm" text="正在分析参数..." />
                  </div>
                )}
              </div>
            )}
          </div>

          {/* 右侧：分析结果 */}
          <div>
            {analysisResult ? (
              <AnalysisResult
                result={analysisResult}
                onSaveFilter={() => setShowSaveModal(true)}
              />
            ) : (
              <div className="bg-white rounded-lg shadow-sm p-6">
                <div className="text-center py-12">
                  <div className="w-16 h-16 mx-auto mb-4 text-gray-400">
                    <svg className="w-full h-full" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M4 3a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V5a2 2 0 00-2-2H4zm12 12H4l4-8 3 6 2-4 3 6z" clipRule="evenodd" />
                    </svg>
                  </div>
                  <h3 className="text-lg font-medium text-gray-900 mb-2">
                    等待图片上传
                  </h3>
                  <p className="text-gray-600">
                    上传一张带滤镜效果的图片，我们将自动分析其滤镜参数
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* 功能说明 */}
        <div className="bg-white rounded-lg shadow-sm p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">功能说明</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {[
              { icon: Upload, title: '上传图片', desc: '支持JPG、PNG、WEBP格式' },
              { icon: ImageIcon, title: '参数分析', desc: '自动识别8类核心滤镜参数' },
              { icon: Sparkles, title: '置信度', desc: '显示分析结果的准确度' },
              { icon: Save, title: '保存滤镜', desc: '将分析结果保存为自定义滤镜' }
            ].map((item, index) => {
              const Icon = item.icon;
              return (
                <div key={index} className="text-center">
                  <div className="w-12 h-12 mx-auto mb-3 bg-primary-100 rounded-lg flex items-center justify-center">
                    <Icon className="w-6 h-6 text-primary-600" />
                  </div>
                  <h4 className="font-medium text-gray-900 mb-1">{item.title}</h4>
                  <p className="text-sm text-gray-600">{item.desc}</p>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* 保存滤镜弹窗 */}
      {analysisResult && (
        <SaveFilterModal
          isOpen={showSaveModal}
          onClose={() => setShowSaveModal(false)}
          onSave={handleSaveFilter}
          analysisResult={analysisResult}
        />
      )}
    </div>
  );
};

export default ImageAnalysis;