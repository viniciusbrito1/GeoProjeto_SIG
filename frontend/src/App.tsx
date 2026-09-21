import { Navigate, Route, Routes } from "react-router-dom";

import { Layout } from "./components/Layout";
import { ProtectedRoute } from "./components/ProtectedRoute";
import { Auditoria } from "./pages/Auditoria";
import { CamadasExternas } from "./pages/CamadasExternas";
import { Login } from "./pages/Login";
import { Mapa } from "./pages/Mapa";
import { OcorrenciaDetalhe } from "./pages/OcorrenciaDetalhe";
import { Ocorrencias } from "./pages/Ocorrencias";
import { Recursos } from "./pages/Recursos";
import { Usuarios } from "./pages/Usuarios";

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route
        path="/*"
        element={
          <ProtectedRoute>
            <Layout>
              <Routes>
                <Route path="/" element={<Navigate to="/mapa" replace />} />
                <Route path="/mapa" element={<Mapa />} />
                <Route path="/ocorrencias" element={<Ocorrencias />} />
                <Route path="/ocorrencias/:id" element={<OcorrenciaDetalhe />} />
                <Route path="/recursos" element={<Recursos />} />
                <Route
                  path="/auditoria"
                  element={
                    <ProtectedRoute perfis={["coordenador"]}>
                      <Auditoria />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/camadas-externas"
                  element={
                    <ProtectedRoute perfis={["coordenador"]}>
                      <CamadasExternas />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/usuarios"
                  element={
                    <ProtectedRoute perfis={["coordenador"]}>
                      <Usuarios />
                    </ProtectedRoute>
                  }
                />
                <Route path="*" element={<Navigate to="/mapa" replace />} />
              </Routes>
            </Layout>
          </ProtectedRoute>
        }
      />
    </Routes>
  );
}
