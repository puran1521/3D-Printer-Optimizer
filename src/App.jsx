import React, { Suspense } from 'react';
import { BrowserRouter as Router, Route, Routes, Navigate } from 'react-router-dom';
import Navigation from './components/Navigation';
import ErrorBoundary from './components/ErrorBoundary';
import LoadingSpinner from './components/LoadingSpinner';
import './styles/App.css';

// Ensure these components exist in the specified paths
const ModelViewer = React.lazy(() => import('./components/ModelViewer'));
const MetricsDashboard = React.lazy(() => import('./components/MetricsDashboard'));
const ProjectManager = React.lazy(() => import('./components/ProjectManager'));

const App = () => {
  return (
    <ErrorBoundary>
      <Router>
        <div className="app-container">
          <Navigation />
          <main className="main-content">
            <Suspense fallback={<LoadingSpinner />}>
              <Routes>
                <Route path="/" element={<ProjectManager />} />
                <Route path="/project/:projectId/optimize" element={<ModelViewer />} />
                <Route path="/project/:projectId/results" element={<MetricsDashboard />} />
                <Route path="*" element={<Navigate to="/" replace />} />
              </Routes>
            </Suspense>
          </main>
        </div>
      </Router>
    </ErrorBoundary>
  );
};

export default App;