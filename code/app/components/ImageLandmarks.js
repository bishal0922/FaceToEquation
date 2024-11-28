import React, { useEffect, useRef } from 'react';

const ImageLandmarks = ({ imageUrl, landmarks, imageDimensions }) => {
  const canvasRef = useRef(null);

  useEffect(() => {
    if (!landmarks || !imageUrl || !canvasRef.current) return;

    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    const img = new Image();

    img.onload = () => {
      // Set canvas size to match image
      canvas.width = imageDimensions.width;
      canvas.height = imageDimensions.height;

      // Draw image
      ctx.drawImage(img, 0, 0, canvas.width, canvas.height);

      // Style for points and lines
      ctx.lineWidth = 2;

      // Draw landmarks for each feature
      Object.entries(landmarks).forEach(([feature, points]) => {
        // Set color based on feature
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
        ctx.strokeStyle = colors[feature] || '#000000';
        ctx.fillStyle = colors[feature] || '#000000';

        // Draw points and lines
        ctx.beginPath();
        points.forEach(([x, y], index) => {
          const canvasX = x * canvas.width;
          const canvasY = y * canvas.height;

          // Draw point
          ctx.fillRect(canvasX - 2, canvasY - 2, 4, 4);

          // Connect points with lines
          if (index === 0) {
            ctx.moveTo(canvasX, canvasY);
          } else {
            ctx.lineTo(canvasX, canvasY);
          }
        });

        // Close the path for closed features
        if (['right_eye', 'left_eye', 'outer_lips', 'inner_lips'].includes(feature)) {
          ctx.closePath();
        }
        ctx.stroke();
      });
    };

    img.src = imageUrl;
  }, [imageUrl, landmarks, imageDimensions]);

  return (
    <div className="relative w-full">
      <canvas
        ref={canvasRef}
        className="w-full h-auto rounded-lg"
      />
    </div>
  );
};

export default ImageLandmarks;