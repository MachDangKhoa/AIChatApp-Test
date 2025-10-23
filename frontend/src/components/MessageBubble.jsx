/**
 * MessageBubble Component - Renders individual chat messages with rich content support
 * 
 * @component
 * @param {Object} props - Component properties
 * @param {string} props.message - The message content to display
 * @param {boolean} props.isUser - Indicates if the message is from user or assistant
 * @param {string} props.timestamp - ISO timestamp of the message
 * @param {string} props.imagePreview - URL for image preview
 * @param {string} props.fileUrl - URL or filename for attached files
 * @param {string} props.csvContent - CSV content for preview modal
 * @param {Function} props.onFileClick - Callback function when file is clicked
 */

import React from 'react';
import ReactMarkdown from 'react-markdown';
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend } from 'chart.js';
import { Bar } from 'react-chartjs-2';
import { BASE_URL } from '../services/chatAPI';

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

const MessageBubble = ({ 
  message, 
  isUser, 
  timestamp, 
  imagePreview, 
  fileUrl, 
  csvContent, 
  onFileClick 
}) => {
  const parseMessageContent = (msg) => {
    let displayMessage = msg;
    let chartData = null;

    const histogramRegex = /📊 Histogram data for '(.+?)':\n([\s\S]*)/;
    const match = msg.match(histogramRegex);
    
    if (match) {
      try {
        const [, columnName, jsonData] = match;
        const histData = JSON.parse(jsonData);
        
        chartData = {
          labels: histData.bins.map((bin, index) => 
            `${bin}-${histData.bins[index + 1] || histData.bins[index] + (histData.bins[1] - histData.bins[0])}`
          ),
          datasets: [{
            label: `Distribution of ${columnName}`,
            data: histData.frequencies,
            backgroundColor: 'rgba(102, 126, 234, 0.8)',
            borderColor: 'rgba(102, 126, 234, 1)',
            borderWidth: 1,
            borderRadius: 4,
          }],
        };
        
        displayMessage = msg.replace(histogramRegex, '').trim();
      } catch (error) {
        console.error('Failed to parse histogram data:', error);
      }
    }

    return { displayMessage, chartData };
  };

  const getImageSource = (imgPreview) => {
    if (!imgPreview) return '';
    
    if (imgPreview.startsWith('blob:') || imgPreview.startsWith('http')) {
      return imgPreview;
    }
    
    return `${BASE_URL}${imgPreview}`;
  };

  const formatTimestamp = (isoString) => {
    return new Date(isoString).toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      hour12: true
    });
  };

  const { displayMessage, chartData } = parseMessageContent(message);
  const bubbleClass = `message ${isUser ? 'user-message' : 'assistant-message'}`;
  const timestampClass = `timestamp ${isUser ? 'user-timestamp' : 'assistant-timestamp'}`;

  const chartOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top',
        labels: {
          usePointStyle: true,
          padding: 15,
        }
      },
      tooltip: {
        mode: 'index',
        intersect: false,
      }
    },
    scales: {
      y: {
        beginAtZero: true,
        grid: {
          color: 'rgba(0, 0, 0, 0.1)',
        }
      },
      x: {
        grid: {
          display: false,
        }
      }
    }
  };

  return (
    <div className={bubbleClass}>
      {/* Markdown Content - chỉ dùng in đậm */}
      <div className="message-content">
        <ReactMarkdown
          components={{
            // Chỉ cần in đậm cho các từ khoá quan trọng
            strong: ({ node, ...props }) => (
              <strong className="bold-text" {...props} />
            ),
            // Code elements cũng hiển thị như text bình thường, chỉ in đậm
            code: ({ node, ...props }) => (
              <strong className="bold-text" {...props} />
            ),
          }}
        >
          {displayMessage}
        </ReactMarkdown>
      </div>

      {imagePreview && (
        <div className="image-preview-container">
          <img
            src={getImageSource(imagePreview)}
            alt="Uploaded preview"
            className="preview-image"
            loading="lazy"
          />
        </div>
      )}

      {fileUrl && (
        <div 
          className="file-attachment"
          onClick={() => onFileClick?.(csvContent)}
          role="button"
          tabIndex={0}
          onKeyDown={(e) => {
            if (e.key === 'Enter' || e.key === ' ') {
              onFileClick?.(csvContent);
            }
          }}
        >
          <div className="file-icon">📄</div>
          <span className="file-name">{fileUrl}</span>
          <div className="file-hint">Click to preview</div>
        </div>
      )}

      {chartData && (
        <div className="chart-container">
          <Bar 
            data={chartData} 
            options={chartOptions}
            height={300}
          />
        </div>
      )}

      <div className={timestampClass}>
        {formatTimestamp(timestamp)}
      </div>
    </div>
  );
};

export default MessageBubble;