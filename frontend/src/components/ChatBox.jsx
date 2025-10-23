/**
 * ChatBox component: Core chat interface.
 * Manages chat history, user inputs, file uploads, and API interactions.
 * Supports streaming for smooth response updates.
 */

import React, { useState, useRef, useEffect } from 'react';
import MessageBubble from './MessageBubble';
import LoadingIndicator from './LoadingIndicator';
import { sendTextMessage, sendImageMessage, sendCsvMessage } from '../services/chatAPI';

const ChatBox = () => {
  const [history, setHistory] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [imageFile, setImageFile] = useState(null);
  const [csvInput, setCsvInput] = useState('');
  const [csvFile, setCsvFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [csvPreview, setCsvPreview] = useState(null);
  const [csvContent, setCsvContent] = useState(null);
  const [selectedCsvContent, setSelectedCsvContent] = useState(null);
  const chatHistoryRef = useRef(null);
  const imageInputRef = useRef(null);
  const csvFileInputRef = useRef(null);

  useEffect(() => {
    if (chatHistoryRef.current) {
      chatHistoryRef.current.scrollTop = chatHistoryRef.current.scrollHeight;
    }
  }, [history]);

  const handleSend = async () => {
    if (!input.trim() && !imageFile && !csvFile && !csvInput.trim()) return;

    const isImage = !!imageFile;
    const isCsv = !!csvFile || !!csvInput.trim();
    const userContent = input;
    const currentTime = new Date().toISOString();
    
    const userMessage = {
      role: 'user',
      content: userContent,
      timestamp: currentTime,
      ...(isImage && { image_url: preview }),
      ...(isCsv && { 
        file_url: csvFile ? csvFile.name : csvInput,
        csv_content: csvContent
      }),
    };

    setHistory([...history, userMessage]);
    setInput('');
    setIsLoading(true);
    setImageFile(null);
    setPreview(null);
    setCsvFile(null);
    setCsvPreview(null);
    setCsvInput('');
    setCsvContent(null);

    try {
      let response;
      const stream = true;
      if (isImage) {
        response = await sendImageMessage(userContent, imageFile, history, stream);
      } else if (isCsv) {
        const csvFileOrUrl = csvFile || csvInput;
        response = await sendCsvMessage(userContent, csvFileOrUrl, history, stream);
      } else {
        response = await sendTextMessage(userContent, history, stream);
      }

      if (response.body) {
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = '';
        let fullReply = '';

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split('\n\n');
          buffer = lines.pop();

          for (const line of lines) {
            if (line.startsWith('data: ')) {
              const data = JSON.parse(line.slice(6));
              
              if (data.chunk) {
                fullReply += data.chunk;
                setHistory(prev => {
                  const newHistory = [...prev];
                  newHistory[newHistory.length - 1] = { 
                    role: 'assistant', 
                    content: fullReply, 
                    timestamp: new Date().toISOString() 
                  };
                  return newHistory;
                });
              }
              
              if (data.history) {
                setHistory(data.history);
              }
            }
          }
        }
      } else {
        const assistantMessage = {
          role: 'assistant',
          content: response.reply,
          timestamp: new Date().toISOString(),
        };
        setHistory([...history, userMessage, assistantMessage]);
      }

    } catch (error) {
      const errorMessage = {
        role: 'assistant',
        content: `Error: ${error.message}`,
        timestamp: new Date().toISOString(),
      };
      setHistory([...history, userMessage, errorMessage]);
    } finally {
      setIsLoading(false);
      if (imageInputRef.current) imageInputRef.current.value = '';
      if (csvFileInputRef.current) csvFileInputRef.current.value = '';
    }
  };

  const handleImageUpload = (e) => {
    const file = e.target.files[0];
    if (file && ['image/png', 'image/jpeg'].includes(file.type)) {
      setImageFile(file);
      setPreview(URL.createObjectURL(file));
    }
  };

  const handleCsvFileUpload = (e) => {
    const file = e.target.files[0];
    if (file && file.type === 'text/csv') {
      setCsvFile(file);
      setCsvInput('');
      setCsvPreview(file.name);
      const reader = new FileReader();
      reader.onload = (event) => {
        setCsvContent(event.target.result);
      };
      reader.readAsText(file);
    }
  };

  const handleCsvInputChange = (e) => {
    setCsvInput(e.target.value);
    setCsvFile(null);
    setCsvPreview(null);
    setCsvContent(null);
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const clearImagePreview = () => {
    setImageFile(null);
    setPreview(null);
    if (imageInputRef.current) imageInputRef.current.value = '';
  };

  const clearCsvPreview = () => {
    setCsvFile(null);
    setCsvPreview(null);
    setCsvContent(null);
    if (csvFileInputRef.current) csvFileInputRef.current.value = '';
  };

  return (
    <div className="chat-container">
      <div className="chat-history" ref={chatHistoryRef}>
        {history.map((msg, index) => (
          <MessageBubble
            key={index}
            message={msg.content}
            isUser={msg.role === 'user'}
            timestamp={msg.timestamp}
            imagePreview={msg.image_url}
            fileUrl={msg.file_url}
            csvContent={msg.csv_content}
            onFileClick={(content) => setSelectedCsvContent(content)}
          />
        ))}
        {isLoading && <LoadingIndicator />}
      </div>

      {/* Preview Areas */}
      {preview && (
        <div className="file-preview">
          <div className="preview-header">
            <span>📷 Image Ready</span>
            <button onClick={clearImagePreview} className="preview-close">
              ×
            </button>
          </div>
          <img src={preview} alt="Preview" className="preview-image" />
        </div>
      )}

      {csvPreview && (
        <div className="file-preview">
          <div className="preview-header">
            <span>📄 CSV File: {csvPreview}</span>
            <button onClick={clearCsvPreview} className="preview-close">
              ×
            </button>
          </div>
          <div 
            className="file-preview-click" 
            onClick={() => setSelectedCsvContent(csvContent)}
          >
            Click to preview CSV content
          </div>
        </div>
      )}

      {/* Input Area */}
      <div className="input-area">
        {/* Text Input */}
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Enter your message or question..."
          className="chat-input"
          disabled={isLoading}
        />

        {/* File Upload Buttons */}
        <label htmlFor="image-upload" className="file-upload-label">
          📷 Image
          <input
            id="image-upload"
            type="file"
            accept="image/png,image/jpeg"
            onChange={handleImageUpload}
            ref={imageInputRef}
            disabled={isLoading}
          />
        </label>

        <label htmlFor="csv-upload" className="file-upload-label">
          📄 CSV
          <input
            id="csv-upload"
            type="file"
            accept=".csv"
            onChange={handleCsvFileUpload}
            ref={csvFileInputRef}
            disabled={isLoading}
          />
        </label>

        {/* CSV URL Input */}
        <input
          type="text"
          value={csvInput}
          onChange={handleCsvInputChange}
          placeholder="Or paste CSV URL"
          className="csv-url-input"
          disabled={isLoading}
        />

        {/* Send Button */}
        <button 
          onClick={handleSend} 
          className="send-button"
          disabled={isLoading || (!input.trim() && !imageFile && !csvFile && !csvInput.trim())}
        >
          {isLoading ? '⏳' : '🚀'} Send
        </button>
      </div>

      {/* CSV Modal */}
      {selectedCsvContent && (
        <div className="modal-overlay" onClick={() => setSelectedCsvContent(null)}>
          <div className="csv-modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3 className="modal-title">📊 CSV Content Preview</h3>
              <button 
                className="modal-close"
                onClick={() => setSelectedCsvContent(null)}
              >
                ×
              </button>
            </div>
            <textarea 
              value={selectedCsvContent} 
              readOnly 
              className="csv-modal-content"
            />
            <div className="modal-actions">
              <button 
                className="send-button"
                onClick={() => setSelectedCsvContent(null)}
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ChatBox;