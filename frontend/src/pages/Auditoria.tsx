import { Fragment, useState } from "react";

import { useAuditoria } from "../api/hooks";

export function Auditoria() {
  const [tabela, setTabela] = useState("");
  const { data: registros, isLoading } = useAuditoria({ tabela: tabela || undefined });
  const [registroExpandido, setRegistroExpandido] = useState<number | null>(null);

  return (
    <div className="conteudo-padding">
      <div className="topo-pagina">
        <h1>Trilha de auditoria</h1>
      </div>
      <p style={{ fontSize: 13, color: "var(--cinza-700)", marginTop: -10, marginBottom: 16 }}>
        Gravada automaticamente por gatilho no banco de dados a cada escrita (RF-13) — somente leitura, mesmo para a aplicação.
      </p>

      <div className="filtros">
        <label>
          Tabela
          <select value={tabela} onChange={(e) => setTabela(e.target.value)}>
            <option value="">Todas</option>
            <option value="recursos">Recursos</option>
            <option value="ocorrencias">Ocorrências</option>
            <option value="demandas">Demandas</option>
            <option value="empenhos">Empenhos</option>
            <option value="usuarios">Usuários</option>
          </select>
        </label>
      </div>

      <table>
        <thead>
          <tr>
            <th>Data/hora</th>
            <th>Tabela</th>
            <th>Operação</th>
            <th>Usuário</th>
            <th>Registro</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {isLoading && (
            <tr>
              <td colSpan={6}>Carregando...</td>
            </tr>
          )}
          {registros?.map((r) => (
            <Fragment key={r.id}>
              <tr>
                <td>{new Date(r.criado_em).toLocaleString("pt-BR")}</td>
                <td>{r.tabela}</td>
                <td>{r.operacao}</td>
                <td>{r.usuario_nome ?? "sistema"}</td>
                <td style={{ fontFamily: "monospace", fontSize: 12 }}>{r.registro_id?.slice(0, 8)}</td>
                <td>
                  <button className="secundario" onClick={() => setRegistroExpandido(registroExpandido === r.id ? null : r.id)}>
                    {registroExpandido === r.id ? "Ocultar" : "Ver dados"}
                  </button>
                </td>
              </tr>
              {registroExpandido === r.id && (
                <tr>
                  <td colSpan={6}>
                    <div style={{ display: "flex", gap: 16 }}>
                      <div style={{ flex: 1 }}>
                        <b style={{ fontSize: 12 }}>Antes</b>
                        <pre style={{ fontSize: 11.5, background: "var(--cinza-100)", padding: 10, borderRadius: 6, overflowX: "auto" }}>
                          {JSON.stringify(r.dados_antes, null, 2) ?? "—"}
                        </pre>
                      </div>
                      <div style={{ flex: 1 }}>
                        <b style={{ fontSize: 12 }}>Depois</b>
                        <pre style={{ fontSize: 11.5, background: "var(--cinza-100)", padding: 10, borderRadius: 6, overflowX: "auto" }}>
                          {JSON.stringify(r.dados_depois, null, 2) ?? "—"}
                        </pre>
                      </div>
                    </div>
                  </td>
                </tr>
              )}
            </Fragment>
          ))}
        </tbody>
      </table>
    </div>
  );
}
