import { useState } from "react";
import { Link } from "react-router-dom";

import { useOcorrencias } from "../api/hooks";
import type { StatusOcorrencia } from "../types";

export function Ocorrencias() {
  const [statusFiltro, setStatusFiltro] = useState<StatusOcorrencia | "">("aberta");
  const { data: ocorrencias, isLoading } = useOcorrencias(statusFiltro || undefined);

  return (
    <div className="conteudo-padding">
      <div className="topo-pagina">
        <h1>Ocorrências</h1>
      </div>

      <div className="filtros">
        <label>
          Status
          <select value={statusFiltro} onChange={(e) => setStatusFiltro(e.target.value as StatusOcorrencia | "")}>
            <option value="">Todas</option>
            <option value="aberta">Abertas</option>
            <option value="encerrada">Encerradas</option>
          </select>
        </label>
      </div>

      <table>
        <thead>
          <tr>
            <th>Tipo</th>
            <th>Município</th>
            <th>Severidade</th>
            <th>Status</th>
            <th>Demandas</th>
            <th>Aberta em</th>
          </tr>
        </thead>
        <tbody>
          {isLoading && (
            <tr>
              <td colSpan={6}>Carregando...</td>
            </tr>
          )}
          {ocorrencias?.map((o) => {
            const saldoTotal = o.demandas.reduce((soma, d) => soma + d.saldo_descoberto, 0);
            return (
              <tr key={o.id}>
                <td>
                  <Link to={`/ocorrencias/${o.id}`}>{o.tipo}</Link>
                </td>
                <td>{o.municipio_nome}</td>
                <td>
                  <span className={`badge ${o.severidade}`}>{o.severidade}</span>
                </td>
                <td>
                  <span className={`badge ${o.status}`}>{o.status}</span>
                </td>
                <td>{saldoTotal > 0 ? `${saldoTotal} em aberto` : "cobertas"}</td>
                <td>{new Date(o.criado_em).toLocaleString("pt-BR")}</td>
              </tr>
            );
          })}
          {ocorrencias?.length === 0 && (
            <tr>
              <td colSpan={6} className="lista-vazia">
                Nenhuma ocorrência encontrada. Use o mapa para registrar uma nova ocorrência.
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
}
