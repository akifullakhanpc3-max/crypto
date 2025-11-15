import React, { useState, useEffect } from 'react';
import { getKeys, createKey, rotateKey, revokeKey, deleteKey } from '../api/api';
import KeyCard from '../components/KeyCard';

const Dashboard = ({ user }) => {
  const [keys, setKeys] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [createForm, setCreateForm] = useState({
    name: '',
    key_type: 'AES256GCM'
  });

  useEffect(() => {
    fetchKeys();
  }, []);

  const fetchKeys = async () => {
    try {
      setLoading(true);
      const keysData = await getKeys();
      setKeys(keysData);
      setError('');
    } catch (err) {
      setError(err.detail || 'Failed to fetch keys');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateKey = async (e) => {
    e.preventDefault();
    if (!createForm.name.trim()) {
      setError('Key name is required');
      return;
    }

    try {
      const newKey = await createKey(createForm);
      setKeys([...keys, newKey]);
      setCreateForm({ name: '', key_type: 'AES256GCM' });
      setShowCreateForm(false);
      setError('');
    } catch (err) {
      setError(err.detail || 'Failed to create key');
    }
  };

  const handleKeyAction = async (keyId, action) => {
    try {
      let updatedKey;
      switch (action) {
        case 'rotate':
          updatedKey = await rotateKey(keyId);
          break;
        case 'revoke':
          updatedKey = await revokeKey(keyId);
          break;
        case 'delete':
          await deleteKey(keyId);
          setKeys(keys.filter(key => key.id !== keyId));
          return;
        default:
          return;
      }
      
      setKeys(keys.map(key => key.id === keyId ? updatedKey : key));
      setError('');
    } catch (err) {
      setError(err.detail || `Failed to ${action} key`);
    }
  };

  const stats = {
    total: keys.length,
    active: keys.filter(key => key.is_active && !key.is_revoked).length,
    revoked: keys.filter(key => key.is_revoked).length,
    symmetric: keys.filter(key => ['AES128GCM', 'AES256GCM', 'AES256CBC', 'ChaCha20Poly1305'].includes(key.key_type)).length,
    asymmetric: keys.filter(key => ['RSA', 'RSA2048', 'RSA4096', 'ECC256', 'ECC384', 'Ed25519'].includes(key.key_type)).length,
    hmac: keys.filter(key => ['HMAC256', 'HMAC512'].includes(key.key_type)).length
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-96">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary-500"></div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">
          Welcome, {user.username}!
        </h1>
        <p className="mt-2 text-gray-600">
          Manage your cryptographic keys securely
        </p>
      </div>

      {/* Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-6 gap-4 mb-8">
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-medium text-gray-900">Total Keys</h3>
          <p className="text-3xl font-bold text-primary-600">{stats.total}</p>
        </div>
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-medium text-gray-900">Active</h3>
          <p className="text-3xl font-bold text-green-500">{stats.active}</p>
        </div>
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-medium text-gray-900">Revoked</h3>
          <p className="text-3xl font-bold text-red-500">{stats.revoked}</p>
        </div>
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-medium text-gray-900">Symmetric</h3>
          <p className="text-3xl font-bold text-blue-500">{stats.symmetric}</p>
        </div>
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-medium text-gray-900">Asymmetric</h3>
          <p className="text-3xl font-bold text-purple-500">{stats.asymmetric}</p>
        </div>
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-medium text-gray-900">HMAC</h3>
          <p className="text-3xl font-bold text-orange-500">{stats.hmac}</p>
        </div>
      </div>

      {error && (
        <div className="mb-6 bg-red-50 border border-red-300 text-red-700 px-4 py-3 rounded">
          {error}
        </div>
      )}

      {/* Create Key Section */}
      {user.role === 'admin' && (
        <div className="mb-8">
          {!showCreateForm ? (
            <button
              onClick={() => setShowCreateForm(true)}
              className="bg-primary-600 hover:bg-primary-700 text-white px-4 py-2 rounded-md font-medium"
            >
              + Create New Key
            </button>
          ) : (
            <div className="bg-white p-6 rounded-lg shadow">
              <h3 className="text-lg font-medium mb-4">Create New Key</h3>
              <form onSubmit={handleCreateKey} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Key Name
                  </label>
                  <input
                    type="text"
                    value={createForm.name}
                    onChange={(e) => setCreateForm({...createForm, name: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
                    placeholder="Enter key name"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Key Type
                  </label>
                  <select
                    value={createForm.key_type}
                    onChange={(e) => setCreateForm({...createForm, key_type: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
                  >
                    <optgroup label="Symmetric Encryption">
                      <option value="AES128GCM">AES-128-GCM</option>
                      <option value="AES256GCM">AES-256-GCM</option>
                      <option value="AES256CBC">AES-256-CBC</option>
                      <option value="ChaCha20Poly1305">ChaCha20-Poly1305</option>
                    </optgroup>
                    <optgroup label="Asymmetric Encryption">
                      <option value="RSA2048">RSA-2048</option>
                      <option value="RSA4096">RSA-4096</option>
                      <option value="RSA">RSA-2048 (Legacy)</option>
                    </optgroup>
                    <optgroup label="Digital Signatures">
                      <option value="ECC256">ECC P-256</option>
                      <option value="ECC384">ECC P-384</option>
                      <option value="Ed25519">Ed25519</option>
                    </optgroup>
                    <optgroup label="Message Authentication">
                      <option value="HMAC256">HMAC-SHA256</option>
                      <option value="HMAC512">HMAC-SHA512</option>
                    </optgroup>
                  </select>
                </div>
                <div className="flex space-x-4">
                  <button
                    type="submit"
                    className="bg-primary-600 hover:bg-primary-700 text-white px-4 py-2 rounded-md font-medium"
                  >
                    Create Key
                  </button>
                  <button
                    type="button"
                    onClick={() => {
                      setShowCreateForm(false);
                      setCreateForm({ name: '', key_type: 'AES256GCM' });
                    }}
                    className="bg-gray-300 hover:bg-gray-400 text-gray-700 px-4 py-2 rounded-md font-medium"
                  >
                    Cancel
                  </button>
                </div>
              </form>
            </div>
          )}
        </div>
      )}

      {/* Keys Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {keys.map(key => (
          <KeyCard
            key={key.id}
            keyData={key}
            userRole={user.role}
            onAction={handleKeyAction}
          />
        ))}
      </div>

      {keys.length === 0 && (
        <div className="text-center py-12">
          <h3 className="text-lg font-medium text-gray-900 mb-2">No keys found</h3>
          <p className="text-gray-600">
            {user.role === 'admin' 
              ? 'Create your first cryptographic key to get started'
              : 'No keys have been created yet'
            }
          </p>
        </div>
      )}
    </div>
  );
};

export default Dashboard;