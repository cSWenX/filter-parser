import React, { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, Image as ImageIcon, X } from 'lucide-react';
import { Button, Loading } from '../UI';
import { Utils } from '../../services';

interface ImageUploadProps {
  onUpload: (file: File) => void;
  isUploading?: boolean;
  currentImage?: {
    filename: string;
    size: number;
    dimensions: [number, number];
  } | null;
  onRemoveImage?: () => void;
  className?: string;
  title?: string;
  description?: string;
}

const ImageUpload: React.FC<ImageUploadProps> = ({
  onUpload,
  isUploading = false,
  currentImage,
  onRemoveImage,
  className = '',
  title = '上传图片',
  description = '拖拽图片到此处，或点击上传'
}) => {
  const onDrop = useCallback((acceptedFiles: File[]) => {
    const file = acceptedFiles[0];
    if (file) {
      // 验证文件大小 (16MB限制)
      if (file.size > 16 * 1024 * 1024) {
        console.error('文件大小不能超过16MB');
        return;
      }

      // 验证文件类型
      const validTypes = ['image/jpeg', 'image/png', 'image/webp'];
      if (!validTypes.includes(file.type)) {
        console.error('仅支持 JPG、PNG、WEBP 格式的图片');
        return;
      }

      onUpload(file);
    }
  }, [onUpload]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.jpeg', '.jpg', '.png', '.webp']
    },
    multiple: false,
    disabled: isUploading
  });

  if (currentImage && !isUploading) {
    return (
      <div className={Utils.cn('space-y-4', className)}>
        <div className="relative bg-gray-50 rounded-lg p-4 border border-gray-200">
          {onRemoveImage && (
            <button
              onClick={onRemoveImage}
              className="absolute top-2 right-2 p-1 bg-red-500 text-white rounded-full hover:bg-red-600 transition-colors z-10"
            >
              <X className="w-4 h-4" />
            </button>
          )}

          <div className="flex items-center space-x-4">
            <div className="flex-shrink-0">
              <ImageIcon className="w-12 h-12 text-gray-400" />
            </div>

            <div className="flex-1 min-w-0">
              <h4 className="text-base font-medium text-gray-900 truncate">
                {currentImage.filename}
              </h4>
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
        </div>

        {/* 重新上传按钮 */}
        {onRemoveImage && (
          <div className="text-center">
            <Button
              variant="outline"
              onClick={onRemoveImage}
              size="sm"
            >
              重新选择图片
            </Button>
          </div>
        )}
      </div>
    );
  }

  return (
    <div className={Utils.cn('space-y-4', className)}>
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
                {isDragActive ? '松开鼠标上传图片' : title}
              </p>
              <p className="text-sm text-gray-500">
                {description}
              </p>
              <p className="text-xs text-gray-400">
                支持 JPG、PNG、WEBP 格式，最大 16MB
              </p>
            </div>

            <Button variant="outline" size="lg">
              选择图片文件
            </Button>
          </div>
        )}
      </div>
    </div>
  );
};

export default ImageUpload;