import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import App from './App';
import './styles/App.css';

const reportError = (error, errorInfo) => {
  console.error('Application error:', error, errorInfo);
};

const renderFallbackUI = () => {
  ReactDOM.createRoot(document.getElementById('root')).render(
    <div style={{ padding: '20px', textAlign: 'center', fontFamily: 'system-ui' }}>
      <h1>Something went wrong</h1>
      <p>Please refresh the page or contact support if the problem persists.</p>
      <button 
        onClick={() => window.location.reload()}
        style={{ padding: '8px 16px', marginTop: '16px', cursor: 'pointer' }}
      >
        Retry
      </button>
    </div>
  );
};

const renderApp = () => {
  try {
    const root = ReactDOM.createRoot(document.getElementById('root'));
    
    root.render(
      <React.StrictMode>
        <BrowserRouter>
          <App />
        </BrowserRouter>
      </React.StrictMode>
    );
  } catch (error) {
    reportError(error);
    renderFallbackUI();
  }
};

window.addEventListener('unhandledrejection', (event) => {
  reportError(event.reason);
});

window.addEventListener('error', (event) => {
  reportError(event.error);
});

renderApp();

if (import.meta.hot) {
  import.meta.hot.accept();
}