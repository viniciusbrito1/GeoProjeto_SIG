import { createContext, useCallback, useContext, useEffect, useMemo, useState, type ReactNode } from "react";

import { api, limparToken, obterToken, salvarToken } from "../api/client";
import type { Perfil, UsuarioAutenticado } from "../types";

interface RespostaLogin {
  access_token: string;
  perfil: Perfil;
  nome: string;
}

interface AuthContextValor {
  usuario: UsuarioAutenticado | null;
  carregando: boolean;
  login: (email: string, senha: string) => Promise<void>;
  logout: () => Promise<void>;
  temPerfil: (...perfis: Perfil[]) => boolean;
}

const AuthContext = createContext<AuthContextValor | null>(null);

// Os tiles WMS do GeoServer são <img> e não enviam o cabeçalho Authorization;
// esta chamada grava o token num cookie HttpOnly restrito a /geoserver para
// que o proxy libere as camadas OGC (RNF-09). Falhar aqui não impede o uso do
// resto do sistema — só as camadas do GeoServer deixariam de carregar.
function abrirSessaoOgc(): Promise<void> {
  return api.post<void>("/auth/sessao-ogc").catch(() => undefined);
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [usuario, setUsuario] = useState<UsuarioAutenticado | null>(null);
  const [carregando, setCarregando] = useState(true);

  useEffect(() => {
    if (!obterToken()) {
      setCarregando(false);
      return;
    }
    api
      .get<UsuarioAutenticado>("/auth/me")
      .then((me) => {
        setUsuario(me);
        return abrirSessaoOgc();
      })
      .catch(() => limparToken())
      .finally(() => setCarregando(false));
  }, []);

  const login = useCallback(async (email: string, senha: string) => {
    const resposta = await api.post<RespostaLogin>("/auth/login", { email, senha });
    salvarToken(resposta.access_token);
    const me = await api.get<UsuarioAutenticado>("/auth/me");
    await abrirSessaoOgc();
    setUsuario(me);
  }, []);

  const logout = useCallback(async () => {
    await api.post<void>("/auth/logout").catch(() => undefined);
    limparToken();
    setUsuario(null);
    window.location.href = "/login";
  }, []);

  const temPerfil = useCallback((...perfis: Perfil[]) => !!usuario && perfis.includes(usuario.perfil), [usuario]);

  const valor = useMemo(() => ({ usuario, carregando, login, logout, temPerfil }), [usuario, carregando, login, logout, temPerfil]);

  return <AuthContext.Provider value={valor}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValor {
  const contexto = useContext(AuthContext);
  if (!contexto) throw new Error("useAuth precisa estar dentro de <AuthProvider>");
  return contexto;
}
