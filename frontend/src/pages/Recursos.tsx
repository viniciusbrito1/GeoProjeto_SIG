import { useState } from "react";

import { ErroApi } from "../api/client";
import { useAlterarEstadoRecurso, useCriarRecurso, useInativarRecurso, useOrgaos, useRecursos } from "../api/hooks";
import { useAuth } from "../auth/AuthContext";
import { SeletorLocalizacao } from "../components/SeletorLocalizacao";
import { ROTULOS_ESTADO, ROTULOS_TIPO } from "../components/mapa/simbologia";
import type { TipoRecurso } from "../types";

export function Recursos() {
  const { temPerfil } = useAuth();
  const podeGerenciar = temPerfil("coordenador");
  const podeOperar = temPerfil("coordenador", "operador");

  const [filtroTipo, setFiltroTipo] = useState("");
  const [filtroEstado, setFiltroEstado] = useState("");
  const { data: recursos, isLoading } = useRecursos({ tipo: filtroTipo || undefined, estado: filtroEstado || undefined });
  const [modalAberto, setModalAberto] = useState(false);

  const alterarEstado = useAlterarEstadoRecurso();
  const inativar = useInativarRecurso();

  return (
    <div className="conteudo-padding">
      <div className="topo-pagina">
        <h1>Recursos</h1>
        {podeGerenciar && <button onClick={() => setModalAberto(true)}>+ Novo recurso</button>}
      </div>

      <div className="filtros">
        <label>
          Tipo
          <select value={filtroTipo} onChange={(e) => setFiltroTipo(e.target.value)}>
            <option value="">Todos</option>
            <option value="equipe">Equipe</option>
            <option value="instalacao">Instalação</option>
            <option value="equipamento">Equipamento</option>
          </select>
        </label>
        <label>
          Estado
          <select value={filtroEstado} onChange={(e) => setFiltroEstado(e.target.value)}>
            <option value="">Todos</option>
            <option value="disponivel">Disponível</option>
            <option value="empenhado">Empenhado</option>
            <option value="indisponivel">Indisponível</option>
            <option value="inativo">Inativo</option>
          </select>
        </label>
      </div>

      <table>
        <thead>
          <tr>
            <th>Nome</th>
            <th>Tipo</th>
            <th>Órgão</th>
            <th>Especialidade</th>
            <th>Estado</th>
            {podeOperar && <th></th>}
          </tr>
        </thead>
        <tbody>
          {isLoading && (
            <tr>
              <td colSpan={6}>Carregando...</td>
            </tr>
          )}
          {recursos?.map((r) => (
            <tr key={r.id}>
              <td>{r.nome}</td>
              <td>{ROTULOS_TIPO[r.tipo]}</td>
              <td>{r.orgao_sigla}</td>
              <td>{r.especialidade ?? "—"}</td>
              <td>
                <span className={`badge ${r.estado}`}>{ROTULOS_ESTADO[r.estado]}</span>
              </td>
              {podeOperar && (
                <td style={{ display: "flex", gap: 6 }}>
                  {r.estado === "disponivel" && (
                    <button
                      className="secundario"
                      onClick={() => alterarEstado.mutate({ id: r.id, estado: "indisponivel" })}
                    >
                      Marcar indisponível
                    </button>
                  )}
                  {r.estado === "indisponivel" && (
                    <button
                      className="secundario"
                      onClick={() => alterarEstado.mutate({ id: r.id, estado: "disponivel" })}
                    >
                      Marcar disponível
                    </button>
                  )}
                  {podeGerenciar && r.estado !== "empenhado" && r.estado !== "inativo" && (
                    <button className="perigo" onClick={() => inativar.mutate(r.id)}>
                      Inativar
                    </button>
                  )}
                </td>
              )}
            </tr>
          ))}
          {recursos?.length === 0 && (
            <tr>
              <td colSpan={6} className="lista-vazia">
                Nenhum recurso encontrado.
              </td>
            </tr>
          )}
        </tbody>
      </table>

      {modalAberto && <ModalNovoRecurso onFechar={() => setModalAberto(false)} />}
    </div>
  );
}

