import React, { useState } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const FeatureVisualizer = ({ data }) => {
  const [selectedFeature, setSelectedFeature] = useState('jawline');
  
  // Generate points for the equation curve
  const generateCurvePoints = () => {
    if (!data?.equations?.[selectedFeature]) return [];
    
    const equation = data.equations[selectedFeature];
    const coefficients = equation.coefficients;
    
    const curvePoints = [];
    // Generate 100 points for smooth curve
    for (let i = 0; i <= 100; i++) {
      const x = i / 100;
      let y = 0;
      // Evaluate polynomial
      for (let j = 0; j < coefficients.length; j++) {
        y += coefficients[j] * Math.pow(x, coefficients.length - 1 - j);
      }
      curvePoints.push({ x, y, type: 'curve' });
    }
    
    // Add original landmark points
    const landmarkPoints = data.landmarks[selectedFeature].map(([x, y]) => ({
      x, y, type: 'point'
    }));
    
    return [...curvePoints, ...landmarkPoints];
  };

  const features = [
    'jawline', 'right_eyebrow', 'left_eyebrow', 'nose_bridge',
    'nose_tip', 'right_eye', 'left_eye', 'outer_lips', 'inner_lips'
  ];

  return (
    <div className="bg-white rounded-xl shadow-lg p-6">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">Face Feature Equations</h2>
        
        {/* Feature Selection */}
        <div className="flex flex-wrap gap-2 mb-6">
          {features.map((feature) => (
            <button
              key={feature}
              onClick={() => setSelectedFeature(feature)}
              className={`px-4 py-2 rounded-full text-sm font-medium transition-colors
                ${selectedFeature === feature 
                  ? 'bg-blue-600 text-white' 
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'}`}
            >
              {feature.replace('_', ' ')}
            </button>
          ))}
        </div>

        {/* Equation Display */}
        <div className="bg-gray-50 p-4 rounded-lg mb-6">
          <h3 className="text-sm font-medium text-gray-600 mb-2">Equation:</h3>
          <p className="font-mono text-sm text-gray-800 overflow-x-auto">
            {data?.equations?.[selectedFeature]?.equation}
          </p>
        </div>
      </div>

      {/* Graph */}
      <div className="h-96">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart 
            data={generateCurvePoints()} 
            margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
          >
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis 
              dataKey="x" 
              domain={[0, 1]}
              tickFormatter={(value) => value.toFixed(1)}
            />
            <YAxis 
              domain={[0, 1]}
              tickFormatter={(value) => value.toFixed(1)}
            />
            <Tooltip 
              formatter={(value) => value.toFixed(4)}
              labelFormatter={(value) => `x: ${value.toFixed(4)}`}
            />
            <Legend />
            {/* Equation Curve */}
            <Line
              data={generateCurvePoints().filter(p => p.type === 'curve')}
              type="monotone"
              dataKey="y"
              stroke="#2563eb"
              name="Fitted Equation"
              dot={false}
              strokeWidth={2}
            />
            {/* Original Points */}
            <Line
              data={generateCurvePoints().filter(p => p.type === 'point')}
              type="scatter"
              dataKey="y"
              stroke="#16a34a"
              name="Original Points"
              dot={{ r: 4, fill: '#16a34a' }}
              line={false}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

export default FeatureVisualizer;