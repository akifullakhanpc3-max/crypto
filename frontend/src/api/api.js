import api from './auth';

// Keys API
export const getKeys = async () => {
  try {
    const response = await api.get('/api/keys');
    return response.data;
  } catch (error) {
    throw error.response?.data || { detail: 'Failed to fetch keys' };
  }
};

export const createKey = async (keyData) => {
  try {
    const response = await api.post('/api/keys', keyData);
    return response.data;
  } catch (error) {
    throw error.response?.data || { detail: 'Failed to create key' };
  }
};

export const rotateKey = async (keyId) => {
  try {
    const response = await api.post(`/api/keys/${keyId}/rotate`);
    return response.data;
  } catch (error) {
    throw error.response?.data || { detail: 'Failed to rotate key' };
  }
};

export const revokeKey = async (keyId) => {
  try {
    const response = await api.post(`/api/keys/${keyId}/revoke`);
    return response.data;
  } catch (error) {
    throw error.response?.data || { detail: 'Failed to revoke key' };
  }
};

export const deleteKey = async (keyId) => {
  try {
    const response = await api.delete(`/api/keys/${keyId}`);
    return response.data;
  } catch (error) {
    throw error.response?.data || { detail: 'Failed to delete key' };
  }
};

// Encryption API
export const encryptData = async (encryptRequest) => {
  try {
    const response = await api.post('/api/encrypt', encryptRequest);
    return response.data;
  } catch (error) {
    throw error.response?.data || { detail: 'Failed to encrypt data' };
  }
};

export const decryptData = async (decryptRequest) => {
  try {
    const response = await api.post('/api/decrypt', decryptRequest);
    return response.data;
  } catch (error) {
    throw error.response?.data || { detail: 'Failed to decrypt data' };
  }
};

// Audit API
export const getAuditLogs = async (params = {}) => {
  try {
    const response = await api.get('/api/audit/logs', { params });
    return response.data;
  } catch (error) {
    throw error.response?.data || { detail: 'Failed to fetch audit logs' };
  }
};

export const getAuditSummary = async () => {
  try {
    const response = await api.get('/api/audit/logs/summary');
    return response.data;
  } catch (error) {
    throw error.response?.data || { detail: 'Failed to fetch audit summary' };
  }
};