"use client"

import React, { useState, useEffect } from 'react';
import { Upload, Camera } from 'lucide-react';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const FaceEquations = () => {
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [landmarks, setLandmarks] = useState(null);
  const [equations, setEquations] = useState(null);
  const [selectedFeature, setSelectedFeature] = useState('jawline');
  const [equationType, setEquationType] = useState('polynomial');
  const [degree, setDegree] = useState(4);

  const features = [
    'jawline', 'right_eyebrow', 'left_eyebrow', 'nose_bridge',
    'nose_tip', 'right_eye', 'left_eye', 'outer_lips', 'inner_lips'
  ];

  const handleFileChange = (event) => {
    const selectedFile = event.target.files[0];
    if (selectedFile) {
      setFile(selectedFile);
      setPreview(URL.createObjectURL(selectedFile));
      setError(null);
    }
  };

  const uploadImage = async () => {
    if (!file) return;

    setLoading(true);
    setError(null);

    const formData = new FormData();
    formData.append('file', file);
    formData.append('equation_type', equationType);
    formData.append('degree', degree);

    try {
      const response = await fetch('http://localhost:8000/api/face/upload', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Failed to process image');
      }

      const data = await response.json();
      setLandmarks(data.landmarks);
      setEquations(data.equations);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // Generate points for plotting
  const generatePlotData = () => {
    if (!landmarks || !equations) return [];

    const feature = selectedFeature;
    const points = landmarks[feature];
    const equation = equations[feature];

    if (!points || !equation) return [];

    // Generate equation curve points
    const curvePoints = [];
    const numPoints = 100;
    for (let i = 0; i <= numPoints; i++) {
      const x = i / numPoints;
      const coeffs = equation.coefficients;
      let y = 0;
      for (let j = 0; j < coeffs.length; j++) {
        y += coeffs[j] * Math.pow(x, coeffs.length - 1 - j);
      }
      curvePoints.push({ x, y, type: 'curve' });
    }

    // Add original landmark points
    const landmarkPoints = points.map(([x, y]) => ({
      x, y, type: 'point'
    }));

    return [...curvePoints, ...landmarkPoints];
  };

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-6xl mx-auto">
        <div className="bg-white rounded-xl shadow-lg p-8">
          {/* Header */}
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">Face to Equations</h1>
            <p className="text-gray-600">Upload a face image to generate mathematical equations for facial features</p>
          </div>

          {/* Upload Section */}
          <div className="mb-8">
            <div className="flex gap-4 mb-4">
              <div className="flex-1">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Equation Type
                </label>
                <select
                  value={equationType}
                  onChange={(e) => setEquationType(e.target.value)}
                  className="w-full rounded-md border border-gray-300 p-2"
                >
                  <option value="polynomial">Polynomial</option>
                  <option value="trigonometric">Trigonometric</option>
                  <option value="fourier">Fourier</option>
                </select>
              </div>
              <div className="flex-1">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Degree/Terms
                </label>
                <input
                  type="number"
                  value={degree}
                  onChange={(e) => setDegree(parseInt(e.target.value))}
                  className="w-full rounded-md border border-gray-300 p-2"
                  min="1"
                  max="10"
                />
              </div>
            </div>

            <div className="flex items-center justify-center w-full">
              <label className="flex flex-col items-center justify-center w-full h-64 border-2 border-gray-300 border-dashed rounded-lg cursor-pointer bg-gray-50 hover:bg-gray-100">
                <div className="flex flex-col items-center justify-center pt-5 pb-6">
                  <Upload className="w-10 h-10 mb-3 text-gray-400" />
                  <p className="mb-2 text-sm text-gray-500">
                    <span className="font-semibold">Click to upload</span> or drag and drop
                  </p>
                  <p className="text-xs text-gray-500">PNG, JPG or JPEG</p>
                </div>
                <input
                  type="file"
                  className="hidden"
                  accept="image/*"
                  onChange={handleFileChange}
                />
              </label>
            </div>

            {preview && (
              <div className="mt-4">
                <img
                  src={preview}
                  alt="Preview"
                  className="max-h-64 mx-auto rounded-lg"
                />
                <button
                  onClick={uploadImage}
                  disabled={loading}
                  className="mt-4 w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 disabled:bg-blue-300"
                >
                  {loading ? 'Processing...' : 'Generate Equations'}
                </button>
              </div>
            )}
          </div>

          {error && (
            <Alert variant="destructive" className="mb-8">
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          {equations && (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              {/* Equation Display */}
              <div className="bg-gray-50 p-6 rounded-lg">
                <h2 className="text-xl font-semibold mb-4">Generated Equations</h2>
                <div className="space-y-4">
                  {features.map((feature) => (
                    <div
                      key={feature}
                      className={`p-4 rounded-md cursor-pointer transition-colors ${
                        selectedFeature === feature
                          ? 'bg-blue-100 border border-blue-300'
                          : 'bg-white border border-gray-200 hover:bg-gray-50'
                      }`}
                      onClick={() => setSelectedFeature(feature)}
                    >
                      <h3 className="font-medium text-gray-900 capitalize mb-2">
                        {feature.replace('_', ' ')}
                      </h3>
                      <p className="text-sm text-gray-600 font-mono overflow-x-auto">
                        {equations[feature].equation}
                      </p>
                    </div>
                  ))}
                </div>
              </div>

              {/* Visualization */}
              <div className="bg-gray-50 p-6 rounded-lg">
                <h2 className="text-xl font-semibold mb-4">Visualization</h2>
                <div className="h-96">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={generatePlotData()} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="x" />
                      <YAxis />
                      <Tooltip />
                      <Legend />
                      {generatePlotData()
                        .filter(point => point.type === 'curve')
                        .length > 0 && (
                        <Line
                          data={generatePlotData().filter(point => point.type === 'curve')}
                          type="monotone"
                          dataKey="y"
                          stroke="#2563eb"
                          name="Equation"
                          dot={false}
                        />
                      )}
                      <Line
                        data={generatePlotData().filter(point => point.type === 'point')}
                        type="scatter"
                        dataKey="y"
                        stroke="#16a34a"
                        name="Original Points"
                        dot={{ r: 4 }}
                        line={false}
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default FaceEquations;