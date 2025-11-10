import type { FilterParameters } from '../types';

// 工具函数集合
export class Utils {
  // 生成唯一ID
  static generateId(prefix = ''): string {
    const timestamp = Date.now().toString(36);
    const random = Math.random().toString(36).substr(2, 5);
    return `${prefix}${prefix ? '_' : ''}${timestamp}_${random}`;
  }

  // 格式化文件大小
  static formatFileSize(bytes: number): string {
    if (bytes === 0) return '0 B';

    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));

    return `${parseFloat((bytes / Math.pow(k, i)).toFixed(1))} ${sizes[i]}`;
  }

  // 格式化时间
  static formatTime(isoString: string): string {
    const date = new Date(isoString);
    const now = new Date();
    const diff = now.getTime() - date.getTime();

    // 少于1分钟
    if (diff < 60000) {
      return '刚刚';
    }

    // 少于1小时
    if (diff < 3600000) {
      const minutes = Math.floor(diff / 60000);
      return `${minutes}分钟前`;
    }

    // 少于24小时
    if (diff < 86400000) {
      const hours = Math.floor(diff / 3600000);
      return `${hours}小时前`;
    }

    // 少于7天
    if (diff < 604800000) {
      const days = Math.floor(diff / 86400000);
      return `${days}天前`;
    }

    // 超过7天显示具体日期
    return date.toLocaleDateString('zh-CN', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  }

  // 验证参数名称
  static validateParameterName(name: string): { valid: boolean; message?: string } {
    const trimmedName = name.trim();

    if (!trimmedName) {
      return { valid: false, message: '参数名称不能为空' };
    }

    if (trimmedName.length > 20) {
      return { valid: false, message: '参数名称不能超过20个字符' };
    }

    // 检查是否只包含中英文、数字、下划线
    const pattern = /^[\u4e00-\u9fa5a-zA-Z0-9_]+$/;
    if (!pattern.test(trimmedName)) {
      return { valid: false, message: '参数名称只能包含中英文、数字、下划线' };
    }

    return { valid: true };
  }

  // 验证滤镜参数范围
  static validateFilterParameters(params: FilterParameters): { valid: boolean; errors: string[] } {
    const errors: string[] = [];

    const ranges = {
      brightness: { min: -100, max: 100, name: '亮度' },
      contrast: { min: -100, max: 100, name: '对比度' },
      saturation: { min: -100, max: 100, name: '饱和度' },
      sharpness: { min: -100, max: 100, name: '锐化' },
      temperature: { min: -500, max: 500, name: '色温' },
      hue: { min: -180, max: 180, name: '色调' },
      shadow: { min: -100, max: 100, name: '阴影' },
      highlight: { min: -100, max: 100, name: '高光' }
    };

    for (const [key, value] of Object.entries(params)) {
      const range = ranges[key as keyof typeof ranges];
      if (range && (value < range.min || value > range.max)) {
        errors.push(`${range.name}参数超出范围 (${range.min} ~ ${range.max})`);
      }
    }

    return { valid: errors.length === 0, errors };
  }

  // 深度复制对象
  static deepClone<T>(obj: T): T {
    if (obj === null || typeof obj !== 'object') return obj;
    if (obj instanceof Date) return new Date(obj.getTime()) as any;
    if (obj instanceof Array) return obj.map(item => Utils.deepClone(item)) as any;

    const cloned = {} as T;
    for (const key in obj) {
      if (obj.hasOwnProperty(key)) {
        cloned[key] = Utils.deepClone(obj[key]);
      }
    }
    return cloned;
  }

  // 防抖函数
  static debounce<T extends (...args: any[]) => any>(
    func: T,
    wait: number
  ): (...args: Parameters<T>) => void {
    let timeout: ReturnType<typeof setTimeout>;
    return (...args: Parameters<T>) => {
      clearTimeout(timeout);
      timeout = setTimeout(() => func.apply(this, args), wait);
    };
  }

  // 下载文件
  static downloadFile(url: string, filename: string): void {
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  }

  // 下载文本内容
  static downloadText(content: string, filename: string, mimeType = 'text/plain'): void {
    const blob = new Blob([content], { type: mimeType });
    const url = URL.createObjectURL(blob);
    Utils.downloadFile(url, filename);
    URL.revokeObjectURL(url);
  }

  // 计算图片显示尺寸（保持宽高比）
  static calculateDisplaySize(
    originalWidth: number,
    originalHeight: number,
    maxWidth: number,
    maxHeight: number
  ): { width: number; height: number } {
    const aspectRatio = originalWidth / originalHeight;

    let width = originalWidth;
    let height = originalHeight;

    if (width > maxWidth) {
      width = maxWidth;
      height = width / aspectRatio;
    }

    if (height > maxHeight) {
      height = maxHeight;
      width = height * aspectRatio;
    }

    return {
      width: Math.round(width),
      height: Math.round(height)
    };
  }

  // 获取参数变化摘要
  static getParameterSummary(params: FilterParameters): string {
    const significantChanges: string[] = [];

    for (const [key, value] of Object.entries(params)) {
      if (Math.abs(value) >= 5) { // 只显示显著变化
        const paramNames: Record<string, string> = {
          brightness: '亮度',
          contrast: '对比度',
          saturation: '饱和度',
          sharpness: '锐化',
          temperature: '色温',
          hue: '色调',
          shadow: '阴影',
          highlight: '高光'
        };

        const name = paramNames[key] || key;
        const sign = value > 0 ? '+' : '';
        significantChanges.push(`${name}${sign}${value}`);
      }
    }

    return significantChanges.length > 0
      ? significantChanges.join(', ')
      : '无显著调整';
  }

  // 合并类名 (简化版clsx)
  static cn(...classes: (string | undefined | null | false)[]): string {
    return classes.filter(Boolean).join(' ');
  }
}

export default Utils;