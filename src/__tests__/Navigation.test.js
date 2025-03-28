import React from 'react';
import { render, screen } from '@testing-library/react';
import { MemoryRouter, RouterProvider, createBrowserRouter } from 'react-router-dom';
import Navigation from '../components/Navigation';

const routes = [
  {
    path: '/',
    element: <Navigation />,
  },
];

const router = createBrowserRouter(routes, {
  future: {
    v7_startTransition: true,
    v7_relativeSplatPath: true,
  },
});

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

<RouterProvider router={router} />;