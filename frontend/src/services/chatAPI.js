/**
 * API service module for handling backend interactions.
 * Supports text, image, and CSV chat endpoints with optional streaming.
 * Uses FormData for POST requests and fetch for streaming responses.
 */

import axios from 'axios';

export const BASE_URL = import.meta.env.VITE_BACKEND_URL;

/**
 * Sends a text message to the backend.
 * @param {string} message - User's input message.
 * @param {Array<Object>} history - Chat history as array of message objects.
 * @param {boolean} stream - Whether to enable streaming response.
 * @returns {Promise<Object>} Response containing reply and updated history.
 */
export const sendTextMessage = async (message, history, stream = false) => {
  const formData = new FormData();
  formData.append('message', message);
  formData.append('history', JSON.stringify(history));
  formData.append('stream', stream);

  if (stream) {
    return handleStreamingResponse(`${BASE_URL}/api/chat/`, formData);
  } else {
    const response = await axios.post(`${BASE_URL}/api/chat/`, formData);
    return response.data;
  }
};

/**
 * Sends an image-based query to the backend.
 * @param {string} question - User's question about the image.
 * @param {File} imageFile - Uploaded image file.
 * @param {Array<Object>} history - Chat history.
 * @param {boolean} stream - Enable streaming.
 * @returns {Promise<Object>} Response data.
 */
export const sendImageMessage = async (question, imageFile, history, stream = false) => {
  const formData = new FormData();
  formData.append('question', question);
  formData.append('file', imageFile);
  formData.append('history', JSON.stringify(history));
  formData.append('stream', stream);

  if (stream) {
    return handleStreamingResponse(`${BASE_URL}/api/image`, formData);
  } else {
    const response = await axios.post(`${BASE_URL}/api/image`, formData);
    return response.data;
  }
};

/**
 * Sends a CSV-based query to the backend.
 * @param {string} question - User's question about the CSV data.
 * @param {File|string} csvFileOrUrl - CSV file or URL.
 * @param {Array<Object>} history - Chat history.
 * @param {boolean} stream - Enable streaming.
 * @returns {Promise<Object>} Response data.
 */
export const sendCsvMessage = async (question, csvFileOrUrl, history, stream = false) => {
  const formData = new FormData();
  formData.append('question', question);
  formData.append('history', JSON.stringify(history));
  formData.append('stream', stream);
  if (csvFileOrUrl instanceof File) {
    formData.append('file', csvFileOrUrl);
  } else {
    formData.append('url', csvFileOrUrl);
  }

  if (stream) {
    return handleStreamingResponse(`${BASE_URL}/api/csv`, formData);
  } else {
    const response = await axios.post(`${BASE_URL}/api/csv`, formData);
    return response.data;
  }
};

/**
 * Helper function to handle streaming responses using fetch and ReadableStream.
 * Parses SSE-like data chunks and collects full reply and history.
 * @param {string} url - Endpoint URL.
 * @param {FormData} formData - Request body.
 * @returns {Promise<Object>} Collected response {reply, history}.
 */
async function handleStreamingResponse(url, formData) {
  return new Promise((resolve, reject) => {
    fetch(url, {
      method: 'POST',
      body: formData,
    }).then(response => {
      if (!response.ok) {
        reject(`HTTP error! status: ${response.status}`);
        return;
      }
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let fullReply = '';
      let updatedHistory = [];
      reader.read().then(function processChunk({ done, value }) {
        if (done) {
          resolve({ reply: fullReply.trim(), history: updatedHistory });
          return;
        }
        const chunk = decoder.decode(value);
        const lines = chunk.split('\n\n');
        lines.forEach(line => {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6));
              if (data.chunk) fullReply += data.chunk;
              if (data.reply) fullReply += data.reply; // For non-chunked replies like histogram
              if (data.history) updatedHistory = data.history;
              if (data.error) reject(data.error);
              if (data.status === 'complete') {
                // Stream complete
              }
            } catch (e) {
              reject('Invalid JSON in stream');
            }
          }
        });
        return reader.read().then(processChunk);
      });
    }).catch(reject);
  });
}