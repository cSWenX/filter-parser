// 参数相关类型定义
export interface ParameterInfo {
  name: string;
  direction: string;
  value: number;
  unit: string;
  reference: string;
}

// 滤镜参数
export interface FilterParameters {
  brightness: number;    // -100 to 100
  contrast: number;      // -100 to 100
  saturation: number;    // -100 to 100
  sharpness: number;     // -100 to 100
  temperature: number;   // -500 to 500
  hue: number;          // -180 to 180
  shadow: number;       // -100 to 100
  highlight: number;    // -100 to 100
}

// 历史参数记录
export interface ParameterHistory {
  id: string;
  name: string;
  parameters: FilterParameters;
  saved_time: string;
  analysis_result?: {
    confidence_score: number;
    suggestions: string[];
  };
}

// 参数范围定义
export interface ParameterRange {
  min: number;
  max: number;
  step: number;
  unit: string;
}

export const PARAMETER_RANGES: Record<keyof FilterParameters, ParameterRange> = {
  brightness: { min: -100, max: 100, step: 1, unit: '%' },
  contrast: { min: -100, max: 100, step: 1, unit: '%' },
  saturation: { min: -100, max: 100, step: 1, unit: '%' },
  sharpness: { min: -100, max: 100, step: 1, unit: '%' },
  temperature: { min: -500, max: 500, step: 10, unit: 'K' },
  hue: { min: -180, max: 180, step: 1, unit: '°' },
  shadow: { min: -100, max: 100, step: 1, unit: '%' },
  highlight: { min: -100, max: 100, step: 1, unit: '%' }
};

// 参数显示名称
export const PARAMETER_LABELS: Record<keyof FilterParameters, string> = {
  brightness: '亮度',
  contrast: '对比度',
  saturation: '饱和度',
  sharpness: '锐化',
  temperature: '色温',
  hue: '色调',
  shadow: '阴影',
  highlight: '高光'
};