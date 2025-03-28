import React from 'react';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import Navigation from '../components/Navigation';

describe('Navigation Component', () => {
  test('renders navigation links', () => {
    render(
      <MemoryRouter>
        <Navigation />
      </MemoryRouter>
    );
    expect(screen.getByRole('navigation')).toBeInTheDocument();
  });
});