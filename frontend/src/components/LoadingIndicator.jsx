/**
 * LoadingIndicator Component - Hiển thị trạng thái loading với thông tin retry
 */

import React from 'react';

const LoadingIndicator = ({ retryCount = 0, maxRetries = 2 }) => (
  <div className="loading">
    <div className="loading-content">
      <div className="loading-dots">
        <div className="loading-dot"></div>
        <div className="loading-dot"></div>
        <div className="loading-dot"></div>
      </div>
      <p className="loading-text">
        AI is thinking... 
        {retryCount > 0 && (
          <span className="loading-retry">
            (Retry {retryCount}/{maxRetries})
          </span>
        )}
      </p>
    </div>
  </div>
);

export default LoadingIndicator;