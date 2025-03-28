import React, { useState, useEffect } from 'react';
import { Bar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js';

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

const MetricsDashboard = ({ projectId }) => {
  const [metrics, setMetrics] = useState({ materialSavings: 0, timeReduction: 0, qualityImprovement: 0 });
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        setLoading(true);
        const response = await fetch(`/api/metrics/${projectId}`);
        if (!response.ok) throw new Error('Failed to fetch metrics');
        const data = await response.json();
        setMetrics(data);
        setError(null);
      } catch (error) {
        setError('Failed to load metrics. Please try again later.');
      } finally {
        setLoading(false);
      }
    };

    if (projectId) {
      fetchMetrics();
    }
  }, [projectId]);

  const chartData = {
    labels: ['Material Savings', 'Print Time Reduction', 'Quality Improvement'],
    datasets: [
      {
        label: 'Optimization Results',
        data: [metrics.materialSavings, metrics.timeReduction, metrics.qualityImprovement],
        backgroundColor: ['rgba(54, 162, 235, 0.8)', 'rgba(255, 99, 132, 0.8)', 'rgba(75, 192, 192, 0.8)'],
        borderColor: ['rgba(54, 162, 235, 1)', 'rgba(255, 99, 132, 1)', 'rgba(75, 192, 192, 1)'],
        borderWidth: 1
      }
    ]
  };

  return (
    <div className="dashboard">
      {error && <p className="error-message">{error}</p>}
      {loading ? <p>Loading metrics...</p> : <Bar data={chartData} />}
    </div>
  );
};

export default MetricsDashboard;