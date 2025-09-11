import React, { useState } from 'react';
import { Image } from 'lucide-react';
import schematicUrls from '../data/testbenches/schematics';

interface TestbenchSchematicProps {
  schematicPath: string;
  altText: string;
}

const TestbenchSchematic: React.FC<TestbenchSchematicProps> = ({ schematicPath, altText }) => {
  const [imageError, setImageError] = useState(false);
  const [imageLoaded, setImageLoaded] = useState(false);
  
  // Reset error state when schematicPath changes
  React.useEffect(() => {
    setImageError(false);
    setImageLoaded(false);
  }, [schematicPath]);

  // Check if we have the SVG URL in our imported schematics
  const svgUrl = schematicUrls[schematicPath];

  // If we have SVG URL from imports, display it as an image
  if (svgUrl) {
    return (
      <div className="relative w-full aspect-[4/3] bg-gray-50 rounded-lg overflow-hidden flex items-center justify-center">
        {!imageLoaded && (
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="text-gray-400">
              <svg className="w-12 h-12 animate-pulse" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
          </div>
        )}
        <img 
          src={svgUrl}
          alt={altText}
          className="w-full h-full object-contain p-4"
          style={{ maxWidth: '100%', maxHeight: '100%' }}
          onLoad={() => setImageLoaded(true)}
        />
      </div>
    );
  }

  // For PNG/JPG images (fallback for external images)
  if (schematicPath.endsWith('.png') || schematicPath.endsWith('.jpg') || schematicPath.endsWith('.jpeg')) {
    if (imageError) {
      return (
        <div className="relative w-full aspect-[4/3] bg-gray-50 rounded-lg overflow-hidden flex items-center justify-center">
          <div className="flex items-center justify-center flex-col text-gray-400">
            <svg className="w-24 h-24 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
            <p className="text-sm text-center">Image not available</p>
          </div>
        </div>
      );
    }

    return (
      <div className="relative w-full aspect-[4/3] bg-gray-50 rounded-lg overflow-hidden flex items-center justify-center">
        {!imageLoaded && (
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="text-gray-400">
              <svg className="w-12 h-12 animate-pulse" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
          </div>
        )}
        <img 
          src={`/src/data/testbenches/${schematicPath}`}
          alt={altText}
          className="w-full h-full object-contain p-4"
          style={{ maxWidth: '100%', maxHeight: '100%' }}
          onError={() => setImageError(true)}
          onLoad={() => setImageLoaded(true)}
        />
      </div>
    );
  }

  // Fallback for missing schematics
  return (
    <div className="relative w-full aspect-[4/3] bg-gray-50 rounded-lg overflow-hidden flex items-center justify-center">
      <div className="flex items-center justify-center flex-col text-gray-400">
        <Image className="w-24 h-24 mb-2" />
        <p className="text-sm text-center">
          Schematic not available
          <br />
          <span className="text-xs">{schematicPath}</span>
        </p>
      </div>
    </div>
  );
};

export default TestbenchSchematic;