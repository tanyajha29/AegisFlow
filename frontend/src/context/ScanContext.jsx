import React, { createContext, useContext, useState } from 'react';
import api from '../lib/api.js';

const ScanContext = createContext();

export const useScan = () => useContext(ScanContext);

export const ScanProvider = ({ children }) => {
  const [lastResult, setLastResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const runCodeScan = async (payload) => {
    setLoading(true);
    setError(null);
    try {
      const { data } = await api.post('/scan/code', payload);
      setLastResult(data);
      return data;
    } catch (e) {
      setError(e.response?.data?.detail || 'Scan failed');
      throw e;
    } finally {
      setLoading(false);
    }
  };

  const runUploadScan = async (file) => {
    setLoading(true);
    setError(null);
    const formData = new FormData();
    formData.append('file', file);
    try {
      const { data } = await api.post('/scan/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      setLastResult(data);
      return data;
    } catch (e) {
      setError(e.response?.data?.detail || 'Scan failed');
      throw e;
    } finally {
      setLoading(false);
    }
  };

  return (
    <ScanContext.Provider value={{ lastResult, loading, error, runCodeScan, runUploadScan }}>
      {children}
    </ScanContext.Provider>
  );
};
