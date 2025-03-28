import React from 'react';
import { render, screen, act } from '@testing-library/react';
import App from '../App';

describe('App Component', () => {
  test('renders without crashing', async () => {
    await act(async () => {
      render(<App />);
    });
    expect(screen.getByRole('main')).toBeInTheDocument();
  });
});
