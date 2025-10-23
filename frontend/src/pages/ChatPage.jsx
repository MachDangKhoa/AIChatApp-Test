/**
 * ChatPage Component - Main application page
 * Renders the chat interface with professional header and layout
 * 
 * @component
 * @example
 * return <ChatPage />
 */

import React from 'react';
import ChatBox from '../components/ChatBox';

const ChatPage = () => (
  <div className="chat-page">
    <header className="chat-header">
      <div className="header-content">
        <div className="logo-section">
          <div className="logo">🤖</div>
          <h1>AI Chat Assistant</h1>
        </div>
        <div className="subtitle">
          Powered by Gemini AI • Multi-modal Chat Support
        </div>
      </div>
    </header>
    <main className="chat-main">
      <ChatBox />
    </main>
  </div>
);

export default ChatPage;