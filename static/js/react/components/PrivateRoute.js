import React from 'react';
import { Route, Redirect } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';

const PrivateRoute = ({ component: Component, roles, ...rest }) => {
  const { user, isAuthenticated } = useAuth();

  return (
    <Route
      {...rest}
      render={(props) => {
        // Not logged in
        if (!isAuthenticated) {
          return <Redirect to="/login" />;
        }

        // Check if route is restricted by role
        if (roles && roles.length > 0 && !roles.includes(user.role)) {
          return <Redirect to="/unauthorized" />;
        }

        // Authorized, render component
        return <Component {...props} />;
      }}
    />
  );
};

export default PrivateRoute;