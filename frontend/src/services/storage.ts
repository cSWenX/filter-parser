import type { ParameterHistory, FilterParameters } from '../types';

// 加密相关工具
const STORAGE_KEY = 'filter_parser_history';
const ENCRYPTION_KEY = 'fp_2023_secret_key'; // 在实际应用中应该更安全

// 简单的加密/解密函数
function simpleEncrypt(text: string): string {
  try {
    return btoa(encodeURIComponent(text));
  } catch {
    return text;
  }
}

function simpleDecrypt(encryptedText: string): string {
  try {
    return decodeURIComponent(atob(encryptedText));
  } catch {
    return encryptedText;
  }
}

class StorageService {
  private maxHistoryCount = 50;

  // 获取所有历史参数
  getParameterHistory(): ParameterHistory[] {
    try {
      const encrypted = localStorage.getItem(STORAGE_KEY);
      if (!encrypted) return [];

      const decrypted = simpleDecrypt(encrypted);
      const history = JSON.parse(decrypted) as ParameterHistory[];

      // 按保存时间倒序排列
      return history.sort((a, b) =>
        new Date(b.saved_time).getTime() - new Date(a.saved_time).getTime()
      );
    } catch (error) {
      console.error('读取历史参数失败:', error);
      return [];
    }
  }

  // 保存参数到历史
  saveParameterHistory(
    name: string,
    parameters: FilterParameters,
    analysisResult?: any
  ): ParameterHistory {
    const history = this.getParameterHistory();

    // 检查是否达到上限
    if (history.length >= this.maxHistoryCount) {
      throw new Error(`历史参数已达上限 ${this.maxHistoryCount} 条，请删除不常用参数后再保存`);
    }

    // 创建新记录
    const newRecord: ParameterHistory = {
      id: `param_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      name: name.trim(),
      parameters,
      saved_time: new Date().toISOString(),
      analysis_result: analysisResult ? {
        confidence_score: analysisResult.confidence_score,
        suggestions: analysisResult.suggestions
      } : undefined
    };

    // 添加到历史记录
    const updatedHistory = [newRecord, ...history];

    // 保存到localStorage
    this.saveToStorage(updatedHistory);

    return newRecord;
  }

  // 删除历史参数
  deleteParameterHistory(id: string): boolean {
    try {
      const history = this.getParameterHistory();
      const filteredHistory = history.filter(item => item.id !== id);

      if (filteredHistory.length === history.length) {
        return false; // 未找到要删除的项
      }

      this.saveToStorage(filteredHistory);
      return true;
    } catch (error) {
      console.error('删除历史参数失败:', error);
      return false;
    }
  }

  // 更新历史参数
  updateParameterHistory(id: string, updates: Partial<ParameterHistory>): boolean {
    try {
      const history = this.getParameterHistory();
      const index = history.findIndex(item => item.id === id);

      if (index === -1) return false;

      history[index] = { ...history[index], ...updates };
      this.saveToStorage(history);
      return true;
    } catch (error) {
      console.error('更新历史参数失败:', error);
      return false;
    }
  }

  // 根据ID获取参数
  getParameterById(id: string): ParameterHistory | null {
    const history = this.getParameterHistory();
    return history.find(item => item.id === id) || null;
  }

  // 清空所有历史参数
  clearAllHistory(): boolean {
    try {
      localStorage.removeItem(STORAGE_KEY);
      return true;
    } catch (error) {
      console.error('清空历史参数失败:', error);
      return false;
    }
  }

  // 导出历史参数为JSON
  exportHistory(): string {
    const history = this.getParameterHistory();
    return JSON.stringify(history, null, 2);
  }

  // 从JSON导入历史参数
  importHistory(jsonData: string): boolean {
    try {
      const importedHistory = JSON.parse(jsonData) as ParameterHistory[];

      // 验证数据格式
      if (!Array.isArray(importedHistory)) {
        throw new Error('导入数据格式不正确');
      }

      // 验证每个记录的必需字段
      for (const record of importedHistory) {
        if (!record.id || !record.name || !record.parameters || !record.saved_time) {
          throw new Error('导入数据包含无效记录');
        }
      }

      // 合并现有历史（避免重复）
      const currentHistory = this.getParameterHistory();
      const mergedHistory = this.mergeHistory(currentHistory, importedHistory);

      // 限制数量
      const finalHistory = mergedHistory.slice(0, this.maxHistoryCount);

      this.saveToStorage(finalHistory);
      return true;
    } catch (error) {
      console.error('导入历史参数失败:', error);
      return false;
    }
  }

  // 获取存储统计信息
  getStorageStats(): {
    count: number;
    maxCount: number;
    usagePercent: number;
    totalSize: number;
  } {
    const history = this.getParameterHistory();
    const encrypted = localStorage.getItem(STORAGE_KEY) || '';

    return {
      count: history.length,
      maxCount: this.maxHistoryCount,
      usagePercent: Math.round((history.length / this.maxHistoryCount) * 100),
      totalSize: new Blob([encrypted]).size
    };
  }

  // 私有方法：保存到localStorage
  private saveToStorage(history: ParameterHistory[]): void {
    try {
      const jsonString = JSON.stringify(history);
      const encrypted = simpleEncrypt(jsonString);
      localStorage.setItem(STORAGE_KEY, encrypted);
    } catch (error) {
      console.error('保存到localStorage失败:', error);
      throw new Error('保存失败，可能是存储空间不足');
    }
  }

  // 私有方法：合并历史记录
  private mergeHistory(current: ParameterHistory[], imported: ParameterHistory[]): ParameterHistory[] {
    const existingIds = new Set(current.map(item => item.id));
    const newRecords = imported.filter(item => !existingIds.has(item.id));

    return [...current, ...newRecords].sort((a, b) =>
      new Date(b.saved_time).getTime() - new Date(a.saved_time).getTime()
    );
  }
}

// 创建单例实例
export const storageService = new StorageService();
export default storageService;