import React, { useEffect, useRef, useState } from 'react';

const ImageLandmarks = ({ imageUrl, landmarks, imageDimensions }) => {
  const canvasRef = useRef(null);
  const [debug, setDebug] = useState(false);
  const containerRef = useRef(null);

  useEffect(() => {
    if (!landmarks || !imageUrl || !canvasRef.current) return;

    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    const img = new Image();

    img.onload = () => {
      // Store original image dimensions
      const originalWidth = img.width;
      const originalHeight = img.height;

      // Set canvas size to match the original image dimensions
      canvas.width = originalWidth;
      canvas.height = originalHeight;

      // Clear canvas
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      // Draw image at original size
      ctx.drawImage(img, 0, 0, originalWidth, originalHeight);

      // Style for points
      const pointSize = Math.min(originalWidth, originalHeight) * 0.005; // Relative point size
      ctx.lineWidth = 2;

      // Draw landmarks for each feature
      Object.entries(landmarks).forEach(([feature, points]) => {
        const colors = {
          jawline: '#2563eb',
          right_eyebrow: '#16a34a',
          left_eyebrow: '#16a34a',
          nose_bridge: '#dc2626',
          nose_tip: '#dc2626',
          right_eye: '#4f46e5',
          left_eye: '#4f46e5',
          outer_lips: '#db2777',
          inner_lips: '#db2777'
        };
        ctx.fillStyle = colors[feature] || '#000000';

        // Draw points
        points.forEach(([x, y], index) => {
          // Convert normalized coordinates (0-1) to pixel coordinates
          const canvasX = x * originalWidth;
          const canvasY = y * originalHeight;

          // Draw point
          ctx.beginPath();
          ctx.arc(canvasX, canvasY, pointSize, 0, 2 * Math.PI);
          ctx.fill();

          if (debug) {
            // Add coordinate labels in debug mode
            ctx.fillStyle = 'white';
            ctx.strokeStyle = 'black';
            ctx.lineWidth = 2;
            ctx.font = `${pointSize * 3}px Arial`;
            const label = `${index + 1} (${x.toFixed(2)}, ${y.toFixed(2)})`;
            ctx.strokeText(label, canvasX + pointSize * 2, canvasY + pointSize * 2);
            ctx.fillText(label, canvasX + pointSize * 2, canvasY + pointSize * 2);
            ctx.fillStyle = colors[feature];
          } else {
            // Just show point numbers in normal mode
            ctx.fillStyle = 'white';
            ctx.font = `${pointSize * 3}px Arial`;
            ctx.fillText(index + 1, canvasX + pointSize * 2, canvasY + pointSize * 2);
            ctx.fillStyle = colors[feature];
          }
        });
      });
    };

    img.src = imageUrl;
  }, [imageUrl, landmarks, imageDimensions, debug]);

  return (
    <div className="space-y-4" ref={containerRef}>
      <div className="relative w-full">
        <canvas
          ref={canvasRef}
          className="w-full h-auto rounded-lg"
          style={{ maxHeight: '80vh' }}
        />
      </div>
      
      <div className="flex justify-between items-start">
        <div className="text-sm space-y-2">
          <div className="font-medium">Feature Points Legend:</div>
          <div className="grid grid-cols-2 gap-2">
            {Object.entries(landmarks || {}).map(([feature, points]) => (
              <div key={feature} className="flex items-center gap-2">
                <div 
                  className="w-3 h-3 rounded-full" 
                  style={{ 
                    backgroundColor: {
                      jawline: '#2563eb',
                      right_eyebrow: '#16a34a',
                      left_eyebrow: '#16a34a',
                      nose_bridge: '#dc2626',
                      nose_tip: '#dc2626',
                      right_eye: '#4f46e5',
                      left_eye: '#4f46e5',
                      outer_lips: '#db2777',
                      inner_lips: '#db2777'
                    }[feature]
                  }}
                />
                <span>{feature.replace(/_/g, ' ')} ({points.length} points)</span>
              </div>
            ))}
          </div>
        </div>

        <button
          onClick={() => setDebug(!debug)}
          className="px-3 py-1 text-sm bg-gray-100 hover:bg-gray-200 rounded"
        >
          {debug ? "Hide Debug Info" : "Show Debug Info"}
        </button>
      </div>

      {debug && (
        <div className="text-sm bg-gray-50 p-4 rounded">
          <div className="font-medium mb-2">Debug Information:</div>
          <div>Original Image Dimensions: {imageDimensions.width} x {imageDimensions.height}</div>
          <div>Canvas Dimensions: {canvasRef.current?.width} x {canvasRef.current?.height}</div>
        </div>
      )}
    </div>
  );
};

export default ImageLandmarks;