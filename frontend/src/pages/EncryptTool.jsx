import React, { useState, useEffect } from 'react';
import { getKeys, encryptData, decryptData } from '../api/api';

const EncryptTool = () => {
  const [keys, setKeys] = useState([]);
  const [activeTab, setActiveTab] = useState('encrypt');
  const [encryptForm, setEncryptForm] = useState({
    key_id: '',
    plaintext: ''
  });
  const [decryptForm, setDecryptForm] = useState({
    key_id: '',
    ciphertext: ''
  });
  const [result, setResult] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchKeys();
  }, []);

  const fetchKeys = async () => {
    try {
      const keysData = await getKeys();
      const activeKeys = keysData.filter(key => key.is_active && !key.is_revoked);
      setKeys(activeKeys);
    } catch (err) {
      setError(err.detail || 'Failed to fetch keys');
    }
  };

  const handleEncrypt = async (e) => {
    e.preventDefault();
    if (!encryptForm.key_id || !encryptForm.plaintext.trim()) {
      setError('Please select a key and enter plaintext');
      return;
    }

    setLoading(true);
    try {
      const response = await encryptData(encryptForm);
      setResult(response.ciphertext);
      setError('');
    } catch (err) {
      setError(err.detail || 'Encryption failed');
      setResult('');
    } finally {
      setLoading(false);
    }
  };

  const handleDecrypt = async (e) => {
    e.preventDefault();
    if (!decryptForm.key_id || !decryptForm.ciphertext.trim()) {
      setError('Please select a key and enter ciphertext');
      return;
    }

    setLoading(true);
    try {
      const response = await decryptData(decryptForm);
      setResult(response.plaintext);
      setError('');
    } catch (err) {
      setError(err.detail || 'Decryption failed');
      setResult('');
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = () => {
    navigator.clipboard.writeText(result);
  };

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">
          Encryption/Decryption Tool
        </h1>
        <p className="mt-2 text-gray-600">
          Encrypt and decrypt data using your managed keys
        </p>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200 mb-6">
        <nav className="-mb-px flex">
          <button
            onClick={() => {
              setActiveTab('encrypt');
              setResult('');
              setError('');
            }}
            className={`py-2 px-4 border-b-2 font-medium text-sm ${
              activeTab === 'encrypt'
                ? 'border-primary-500 text-primary-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            Encrypt
          </button>
          <button
            onClick={() => {
              setActiveTab('decrypt');
              setResult('');
              setError('');
            }}
            className={`ml-8 py-2 px-4 border-b-2 font-medium text-sm ${
              activeTab === 'decrypt'
                ? 'border-primary-500 text-primary-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            Decrypt
          </button>
        </nav>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Input Form */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-medium mb-4">
            {activeTab === 'encrypt' ? 'Encrypt Data' : 'Decrypt Data'}
          </h3>
          
          <form onSubmit={activeTab === 'encrypt' ? handleEncrypt : handleDecrypt}>
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Select Key
              </label>
              <select
                value={activeTab === 'encrypt' ? encryptForm.key_id : decryptForm.key_id}
                onChange={(e) => {
                  const value = e.target.value;
                  if (activeTab === 'encrypt') {
                    setEncryptForm({...encryptForm, key_id: value});
                  } else {
                    setDecryptForm({...decryptForm, key_id: value});
                  }
                }}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
                required
              >
                <option value="">Choose a key...</option>
                {keys.map(key => (
                  <option key={key.id} value={key.id}>
                    {key.name} ({key.key_type}) - v{key.key_version}
                  </option>
                ))}
              </select>
            </div>

            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                {activeTab === 'encrypt' ? 'Plaintext' : 'Ciphertext'}
              </label>
              <textarea
                value={activeTab === 'encrypt' ? encryptForm.plaintext : decryptForm.ciphertext}
                onChange={(e) => {
                  const value = e.target.value;
                  if (activeTab === 'encrypt') {
                    setEncryptForm({...encryptForm, plaintext: value});
                  } else {
                    setDecryptForm({...decryptForm, ciphertext: value});
                  }
                }}
                rows={6}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
                placeholder={activeTab === 'encrypt' 
                  ? 'Enter text to encrypt...' 
                  : 'Enter base64 ciphertext to decrypt...'}
                required
              />
            </div>

            <button
              type="submit"
              disabled={loading || keys.length === 0}
              className="w-full bg-primary-600 hover:bg-primary-700 disabled:bg-gray-400 text-white py-2 px-4 rounded-md font-medium"
            >
              {loading ? (
                <div className="flex items-center justify-center">
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                  Processing...
                </div>
              ) : (
                activeTab === 'encrypt' ? 'Encrypt' : 'Decrypt'
              )}
            </button>
          </form>
        </div>

        {/* Result Display */}
        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-medium">
              {activeTab === 'encrypt' ? 'Encrypted Result' : 'Decrypted Result'}
            </h3>
            {result && (
              <button
                onClick={copyToClipboard}
                className="text-sm bg-gray-100 hover:bg-gray-200 px-3 py-1 rounded"
              >
                Copy
              </button>
            )}
          </div>

          {error && (
            <div className="mb-4 bg-red-50 border border-red-300 text-red-700 px-4 py-3 rounded">
              {error}
            </div>
          )}

          <div className="min-h-48">
            {result ? (
              <div className="bg-gray-50 p-4 rounded-md">
                <pre className="whitespace-pre-wrap break-all text-sm font-mono">
                  {result}
                </pre>
              </div>
            ) : (
              <div className="flex items-center justify-center h-full text-gray-500">
                {keys.length === 0 
                  ? 'No active keys available for encryption/decryption'
                  : `${activeTab === 'encrypt' ? 'Encrypted' : 'Decrypted'} result will appear here`
                }
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Instructions */}
      <div className="mt-8 bg-blue-50 p-6 rounded-lg">
        <h4 className="text-lg font-medium text-blue-900 mb-2">Instructions</h4>
        <ul className="text-blue-800 space-y-1">
          <li>• Select an active key from the dropdown</li>
          <li>• For encryption: Enter plaintext and get base64-encoded ciphertext</li>
          <li>• For decryption: Enter base64 ciphertext and get plaintext</li>
          <li>• Only active (non-revoked) keys can be used for encryption</li>
          <li>• Revoked keys can still decrypt previously encrypted data</li>
        </ul>
      </div>
    </div>
  );
};

export default EncryptTool;