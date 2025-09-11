import React from 'react';

interface SlideTemplateProps {
  title?: string;
  backgroundColor?: string;
  children: React.ReactNode;
  showTitle?: boolean;
}

const SlideTemplate: React.FC<SlideTemplateProps> = ({ 
  title, 
  backgroundColor = 'bg-gradient-to-br from-gray-50 to-gray-100',
  children,
  showTitle = true
}) => {
  return (
    <div className={`h-full flex flex-col px-24 py-12 ${backgroundColor}`}>
      {showTitle && title && (
        <h2 className="text-5xl font-bold text-gray-900 mb-12 text-center">
          {title}
        </h2>
      )}
      <div className={showTitle && title ? 'flex-1 flex flex-col justify-center' : 'h-full'}>
        {children}
      </div>
    </div>
  );
};

export default SlideTemplate;