import React, { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, Image as ImageIcon, X } from 'lucide-react';
import { Button, Loading } from '../UI';
import { Utils } from '../../services';
import { useAppStore } from '../../store/useAppStore';

interface ImageUploadProps {
  onUpload: (file: File) => void;
  className?: string;
}

const ImageUpload: React.FC<ImageUploadProps> = ({ onUpload, className = '' }) => {
  const {
    currentImage,
    processingStatus,
    setCurrentImage,
    setError
  } = useAppStore();

  const onDrop = useCallback((acceptedFiles: File[]) => {
    const file = acceptedFiles[0];
    if (file) {
      // 验证文件大小 (16MB限制)
      if (file.size > 16 * 1024 * 1024) {
        setError('文件大小不能超过16MB');
        return;
      }

      // 验证文件类型
      const validTypes = ['image/jpeg', 'image/png', 'image/webp'];
      if (!validTypes.includes(file.type)) {
        setError('仅支持 JPG、PNG、WEBP 格式的图片');
        return;
      }

      setError(null);
      onUpload(file);
    }
  }, [onUpload, setError]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.jpeg', '.jpg', '.png', '.webp']
    },
    multiple: false,
    disabled: processingStatus === 'uploading'
  });

  const handleRemoveImage = () => {
    setCurrentImage(null);
  };

  const isUploading = processingStatus === 'uploading';
  const hasImage = currentImage !== null;

  return (
    <div className={Utils.cn('space-y-4', className)}>
      {/* 上传区域 */}
      {!hasImage && (
        <div
          {...getRootProps()}
          className={Utils.cn(
            'border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors',
            isDragActive
              ? 'border-primary-500 bg-primary-50'
              : 'border-gray-300 hover:border-gray-400',
            isUploading && 'pointer-events-none opacity-50'
          )}
        >
          <input {...getInputProps()} />

          {isUploading ? (
            <Loading size="lg" text="正在上传图片..." />
          ) : (
            <div className="space-y-4">
              <div className="mx-auto w-16 h-16 text-gray-400">
                <Upload className="w-full h-full" />
              </div>

              <div className="space-y-2">
                <p className="text-lg font-medium text-gray-700">
                  {isDragActive ? '松开鼠标上传图片' : '拖拽图片到此处，或点击上传'}
                </p>
                <p className="text-sm text-gray-500">
                  支持 JPG、PNG、WEBP 格式，最大 16MB
                </p>
              </div>

              <Button variant="outline" size="lg">
                选择图片文件
              </Button>
            </div>
          )}
        </div>
      )}

      {/* 图片预览 */}
      {hasImage && (
        <div className="space-y-4">
          <div className="relative bg-gray-50 rounded-lg p-4">
            <button
              onClick={handleRemoveImage}
              className="absolute top-2 right-2 p-1 bg-red-500 text-white rounded-full hover:bg-red-600 transition-colors z-10"
              disabled={isUploading}
            >
              <X className="w-4 h-4" />
            </button>

            <div className="flex items-center space-x-4">
              <div className="flex-shrink-0">
                <ImageIcon className="w-12 h-12 text-gray-400" />
              </div>

              <div className="flex-1 min-w-0">
                <h3 className="text-lg font-medium text-gray-900 truncate">
                  {currentImage.filename}
                </h3>
                <div className="text-sm text-gray-500 space-y-1">
                  <p>
                    尺寸: {currentImage.dimensions[0]} × {currentImage.dimensions[1]}
                  </p>
                  <p>
                    大小: {Utils.formatFileSize(currentImage.size)}
                  </p>
                </div>
              </div>
            </div>

            {processingStatus === 'analyzing' && (
              <div className="mt-4 pt-4 border-t border-gray-200">
                <Loading size="sm" text="正在分析参数..." />
              </div>
            )}
          </div>

          {/* 重新上传按钮 */}
          <div className="text-center">
            <Button
              variant="outline"
              onClick={() => setCurrentImage(null)}
              disabled={isUploading || processingStatus === 'analyzing'}
            >
              重新选择图片
            </Button>
          </div>
        </div>
      )}
    </div>
  );
};

export default ImageUpload;