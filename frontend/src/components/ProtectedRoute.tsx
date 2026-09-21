import type { ReactNode } from "react";
import { Navigate } from "react-router-dom";

import { useAuth } from "../auth/AuthContext";
import type { Perfil } from "../types";

export function ProtectedRoute({ children, perfis }: { children: ReactNode; perfis?: Perfil[] }) {
  const { usuario, carregando, temPerfil } = useAuth();

  if (carregando) return null;
  if (!usuario) return <Navigate to="/login" replace />;
  if (perfis && !temPerfil(...perfis)) return <Navigate to="/mapa" replace />;

  return <>{children}</>;
}
