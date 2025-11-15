import React, { useState, useEffect } from 'react';
import { getAuditLogs, getAuditSummary } from '../api/api';

const AuditLogs = () => {
  const [logs, setLogs] = useState([]);
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [filters, setFilters] = useState({
    action: '',
    status: '',
    user_id: '',
    limit: 50,
    offset: 0
  });

  useEffect(() => {
    fetchData();
  }, [filters]);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [logsData, summaryData] = await Promise.all([
        getAuditLogs(filters),
        getAuditSummary()
      ]);
      setLogs(logsData);
      setSummary(summaryData);
      setError('');
    } catch (err) {
      setError(err.detail || 'Failed to fetch audit data');
    } finally {
      setLoading(false);
    }
  };

  const handleFilterChange = (key, value) => {
    setFilters(prev => ({
      ...prev,
      [key]: value,
      offset: 0 // Reset pagination when filters change
    }));
  };

  const loadMore = () => {
    setFilters(prev => ({
      ...prev,
      offset: prev.offset + prev.limit
    }));
  };

  const formatTimestamp = (timestamp) => {
    return new Date(timestamp).toLocaleString();
  };

  const getStatusColor = (status) => {
    return status === 'success' 
      ? 'bg-success-100 text-success-800' 
      : 'bg-danger-100 text-danger-800';
  };

  const getActionColor = (action) => {
    const colorMap = {
      login: 'bg-blue-100 text-blue-800',
      signup: 'bg-green-100 text-green-800',
      create_key: 'bg-purple-100 text-purple-800',
      rotate_key: 'bg-yellow-100 text-yellow-800',
      revoke_key: 'bg-red-100 text-red-800',
      delete_key: 'bg-gray-100 text-gray-800',
      encrypt: 'bg-indigo-100 text-indigo-800',
      decrypt: 'bg-teal-100 text-teal-800'
    };
    return colorMap[action] || 'bg-gray-100 text-gray-800';
  };

  if (loading && logs.length === 0) {
    return (
      <div className="flex justify-center items-center min-h-96">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary-500"></div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Audit Logs</h1>
        <p className="mt-2 text-gray-600">
          Monitor all system activities and user actions
        </p>
      </div>

      {error && (
        <div className="mb-6 bg-red-50 border border-red-300 text-red-700 px-4 py-3 rounded">
          {error}
        </div>
      )}

      {/* Summary Cards */}
      {summary && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-lg font-medium text-gray-900">Total Logs</h3>
            <p className="text-3xl font-bold text-primary-600">{summary.total_logs}</p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-lg font-medium text-gray-900 mb-2">Top Actions</h3>
            <div className="space-y-1">
              {summary.actions.slice(0, 3).map((item, index) => (
                <div key={index} className="flex justify-between text-sm">
                  <span className="capitalize">{item.action.replace('_', ' ')}</span>
                  <span className="font-medium">{item.count}</span>
                </div>
              ))}
            </div>
          </div>
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-lg font-medium text-gray-900 mb-2">Status Summary</h3>
            <div className="space-y-1">
              {summary.statuses.map((item, index) => (
                <div key={index} className="flex justify-between text-sm">
                  <span className="capitalize">{item.status}</span>
                  <span className="font-medium">{item.count}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Filters */}
      <div className="bg-white p-6 rounded-lg shadow mb-6">
        <h3 className="text-lg font-medium mb-4">Filters</h3>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Action
            </label>
            <select
              value={filters.action}
              onChange={(e) => handleFilterChange('action', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
            >
              <option value="">All Actions</option>
              <option value="login">Login</option>
              <option value="signup">Signup</option>
              <option value="create_key">Create Key</option>
              <option value="rotate_key">Rotate Key</option>
              <option value="revoke_key">Revoke Key</option>
              <option value="delete_key">Delete Key</option>
              <option value="encrypt">Encrypt</option>
              <option value="decrypt">Decrypt</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Status
            </label>
            <select
              value={filters.status}
              onChange={(e) => handleFilterChange('status', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
            >
              <option value="">All Statuses</option>
              <option value="success">Success</option>
              <option value="failure">Failure</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              User ID
            </label>
            <input
              type="number"
              value={filters.user_id}
              onChange={(e) => handleFilterChange('user_id', e.target.value)}
              placeholder="Filter by user ID"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Limit
            </label>
            <select
              value={filters.limit}
              onChange={(e) => handleFilterChange('limit', parseInt(e.target.value))}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
            >
              <option value={25}>25</option>
              <option value={50}>50</option>
              <option value={100}>100</option>
            </select>
          </div>
        </div>
      </div>

      {/* Logs Table */}
      <div className="bg-white shadow rounded-lg overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Timestamp
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  User
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Action
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Resource
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  IP Address
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {logs.map((log) => (
                <tr key={log.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {formatTimestamp(log.timestamp)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {log.user_id || 'N/A'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getActionColor(log.action)}`}>
                      {log.action.replace('_', ' ')}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {log.resource_type}
                    {log.resource_id && ` #${log.resource_id}`}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(log.status)}`}>
                      {log.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {log.ip_address}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        
        {logs.length === 0 && !loading && (
          <div className="text-center py-12">
            <h3 className="text-lg font-medium text-gray-900 mb-2">No audit logs found</h3>
            <p className="text-gray-600">Try adjusting your filters</p>
          </div>
        )}
        
        {logs.length >= filters.limit && (
          <div className="bg-gray-50 px-6 py-3">
            <button
              onClick={loadMore}
              disabled={loading}
              className="text-primary-600 hover:text-primary-500 font-medium disabled:opacity-50"
            >
              {loading ? 'Loading...' : 'Load More'}
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default AuditLogs;