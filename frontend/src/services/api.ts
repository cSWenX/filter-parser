import axios, { AxiosInstance, AxiosResponse } from 'axios';
import type {
  ApiResponse,
  UploadResponse,
  AnalysisResponse,
  GenerationResponse,
  HealthResponse,
  FilterParameters,
  ParameterHistory
} from '../types';

class ApiService {
  private client: AxiosInstance;

  constructor() {
    // 自动检测API基础URL
    const getApiBaseURL = () => {
      // 从环境变量获取
      if (import.meta.env.VITE_API_BASE_URL) {
        return import.meta.env.VITE_API_BASE_URL;
      }

      // 如果是本地开发环境
      if (import.meta.env.DEV) {
        return 'http://localhost:8080/api';
      }

      // 如果是生产环境，使用相对路径
      const currentOrigin = window.location.origin;
      return `${currentOrigin}/api`;
    };

    const baseURL = getApiBaseURL();
    console.log('API Base URL:', baseURL);

    this.client = axios.create({
      baseURL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // 请求拦截器
    this.client.interceptors.request.use(
      (config) => {
        console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`);
        return config;
      },
      (error) => {
        console.error('API Request Error:', error);
        return Promise.reject(error);
      }
    );

    // 响应拦截器
    this.client.interceptors.response.use(
      (response: AxiosResponse<ApiResponse>) => {
        console.log(`API Response: ${response.config.url}`, response.data);
        return response;
      },
      (error) => {
        console.error('API Response Error:', error);

        // 统一错误处理
        if (error.response?.data?.message) {
          throw new Error(error.response.data.message);
        }

        if (error.code === 'ECONNABORTED') {
          throw new Error('请求超时，请稍后重试');
        }

        if (!error.response) {
          throw new Error('网络连接失败，请检查网络状态');
        }

        throw new Error(error.message || '请求失败');
      }
    );
  }

  // 健康检查
  async healthCheck(): Promise<HealthResponse> {
    const response = await this.client.get<ApiResponse<HealthResponse>>('/health');
    return response.data.data!;
  }

  // 上传图片
  async uploadImage(file: File): Promise<UploadResponse> {
    const formData = new FormData();
    formData.append('image', file);

    const response = await this.client.post<ApiResponse<UploadResponse>>(
      '/upload',
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        timeout: 60000, // 上传超时时间延长
      }
    );

    return response.data.data!;
  }

  // 获取上传状态
  async getUploadStatus(imageId: string): Promise<any> {
    const response = await this.client.get<ApiResponse>(`/upload/status/${imageId}`);
    return response.data.data;
  }

  // 分析图片参数
  async analyzeImage(imageId: string): Promise<AnalysisResponse> {
    const response = await this.client.get<ApiResponse<AnalysisResponse>>(
      `/analyze/${imageId}`
    );
    return response.data.data!;
  }

  // 批量分析图片
  async analyzeBatch(imageIds: string[]): Promise<any> {
    const response = await this.client.post<ApiResponse>('/analyze/batch', {
      image_ids: imageIds,
    });
    return response.data.data;
  }

  // 生成滤镜图片
  async generateFilter(
    originalImageId: string,
    parameters: FilterParameters
  ): Promise<GenerationResponse> {
    const response = await this.client.post<ApiResponse<GenerationResponse>>(
      '/generate',
      {
        original_image_id: originalImageId,
        parameters,
      },
      {
        timeout: 60000, // 生成超时时间延长
      }
    );
    return response.data.data!;
  }

  // 下载滤镜图片
  getDownloadUrl(outputImageId: string): string {
    return `${this.client.defaults.baseURL}/download/${outputImageId}`;
  }

  // 生成滤镜预览
  async generatePreview(
    originalImageId: string,
    parameters: FilterParameters
  ): Promise<string> {
    const response = await this.client.post<ApiResponse<{ preview_base64: string }>>(
      '/preview',
      {
        original_image_id: originalImageId,
        parameters,
      }
    );
    return response.data.data!.preview_base64;
  }

  // 手动清理文件
  async manualCleanup(): Promise<any> {
    const response = await this.client.post<ApiResponse>('/cleanup');
    return response.data.data;
  }

  // ======================== 滤镜管理 API ========================

  // 获取所有保存的滤镜
  async getFilters(): Promise<{ filters: ParameterHistory[]; total: number }> {
    const response = await this.client.get<ApiResponse<{ filters: ParameterHistory[]; total: number }>>('/filters');
    return response.data.data!;
  }

  // 保存新滤镜
  async saveFilter(data: {
    name: string;
    parameters: FilterParameters;
    analysis_result?: any;
  }): Promise<{ filter_id: string; name: string; saved_time: string }> {
    const response = await this.client.post<ApiResponse<{
      filter_id: string;
      name: string;
      saved_time: string;
    }>>('/filters', data);
    return response.data.data!;
  }

  // 获取单个滤镜详情
  async getFilter(filterId: string): Promise<ParameterHistory> {
    const response = await this.client.get<ApiResponse<ParameterHistory>>(`/filters/${filterId}`);
    return response.data.data!;
  }

  // 更新滤镜信息
  async updateFilter(filterId: string, data: {
    name?: string;
    parameters?: FilterParameters;
    analysis_result?: any;
  }): Promise<{ filter_id: string; updated_time: string }> {
    const response = await this.client.put<ApiResponse<{
      filter_id: string;
      updated_time: string;
    }>>(`/filters/${filterId}`, data);
    return response.data.data!;
  }

  // 删除滤镜
  async deleteFilter(filterId: string): Promise<{ filter_id: string; deleted_time: string }> {
    const response = await this.client.delete<ApiResponse<{
      filter_id: string;
      deleted_time: string;
    }>>(`/filters/${filterId}`);
    return response.data.data!;
  }

  // 应用滤镜到图片
  async applyFilter(imageId: string, parameters: FilterParameters): Promise<{
    output_image_id: string;
    output_filename: string;
    processing_time: number;
    download_url: string;
    applied_parameters: FilterParameters;
  }> {
    const response = await this.client.post<ApiResponse<{
      output_image_id: string;
      output_filename: string;
      processing_time: number;
      download_url: string;
      applied_parameters: FilterParameters;
    }>>('/apply-filter', {
      image_id: imageId,
      parameters
    }, {
      timeout: 60000, // 应用滤镜超时时间延长
    });
    return response.data.data!;
  }

  // 获取下载链接
  async getDownloadLink(filename: string): Promise<{
    download_url: string;
    filename: string;
    expires_at: string;
  }> {
    const response = await this.client.get<ApiResponse<{
      download_url: string;
      filename: string;
      expires_at: string;
    }>>(`/download/${filename}`);
    return response.data.data!;
  }
}

// 创建单例实例
export const apiService = new ApiService();
export default apiService;