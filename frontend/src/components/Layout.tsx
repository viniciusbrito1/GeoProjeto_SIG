import type { ReactNode } from "react";
import { NavLink } from "react-router-dom";

import { useAuth } from "../auth/AuthContext";

const ITENS_NAV: Array<{ para: string; rotulo: string; perfis?: Array<"coordenador" | "operador" | "consulta"> }> = [
  { para: "/mapa", rotulo: "Mapa" },
  { para: "/ocorrencias", rotulo: "Ocorrências" },
  { para: "/recursos", rotulo: "Recursos" },
  { para: "/camadas-externas", rotulo: "Camadas externas", perfis: ["coordenador"] },
  { para: "/auditoria", rotulo: "Auditoria", perfis: ["coordenador"] },
  { para: "/usuarios", rotulo: "Usuários", perfis: ["coordenador"] },
];

export function Layout({ children }: { children: ReactNode }) {
  const { usuario, logout, temPerfil } = useAuth();

  return (
    <div className="app-shell">
      <aside className="barra-lateral">
        <div className="marca">
          SISCOORD-DC
          <small>Defesa Civil Estadual · Exército Brasileiro</small>
        </div>
        <nav>
          {ITENS_NAV.filter((item) => !item.perfis || temPerfil(...item.perfis)).map((item) => (
            <NavLink key={item.para} to={item.para} className={({ isActive }) => (isActive ? "ativo" : "")}>
              {item.rotulo}
            </NavLink>
          ))}
        </nav>
        <div className="usuario">
          <div>{usuario?.nome}</div>
          <span className="perfil-badge">{usuario?.perfil}</span>
          <div style={{ marginTop: 10 }}>
            <button className="secundario" onClick={logout} style={{ width: "100%" }}>
              Sair
            </button>
          </div>
        </div>
      </aside>
      <div className="conteudo">{children}</div>
    </div>
  );
}
