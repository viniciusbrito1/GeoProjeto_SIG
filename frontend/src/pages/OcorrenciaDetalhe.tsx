import { useState } from "react";
import { useParams } from "react-router-dom";

import { baixarArquivo, ErroApi } from "../api/client";
import {
  useEmpenharRecurso,
  useEmpenhosDaOcorrencia,
  useEncerrarOcorrencia,
  useLiberarEmpenho,
  useOcorrencia,
  useRecursosCompativeis,
} from "../api/hooks";
import { useAuth } from "../auth/AuthContext";
import { ROTULOS_TIPO } from "../components/mapa/simbologia";
import type { Demanda } from "../types";

export function OcorrenciaDetalhe() {
  const { id } = useParams<{ id: string }>();
  const { temPerfil } = useAuth();
  const podeOperar = temPerfil("coordenador", "operador");

  const { data: ocorrencia } = useOcorrencia(id);
  const { data: empenhos } = useEmpenhosDaOcorrencia(id);
  const encerrar = useEncerrarOcorrencia();
  const liberar = useLiberarEmpenho();

  const [demandaEmpenhando, setDemandaEmpenhando] = useState<Demanda | null>(null);
  const [erro, setErro] = useState<string | null>(null);

  if (!ocorrencia) return <div className="conteudo-padding">Carregando...</div>;

  async function aoEncerrar() {
    setErro(null);
    try {
      await encerrar.mutateAsync(ocorrencia!.id);
    } catch (e) {
      setErro(e instanceof ErroApi ? e.message : "Não foi possível encerrar a ocorrência.");
    }
  }

  return (
    <div className="conteudo-padding">
      <div className="topo-pagina">
        <div>
          <h1>{ocorrencia.tipo}</h1>
          <div style={{ display: "flex", gap: 8, marginTop: 6 }}>
            <span className={`badge ${ocorrencia.severidade}`}>{ocorrencia.severidade}</span>
            <span className={`badge ${ocorrencia.status}`}>{ocorrencia.status}</span>
          </div>
        </div>
        <div style={{ display: "flex", gap: 8 }}>
          <button className="secundario" onClick={() => baixarArquivo(`/ocorrencias/${ocorrencia.id}/sitrep.pdf`, `sitrep_${ocorrencia.id}.pdf`)}>
            📄 SITREP (PDF)
          </button>
          <button
            className="secundario"
            onClick={() => baixarArquivo(`/ocorrencias/${ocorrencia.id}/exportar?formato=geojson`, `ocorrencia_${ocorrencia.id}.geojson`)}
          >
            Exportar GeoJSON
          </button>
          <button
            className="secundario"
            onClick={() => baixarArquivo(`/ocorrencias/${ocorrencia.id}/exportar?formato=gpkg`, `ocorrencia_${ocorrencia.id}.gpkg`)}
          >
            Exportar GeoPackage
          </button>
          {podeOperar && ocorrencia.status === "aberta" && (
            <button className="perigo" onClick={aoEncerrar}>
              Encerrar ocorrência
            </button>
          )}
        </div>
      </div>

      {erro && <div className="erro-mensagem">{erro}</div>}

      <div className="cartao" style={{ marginBottom: 18 }}>
        <p>
          <b>Município:</b> {ocorrencia.municipio_nome} ({ocorrencia.municipio_codigo_ibge}) &nbsp;·&nbsp;
          <b>Aberta em:</b> {new Date(ocorrencia.criado_em).toLocaleString("pt-BR")}
        </p>
        {ocorrencia.descricao && <p>{ocorrencia.descricao}</p>}
      </div>

      <h3>Demandas e cobertura (RF-04)</h3>
      <table>
        <thead>
          <tr>
            <th>Tipo</th>
            <th>Especialidade</th>
            <th>Necessário</th>
            <th>Empenhado</th>
            <th>Saldo descoberto</th>
            {podeOperar && ocorrencia.status === "aberta" && <th></th>}
          </tr>
        </thead>
        <tbody>
          {ocorrencia.demandas.map((d) => (
            <tr key={d.id}>
              <td>{ROTULOS_TIPO[d.tipo_recurso]}</td>
              <td>{d.especialidade ?? "—"}</td>
              <td>{d.quantidade_necessaria}</td>
              <td>{d.quantidade_empenhada}</td>
              <td style={{ color: d.saldo_descoberto > 0 ? "var(--vermelho)" : "var(--verde)", fontWeight: 700 }}>
                {d.saldo_descoberto}
              </td>
              {podeOperar && ocorrencia.status === "aberta" && (
                <td>
                  {d.saldo_descoberto > 0 && <button onClick={() => setDemandaEmpenhando(d)}>Empenhar recurso</button>}
                </td>
              )}
            </tr>
          ))}
          {ocorrencia.demandas.length === 0 && (
            <tr>
              <td colSpan={6} className="lista-vazia">
                Nenhuma demanda registrada.
              </td>
            </tr>
          )}
        </tbody>
      </table>

      <h3 style={{ marginTop: 24 }}>Recursos empenhados (RF-05)</h3>
      <table>
        <thead>
          <tr>
            <th>Recurso</th>
            <th>Status</th>
            <th>Empenhado em</th>
            <th>Liberado em</th>
            {podeOperar && <th></th>}
          </tr>
        </thead>
        <tbody>
          {empenhos?.map((e) => (
            <tr key={e.id}>
              <td>{e.recurso_nome}</td>
              <td>
                <span className={`badge ${e.status}`}>{e.status}</span>
              </td>
              <td>{new Date(e.empenhado_em).toLocaleString("pt-BR")}</td>
              <td>{e.liberado_em ? new Date(e.liberado_em).toLocaleString("pt-BR") : "—"}</td>
              {podeOperar && (
                <td>
                  {e.status === "ativo" && (
                    <button className="secundario" onClick={() => liberar.mutate(e.id)}>
                      Liberar
                    </button>
                  )}
                </td>
              )}
            </tr>
          ))}
          {empenhos?.length === 0 && (
            <tr>
              <td colSpan={5} className="lista-vazia">
                Nenhum recurso empenhado ainda.
              </td>
            </tr>
          )}
        </tbody>
      </table>

      {demandaEmpenhando && (
        <ModalEmpenhar demanda={demandaEmpenhando} ocorrenciaId={ocorrencia.id} onFechar={() => setDemandaEmpenhando(null)} />
      )}
    </div>
  );
}

