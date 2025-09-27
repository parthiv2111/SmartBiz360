import React from 'react';
import { Navigate } from 'react-router-dom';
import { useApp } from '../../contexts/AppContext';
import LoadingSpinner from '../ui/LoadingSpinner';

interface PublicRouteProps {
  children: React.ReactNode;
}

const PublicRoute: React.FC<PublicRouteProps> = ({ children }) => {
  const { state } = useApp();

  // Show loading spinner while checking authentication
  if (state.isLoading) {
    return <LoadingSpinner text="Loading..." />;
  }

  // If user is authenticated, redirect to dashboard
  if (state.isAuthenticated) {
    return <Navigate to="/" replace />;
  }

  // If user is not authenticated, render the public content
  return <>{children}</>;
};

export default PublicRoute;
