'use client'

import React, { useState } from 'react';
import { Upload } from 'lucide-react';
import { Alert, AlertDescription } from '@/components/ui/alert';
import EnhancedFaceVisualizer from './EnhancedFaceVisualizer';
import ImageLandmarks from './ImageLandmarks';

const FaceEquations = () => {
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [faceData, setFaceData] = useState(null);
  const [landmarkData, setLandmarkData] = useState(null);
  const [equationType, setEquationType] = useState('polynomial');
  const [degree, setDegree] = useState(4);

  const handleFileChange = (event) => {
    const selectedFile = event.target.files[0];
    if (selectedFile) {
      setFile(selectedFile);
      setPreview(URL.createObjectURL(selectedFile));
      setError(null);
      uploadImage(selectedFile);
    }
  };

  const uploadImage = async (selectedFile) => {
    setLoading(true);
    setError(null);

    try {
      // First, analyze the image to get landmarks
      const analyzeFormData = new FormData();
      analyzeFormData.append('file', selectedFile);
      
      const analyzeResponse = await fetch('http://localhost:8000/api/face/analyze', {
        method: 'POST',
        body: analyzeFormData,
      });

      if (!analyzeResponse.ok) {
        throw new Error('Failed to analyze image');
      }

      const analyzeData = await analyzeResponse.json();
      setLandmarkData(analyzeData);

      // Then, get the equations
      const equationFormData = new FormData();
      equationFormData.append('file', selectedFile);
      equationFormData.append('equation_type', equationType);
      equationFormData.append('degree', degree);

      const equationResponse = await fetch('http://localhost:8000/api/face/upload', {
        method: 'POST',
        body: equationFormData,
      });

      if (!equationResponse.ok) {
        throw new Error('Failed to generate equations');
      }

      const equationData = await equationResponse.json();
      setFaceData(equationData);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-6xl mx-auto">
        <div className="bg-white rounded-xl shadow-lg p-8">
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">Face to Equations</h1>
            <p className="text-gray-600">Upload a face image to generate mathematical equations</p>
          </div>

          <div className="grid md:grid-cols-2 gap-8">
            <div className="space-y-6">
              <div className="flex items-center justify-center w-full">
                <label className="flex flex-col items-center justify-center w-full h-64 border-2 border-gray-300 border-dashed rounded-lg cursor-pointer bg-gray-50 hover:bg-gray-100">
                  <div className="flex flex-col items-center justify-center pt-5 pb-6">
                    {!preview && (
                      <>
                        <Upload className="w-10 h-10 mb-3 text-gray-400" />
                        <p className="mb-2 text-sm text-gray-500">
                          <span className="font-semibold">Click to upload</span> or drag and drop
                        </p>
                        <p className="text-xs text-gray-500">PNG, JPG or JPEG</p>
                      </>
                    )}
                  </div>
                  <input
                    type="file"
                    className="hidden"
                    accept="image/*"
                    onChange={handleFileChange}
                    disabled={loading}
                  />
                </label>
              </div>
              
              {preview && landmarkData && (
                <div className="bg-white rounded-lg p-4 shadow-md">
                  <h3 className="text-lg font-semibold mb-3">Detected Features</h3>
                  <ImageLandmarks 
                    imageUrl={preview}
                    landmarks={landmarkData.landmarks}
                    imageDimensions={landmarkData.image_dimensions}
                  />
                </div>
              )}

              {loading && (
                <div className="mt-4 text-center text-gray-600">
                  Processing image...
                </div>
              )}

              {error && (
                <Alert variant="destructive" className="mt-4">
                  <AlertDescription>{error}</AlertDescription>
                </Alert>
              )}
            </div>

            <div>
              {/* {faceData && <FaceVisualizer faceData={faceData} />} */}
              {faceData && <EnhancedFaceVisualizer faceData={faceData} />}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default FaceEquations;