function ModalEmpenhar({ demanda, ocorrenciaId, onFechar }: { demanda: Demanda; ocorrenciaId: string; onFechar: () => void }) {
  const { data: compativeis, isLoading } = useRecursosCompativeis(demanda.id);
  const empenhar = useEmpenharRecurso();
  const [erro, setErro] = useState<string | null>(null);

  async function aoEscolher(recursoId: string) {
    setErro(null);
    try {
      await empenhar.mutateAsync({ recurso_id: recursoId, ocorrencia_id: ocorrenciaId, demanda_id: demanda.id });
      onFechar();
    } catch (e) {
      setErro(e instanceof ErroApi ? e.message : "Não foi possível empenhar este recurso.");
    }
  }

  return (
    <div className="modal-fundo">
      <div className="modal-caixa">
        <h2>Empenhar recurso</h2>
        <p style={{ fontSize: 13, color: "var(--cinza-700)" }}>
          {ROTULOS_TIPO[demanda.tipo_recurso]}
          {demanda.especialidade && ` · ${demanda.especialidade}`} — ordenado pela distância até a área atingida (RF-06).
        </p>
        {erro && <div className="erro-mensagem">{erro}</div>}
        {isLoading && <p>Carregando recursos compatíveis...</p>}
        {compativeis?.length === 0 && <p className="lista-vazia">Nenhum recurso disponível compatível com esta demanda.</p>}
        {compativeis?.map((r) => (
          <div key={r.id} className="cartao" style={{ marginBottom: 8, display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <div>
              <b>{r.nome}</b>
              <div style={{ fontSize: 12, color: "var(--cinza-700)" }}>
                {r.orgao_sigla} {r.distancia_m != null && `· ${(r.distancia_m / 1000).toFixed(1)} km`}
              </div>
            </div>
            <button onClick={() => aoEscolher(r.id)} disabled={empenhar.isPending}>
              Empenhar
            </button>
          </div>
        ))}
        <div className="acoes-rodape">
          <button type="button" className="secundario" onClick={onFechar}>
            Fechar
          </button>
        </div>
      </div>
    </div>
  );
}
