import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const EquationGraph = ({ equations, points }) => {
  // Generate points for the graph
  const generateGraphPoints = () => {
    if (!equations || !equations.coefficients) return [];
    
    const data = [];
    const numPoints = 100;
    
    // Generate x values between 0 and 1
    for (let i = 0; i <= numPoints; i++) {
      const x = i / numPoints;
      let y = 0;
      
      // Calculate y value based on equation type
      if (equations.type === 'polynomial') {
        // Evaluate polynomial
        equations.coefficients.forEach((coeff, index) => {
          const power = equations.coefficients.length - 1 - index;
          y += coeff * Math.pow(x, power);
        });
      } else if (equations.type === 'trigonometric') {
        // Evaluate trigonometric series
        const params = equations.parameters;
        y = params[0]; // offset
        for (let j = 1; j < params.length; j += 2) {
          if (j + 1 < params.length) {
            y += params[j] * Math.sin(j * Math.PI * x) + 
                 params[j+1] * Math.cos(j * Math.PI * x);
          }
        }
      }
      
      data.push({ x, y });
    }
    
    return data;
  };

  const graphData = generateGraphPoints();

  return (
    <div className="w-full h-96 mt-8">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={graphData} margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="x" />
          <YAxis />
          <Tooltip />
          <Legend />
          <Line 
            type="monotone" 
            dataKey="y" 
            stroke="#8884d8" 
            name="Generated Equation" 
          />
          {points && (
            <Line
              type="scatter"
              data={points.map(p => ({ x: p[0], y: p[1] }))}
              dataKey="y"
              stroke="#82ca9d"
              name="Original Points"
              dot={{ r: 4 }}
              line={false}
            />
          )}
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

export default EquationGraph;