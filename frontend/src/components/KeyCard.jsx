import React from 'react';

const KeyCard = ({ keyData, userRole, onAction }) => {
  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString();
  };

  const getStatusColor = () => {
    if (keyData.is_revoked) return 'bg-red-100 text-red-800';
    if (!keyData.is_active) return 'bg-gray-100 text-gray-800';
    return 'bg-green-100 text-green-800';
  };

  const getStatusText = () => {
    if (keyData.is_revoked) return 'Revoked';
    if (!keyData.is_active) return 'Inactive';
    return 'Active';
  };

  const getKeyTypeColor = () => {
    return keyData.key_type === 'AES256GCM' 
      ? 'bg-blue-100 text-blue-800' 
      : 'bg-purple-100 text-purple-800';
  };

  const handleAction = (action) => {
    if (window.confirm(`Are you sure you want to ${action} this key?`)) {
      onAction(keyData.id, action);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md border border-gray-200 p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900 truncate">
          {keyData.name}
        </h3>
        <div className="flex space-x-2">
          <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getKeyTypeColor()}`}>
            {keyData.key_type}
          </span>
          <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor()}`}>
            {getStatusText()}
          </span>
        </div>
      </div>

      {/* Key Information */}
      <div className="space-y-3 mb-6">
        <div className="flex justify-between text-sm">
          <span className="text-gray-500">ID:</span>
          <span className="font-medium">#{keyData.id}</span>
        </div>
        <div className="flex justify-between text-sm">
          <span className="text-gray-500">Version:</span>
          <span className="font-medium">v{keyData.key_version}</span>
        </div>
        <div className="flex justify-between text-sm">
          <span className="text-gray-500">Created:</span>
          <span className="font-medium">{formatDate(keyData.created_at)}</span>
        </div>
        {keyData.rotated_at && (
          <div className="flex justify-between text-sm">
            <span className="text-gray-500">Last Rotated:</span>
            <span className="font-medium">{formatDate(keyData.rotated_at)}</span>
          </div>
        )}
        {keyData.revoked_at && (
          <div className="flex justify-between text-sm">
            <span className="text-gray-500">Revoked:</span>
            <span className="font-medium">{formatDate(keyData.revoked_at)}</span>
          </div>
        )}
      </div>

      {/* Actions */}
      {userRole === 'admin' && (
        <div className="border-t pt-4">
          <div className="flex flex-wrap gap-2">
            {keyData.is_active && !keyData.is_revoked && (
              <>
                <button
                  onClick={() => handleAction('rotate')}
                  className="bg-yellow-500 hover:bg-yellow-600 text-white px-3 py-1 rounded text-sm font-medium"
                >
                  Rotate
                </button>
                <button
                  onClick={() => handleAction('revoke')}
                  className="bg-orange-500 hover:bg-orange-600 text-white px-3 py-1 rounded text-sm font-medium"
                >
                  Revoke
                </button>
              </>
            )}
            <button
              onClick={() => handleAction('delete')}
              className="bg-red-500 hover:bg-red-600 text-white px-3 py-1 rounded text-sm font-medium"
            >
              Delete
            </button>
          </div>
        </div>
      )}

      {/* Key Usage Info */}
      <div className="mt-4 pt-4 border-t">
        <div className="text-xs text-gray-500">
          {keyData.is_active && !keyData.is_revoked ? (
            <span className="text-green-600">✓ Available for encryption/decryption</span>
          ) : keyData.is_revoked ? (
            <span className="text-orange-600">⚠️ Can decrypt existing data only</span>
          ) : (
            <span className="text-red-600">✗ Unavailable</span>
          )}
        </div>
      </div>
    </div>
  );
};

export default KeyCard;