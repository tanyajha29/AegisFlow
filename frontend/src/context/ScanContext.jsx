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

  const runUploadScan = async (files) => {
    setLoading(true);
    setError(null);
    const formData = new FormData();
    const fileArray = Array.isArray(files) ? files : [files];

    fileArray.forEach((file, idx) => {
      formData.append('files', file);
      // also append singular "file" for backends that expect one field
      if (idx === 0) formData.append('file', file);
    });

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

  const runRepoScan = async (repo_url, branch = null) => {
    setLoading(true);
    setError(null);
    try {
      const { data } = await api.post('/scan/repo', { repo_url, branch });
      setLastResult(data);
      return data;
    } catch (e) {
      setError(e.response?.data?.detail || 'Repository scan failed');
      throw e;
    } finally {
      setLoading(false);
    }
  };

  return (
    <ScanContext.Provider value={{ lastResult, loading, error, runCodeScan, runUploadScan, runRepoScan }}>
      {children}
    </ScanContext.Provider>
  );
};
