import React, { useState } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, ResponsiveContainer } from 'recharts';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription } from '@/components/ui/alert';

const FaceVisualizer = ({ faceData }) => {
  const [showPoints, setShowPoints] = useState(true);
  const [showCurves, setShowCurves] = useState(true);

  if (!faceData?.landmarks || !faceData?.equations) {
    return (
      <Alert>
        <AlertDescription>No face data available to visualize</AlertDescription>
      </Alert>
    );
  }

  // Generate points for each feature's equation
  const generateEquationPoints = (coefficients, numPoints = 50) => {
    const points = [];
    for (let i = 0; i <= numPoints; i++) {
      const x = i / numPoints;
      let y = 0;
      // Evaluate polynomial
      coefficients.forEach((coeff, power) => {
        y += coeff * Math.pow(x, coefficients.length - 1 - power);
      });
      points.push({ x, y, type: 'curve' });
    }
    return points;
  };

  // Prepare data for all facial features
  const allFeatureData = Object.entries(faceData.landmarks).map(([feature, points]) => {
    const equation = faceData.equations[feature];
    const curvePoints = generateEquationPoints(equation.coefficients);
    const originalPoints = points.map(([x, y]) => ({ x, y, type: 'point' }));
    
    return {
      feature,
      data: [...(showCurves ? curvePoints : []), ...(showPoints ? originalPoints : [])],
      color: getFeatureColor(feature)
    };
  });

  // Get color based on facial feature
  function getFeatureColor(feature) {
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
    return colors[feature] || '#000000';
  }

  return (
    <div className="bg-white rounded-xl shadow-lg p-6 space-y-4">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-gray-900">Face Visualization</h2>
        <div className="flex gap-2">
          <Button
            variant={showPoints ? "default" : "outline"}
            onClick={() => setShowPoints(!showPoints)}
          >
            {showPoints ? "Hide Points" : "Show Points"}
          </Button>
          <Button
            variant={showCurves ? "default" : "outline"}
            onClick={() => setShowCurves(!showCurves)}
          >
            {showCurves ? "Hide Curves" : "Show Curves"}
          </Button>
        </div>
      </div>

      <div className="h-96 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart margin={{ top: 20, right: 20, bottom: 20, left: 20 }}>
            <CartesianGrid strokeDasharray="3 3" opacity={0.3} />
            <XAxis
              dataKey="x"
              type="number"
              domain={[0, 1]}
              tickFormatter={(value) => value.toFixed(1)}
            />
            <YAxis
              type="number"
              domain={[0, 1]}
              tickFormatter={(value) => value.toFixed(1)}
              reversed={true}
            />
            {allFeatureData.map(({ feature, data, color }) => (
              <Line
                key={feature}
                data={data}
                type={feature.includes('eye') ? 'linear' : 'monotone'}
                dataKey="y"
                stroke={color}
                strokeWidth={2}
                dot={showPoints ? { r: 3, fill: color } : false}
                isAnimationActive={false}
                connectNulls={true}
              />
            ))}
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

export default FaceVisualizer;