// API响应类型定义
export interface ApiResponse<T = any> {
  status: 'success' | 'error' | 'warning';
  message: string;
  data?: T;
  error_code?: string;
}

// 上传响应
export interface UploadResponse {
  image_id: string;
  filename: string;
  file_size: number;
  dimensions: [number, number];
  message: string;
}

// 分析响应
export interface AnalysisResponse {
  image_id: string;
  parameters: Record<string, any>;
  analysis_time: number;
  confidence_score: number;
  suggestions: string[];
  message: string;
}

// 生成响应
export interface GenerationResponse {
  output_image_id: string;
  output_filename: string;
  processing_time: number;
  original_image_id: string;
  applied_parameters: Record<string, number>;
  message: string;
}

// 健康检查响应
export interface HealthResponse {
  status: string;
  upload_folder_size_mb: number;
  output_folder_size_mb: number;
  upload_files_count: number;
  output_files_count: number;
}