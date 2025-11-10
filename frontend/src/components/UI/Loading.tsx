import React from 'react';
import { Loader2 } from 'lucide-react';
import { Utils } from '../../services';

interface LoadingProps {
  size?: 'sm' | 'md' | 'lg';
  text?: string;
  className?: string;
}

const Loading: React.FC<LoadingProps> = ({
  size = 'md',
  text,
  className = ''
}) => {
  const sizeClasses = {
    sm: 'w-4 h-4',
    md: 'w-6 h-6',
    lg: 'w-8 h-8'
  };

  const textSizeClasses = {
    sm: 'text-sm',
    md: 'text-base',
    lg: 'text-lg'
  };

  return (
    <div className={Utils.cn('flex flex-col items-center justify-center gap-3', className)}>
      <Loader2 className={Utils.cn('animate-spin text-primary-500', sizeClasses[size])} />
      {text && (
        <p className={Utils.cn('text-gray-600', textSizeClasses[size])}>
          {text}
        </p>
      )}
    </div>
  );
};

export default Loading;