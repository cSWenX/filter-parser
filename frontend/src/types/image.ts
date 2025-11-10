// 图片相关类型定义
export interface UploadedImage {
  id: string;
  filename: string;
  url: string;
  size: number;
  dimensions: [number, number];
  upload_time: string;
}

// 图片处理状态
export type ImageProcessingStatus =
  | 'idle'
  | 'uploading'
  | 'analyzing'
  | 'generating'
  | 'completed'
  | 'error';

// 图片分析结果
export interface ImageAnalysisResult {
  image_id: string;
  parameters: Record<string, any>;
  analysis_time: number;
  confidence_score: number;
  suggestions: string[];
  timestamp: string;
}

// 滤镜生成结果
export interface FilterGenerationResult {
  output_image_id: string;
  output_filename: string;
  processing_time: number;
  original_image_id: string;
  preview_url?: string;
  download_url: string;
}

// 图片比较数据
export interface ImageComparison {
  original: UploadedImage;
  filtered: UploadedImage;
  parameters_used: Record<string, number>;
}