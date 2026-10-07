import { Navigate } from 'react-router-dom';

export default function ProtectedRoute({ user, roles, children }) {
  if (!user) return <Navigate to="/login" replace />;
  if (roles && !roles.includes(user.perfil)) return <Navigate to="/dashboard" replace />;
  return children;
}
