/**
 * App component: Root of the React application.
 * Routes to the ChatPage.
 */

import React from 'react';
import ChatPage from './pages/ChatPage';

function App() {
  return (
    <div className="App">
      <ChatPage />
    </div>
  );
}

export default App;