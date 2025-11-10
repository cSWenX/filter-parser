import { create } from 'zustand';
import type {
  UploadedImage,
  ImageProcessingStatus,
  ImageAnalysisResult,
  FilterGenerationResult,
  ParameterHistory,
  FilterParameters
} from '../types';

interface AppState {
  // 图片状态
  currentImage: UploadedImage | null;
  processingStatus: ImageProcessingStatus;

  // 分析结果
  analysisResult: ImageAnalysisResult | null;

  // 滤镜生成
  generationResult: FilterGenerationResult | null;

  // 历史参数
  parameterHistory: ParameterHistory[];

  // UI状态
  isLoading: boolean;
  error: string | null;

  // 操作方法
  setCurrentImage: (image: UploadedImage | null) => void;
  setProcessingStatus: (status: ImageProcessingStatus) => void;
  setAnalysisResult: (result: ImageAnalysisResult | null) => void;
  setGenerationResult: (result: FilterGenerationResult | null) => void;
  setParameterHistory: (history: ParameterHistory[]) => void;
  addParameterHistory: (item: ParameterHistory) => void;
  removeParameterHistory: (id: string) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;

  // 重置状态
  reset: () => void;
  resetResults: () => void;
}

export const useAppStore = create<AppState>((set, get) => ({
  // 初始状态
  currentImage: null,
  processingStatus: 'idle',
  analysisResult: null,
  generationResult: null,
  parameterHistory: [],
  isLoading: false,
  error: null,

  // 设置当前图片
  setCurrentImage: (image) => set({
    currentImage: image,
    processingStatus: image ? 'idle' : 'idle',
    error: null
  }),

  // 设置处理状态
  setProcessingStatus: (status) => set({
    processingStatus: status,
    isLoading: status === 'uploading' || status === 'analyzing' || status === 'generating'
  }),

  // 设置分析结果
  setAnalysisResult: (result) => set({
    analysisResult: result,
    processingStatus: result ? 'completed' : 'idle'
  }),

  // 设置生成结果
  setGenerationResult: (result) => set({
    generationResult: result,
    processingStatus: result ? 'completed' : 'idle'
  }),

  // 设置历史参数
  setParameterHistory: (history) => set({ parameterHistory: history }),

  // 添加历史参数
  addParameterHistory: (item) => set((state) => ({
    parameterHistory: [item, ...state.parameterHistory]
  })),

  // 删除历史参数
  removeParameterHistory: (id) => set((state) => ({
    parameterHistory: state.parameterHistory.filter(item => item.id !== id)
  })),

  // 设置加载状态
  setLoading: (loading) => set({ isLoading: loading }),

  // 设置错误信息
  setError: (error) => set({ error }),

  // 重置所有状态
  reset: () => set({
    currentImage: null,
    processingStatus: 'idle',
    analysisResult: null,
    generationResult: null,
    isLoading: false,
    error: null
  }),

  // 重置结果状态
  resetResults: () => set({
    analysisResult: null,
    generationResult: null,
    processingStatus: 'idle',
    error: null
  })
}));