function ModalNovoRecurso({ onFechar }: { onFechar: () => void }) {
  const { data: orgaos } = useOrgaos();
  const criarRecurso = useCriarRecurso();

  const [tipo, setTipo] = useState<TipoRecurso>("equipamento");
  const [nome, setNome] = useState("");
  const [orgaoId, setOrgaoId] = useState("");
  const [especialidade, setEspecialidade] = useState("");
  const [capacidadeValor, setCapacidadeValor] = useState("");
  const [capacidadeUnidade, setCapacidadeUnidade] = useState("");
  const [lat, setLat] = useState<number | null>(null);
  const [lon, setLon] = useState<number | null>(null);
  const [erro, setErro] = useState<string | null>(null);
  const [enviando, setEnviando] = useState(false);

  async function aoSubmeter() {
    if (!orgaoId || lat == null || lon == null) {
      setErro("Preencha o órgão e clique no mapa para definir a localização.");
      return;
    }
    setErro(null);
    setEnviando(true);
    try {
      await criarRecurso.mutateAsync({
        tipo,
        nome,
        orgao_id: orgaoId,
        especialidade: especialidade || null,
        capacidade_valor: capacidadeValor ? Number(capacidadeValor) : null,
        capacidade_unidade: capacidadeUnidade || null,
        localizacao: { type: "Point", coordinates: [lon, lat] },
      });
      onFechar();
    } catch (e) {
      setErro(e instanceof ErroApi ? e.message : "Não foi possível cadastrar o recurso.");
    } finally {
      setEnviando(false);
    }
  }

  return (
    <div className="modal-fundo">
      <div className="modal-caixa">
        <h2>Novo recurso</h2>
        {erro && <div className="erro-mensagem">{erro}</div>}

        <div className="grade-formulario">
          <label>
            Tipo
            <select value={tipo} onChange={(e) => setTipo(e.target.value as TipoRecurso)}>
              <option value="equipe">Equipe</option>
              <option value="instalacao">Instalação</option>
              <option value="equipamento">Equipamento</option>
            </select>
          </label>
          <label>
            Órgão de origem
            <select value={orgaoId} onChange={(e) => setOrgaoId(e.target.value)}>
              <option value="">Selecione...</option>
              {orgaos?.map((o) => (
                <option key={o.id} value={o.id}>
                  {o.sigla}
                </option>
              ))}
            </select>
          </label>
        </div>

        <label style={{ marginTop: 14 }}>
          Nome
          <input value={nome} onChange={(e) => setNome(e.target.value)} placeholder="Ex.: Viatura de Resgate 01" />
        </label>

        <div className="grade-formulario" style={{ marginTop: 14 }}>
          <label>
            Especialidade
            <input value={especialidade} onChange={(e) => setEspecialidade(e.target.value)} />
          </label>
          <label>
            Capacidade
            <div style={{ display: "flex", gap: 6 }}>
              <input type="number" value={capacidadeValor} onChange={(e) => setCapacidadeValor(e.target.value)} />
              <input placeholder="unidade" value={capacidadeUnidade} onChange={(e) => setCapacidadeUnidade(e.target.value)} />
            </div>
          </label>
        </div>

        <label style={{ marginTop: 14 }}>
          Localização (clique no mapa)
          <SeletorLocalizacao
            lat={lat}
            lon={lon}
            onMudar={(novaLat, novoLon) => {
              setLat(novaLat);
              setLon(novoLon);
            }}
          />
        </label>

        <div className="acoes-rodape">
          <button type="button" className="secundario" onClick={onFechar}>
            Cancelar
          </button>
          <button type="button" onClick={aoSubmeter} disabled={enviando || !nome}>
            {enviando ? "Salvando..." : "Cadastrar"}
          </button>
        </div>
      </div>
    </div>
  );
}
