import React, { useState, useCallback, useMemo } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, ResponsiveContainer, Tooltip } from 'recharts';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Button } from '@/components/ui/button';

const EnhancedFaceVisualizer = ({ faceData }) => {
  const [showPoints, setShowPoints] = useState(true);
  const [showCurves, setShowCurves] = useState(true);
  const [selectedFeature, setSelectedFeature] = useState(null);

  const evaluateBezierCurve = useCallback((controlPoints, numPoints = 50) => {
    const points = [];
    for (let t = 0; t <= 1; t += 1/numPoints) {
      let x = 0;
      let y = 0;
      const n = controlPoints.length - 1;
      
      for (let i = 0; i <= n; i++) {
        const binomial = (n, k)=> {
          if (k === 0 || k === n) return 1;
          if (k > n) return 0;
          return binomial(n - 1, k - 1) + binomial(n - 1, k);
        };
        
        const b = binomial(n, i) * Math.pow(t, i) * Math.pow(1 - t, n - i);
        x += controlPoints[i][0] * b;
        y += controlPoints[i][1] * b;
      }
      
      points.push({ x, y });
    }
    return points;
  }, []);

  const generateFeaturePoints = useCallback((feature, equation) => {
    const points = [];
    
    switch (equation.type) {
      case 'piecewise_spline':
        // Handle jawline with natural cubic splines
        ['left', 'right'].forEach(side => {
          const spline = equation.segments[side];
          const t = Array.from({ length: 50 }, (_, i) => i / 49);
          t.forEach(t => {
            const x = spline.coefficients[0].reduce((sum, c, i) => 
              sum + c * Math.pow(t, spline.degree - i), 0);
            const y = spline.coefficients[1].reduce((sum, c, i) => 
              sum + c * Math.pow(t, spline.degree - i), 0);
            points.push({ x, y, type: 'curve', feature });
          });
        });
        break;

      case 'parametric_eye':
        // Handle eyes with parametric equations
        const { center, parameters: { a, b, theta } } = equation;
        for (let t = 0; t <= 2 * Math.PI; t += 0.1) {
          const x = center[0] + a * Math.cos(t) * Math.cos(theta) - 
                   b * Math.sin(t) * Math.sin(theta);
          const y = center[1] + a * Math.cos(t) * Math.sin(theta) + 
                   b * Math.sin(t) * Math.cos(theta);
          points.push({ x, y, type: 'curve', feature });
        }
        break;

      case 'composite_lips':
        // Handle lips with Cupid's bow
        if (equation.cupids_bow) {
          ['left', 'right'].forEach(side => {
            const segment = equation.cupids_bow.segments[side];
            const controlPoints = [
              segment.start,
              segment.control,
              segment.end
            ];
            evaluateBezierCurve(controlPoints).forEach(point => 
              points.push({ ...point, type: 'curve', feature }));
          });
        }
        
        ['upper', 'lower'].forEach(part => {
          const curve = equation.curves[part];
          evaluateBezierCurve(curve.control_points).forEach(point =>
            points.push({ ...point, type: 'curve', feature }));
        });
        break;

      case 'hermite_spline':
        // Handle nose bridge with Hermite spline
        const { parameters } = equation;
        const y_vals = parameters.x;
        const coeffs = parameters.c;
        
        for (let i = 0; i < y_vals.length - 1; i++) {
          const y0 = y_vals[i];
          const y1 = y_vals[i + 1];
          
          for (let t = 0; t <= 1; t += 0.05) {
            const y = y0 + t * (y1 - y0);
            const x = coeffs.slice(0, 4).reduce((sum, c, j) => 
              sum + c * Math.pow(t, 3 - j), 0);
            points.push({ x, y, type: 'curve', feature });
          }
        }
        break;

      default:
        console.warn(`Unknown equation type: ${equation.type}`);
    }
    
    return points;
  }, [evaluateBezierCurve]);

  const allFeatureData = useMemo(() => {
    if (!faceData?.landmarks || !faceData?.equations) return [];
    
    return Object.entries(faceData.equations).flatMap(([feature, equation]) => {
      const curvePoints = showCurves ? generateFeaturePoints(feature, equation) : [];
      const originalPoints = showPoints ? faceData.landmarks[feature].map(([x, y]) => 
        ({ x, y, type: 'point', feature })) : [];
      
      return [...curvePoints, ...originalPoints];
    });
  }, [faceData, showCurves, showPoints, generateFeaturePoints]);

  const getFeatureColor = useCallback((feature) => {
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
  }, []);

  if (!faceData?.landmarks || !faceData?.equations) {
    return (
      <Alert>
        <AlertDescription>No face data available to visualize</AlertDescription>
      </Alert>
    );
  }

  return (
    <div className="bg-white rounded-xl shadow-lg p-6 space-y-4">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-gray-900">Enhanced Face Visualization</h2>
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

      <div className="flex flex-wrap gap-2 mb-4">
        {Object.keys(faceData.equations).map(feature => (
          <Button
            key={feature}
            variant={selectedFeature === feature ? "default" : "outline"}
            onClick={() => setSelectedFeature(selectedFeature === feature ? null : feature)}
            className="text-sm"
            style={{
              color: selectedFeature === feature ? 'white' : getFeatureColor(feature),
              borderColor: getFeatureColor(feature)
            }}
          >
            {feature.replace(/_/g, ' ')}
          </Button>
        ))}
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
            <Tooltip
              formatter={(value, name) => [value.toFixed(3), name]}
              labelFormatter={(label) => `x: ${parseFloat(label).toFixed(3)}`}
            />
            {Object.keys(faceData.equations)
              .filter(feature => !selectedFeature || feature === selectedFeature)
              .map((feature) => (
                <Line
                  key={feature}
                  data={allFeatureData.filter(point => point.feature === feature)}
                  type="monotone"
                  dataKey="y"
                  stroke={getFeatureColor(feature)}
                  strokeWidth={selectedFeature === feature ? 3 : 2}
                  dot={point => 
                    point.type === 'point' && showPoints ? 
                    { r: 3, fill: getFeatureColor(feature) } : false
                  }
                  isAnimationActive={false}
                  connectNulls={true}
                  name={feature.replace(/_/g, ' ')}
                />
            ))}
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

export default EnhancedFaceVisualizer;