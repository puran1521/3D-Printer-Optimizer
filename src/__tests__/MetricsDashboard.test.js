import React from 'react';
import { render, screen } from '@testing-library/react';
import MetricsDashboard from '../components/MetricsDashboard';

describe('MetricsDashboard Component', () => {
  test('renders loading state initially', () => {
    render(<MetricsDashboard />);
    expect(screen.getByText(/loading metrics/i)).toBeInTheDocument();
  });
});