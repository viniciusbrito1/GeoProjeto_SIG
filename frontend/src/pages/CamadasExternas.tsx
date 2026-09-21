import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { api, ErroApi } from "../api/client";
import type { CamadaExterna } from "../types";

// RF-15: gestão das camadas WMS de outros provedores que o mapa consome.
// Não existe exclusão — inativar tira a camada do mapa e mantém o histórico
// na trilha de auditoria (RF-13).
export function CamadasExternas() {
  const queryClient = useQueryClient();
  const { data: camadas, isLoading } = useQuery({
    queryKey: ["camadas-externas", "todas"],
    queryFn: () => api.get<CamadaExterna[]>("/camadas-externas?incluir_inativas=true"),
  });
  const alternarAtiva = useMutation({
    mutationFn: ({ id, ativa }: { id: string; ativa: boolean }) => api.patch<CamadaExterna>(`/camadas-externas/${id}`, { ativa }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["camadas-externas"] }),
  });

  const [modalAberto, setModalAberto] = useState(false);

  return (
    <div className="conteudo-padding">
      <div className="topo-pagina">
        <h1>Camadas externas (WMS)</h1>
        <button onClick={() => setModalAberto(true)}>+ Nova camada</button>
      </div>

      <p style={{ color: "var(--cinza-700)", marginTop: 0 }}>
        Camadas de outros provedores (IBGE, INDE etc.) exibidas no painel do mapa. Se um provedor sair do ar, o mapa
        continua funcionando e a camada aparece como "indisponível".
      </p>

      <table>
        <thead>
          <tr>
            <th>Nome</th>
            <th>URL do serviço WMS</th>
            <th>Camada</th>
            <th>Situação</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {isLoading && (
            <tr>
              <td colSpan={5}>Carregando...</td>
            </tr>
          )}
          {!isLoading && camadas?.length === 0 && (
            <tr>
              <td colSpan={5} className="lista-vazia">
                Nenhuma camada externa cadastrada.
              </td>
            </tr>
          )}
          {camadas?.map((c) => (
            <tr key={c.id}>
              <td>{c.nome}</td>
              <td style={{ wordBreak: "break-all" }}>{c.url_wms}</td>
              <td>{c.nome_camada}</td>
              <td>{c.ativa ? "Ativa" : "Inativa"}</td>
              <td>
                <button
                  className={c.ativa ? "perigo" : "secundario"}
                  onClick={() => alternarAtiva.mutate({ id: c.id, ativa: !c.ativa })}
                  disabled={alternarAtiva.isPending}
                >
                  {c.ativa ? "Inativar" : "Reativar"}
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      {modalAberto && <ModalNovaCamada onFechar={() => setModalAberto(false)} />}
    </div>
  );
}

function ModalNovaCamada({ onFechar }: { onFechar: () => void }) {
  const queryClient = useQueryClient();
  const criar = useMutation({
    mutationFn: (dados: { nome: string; url_wms: string; nome_camada: string }) => api.post<CamadaExterna>("/camadas-externas", dados),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["camadas-externas"] });
      onFechar();
    },
  });

  const [nome, setNome] = useState("");
  const [urlWms, setUrlWms] = useState("");
  const [nomeCamada, setNomeCamada] = useState("");
  const [erro, setErro] = useState<string | null>(null);

  async function aoSubmeter() {
    setErro(null);
    try {
      await criar.mutateAsync({ nome, url_wms: urlWms, nome_camada: nomeCamada });
    } catch (e) {
      setErro(e instanceof ErroApi ? e.message : "Não foi possível cadastrar a camada.");
    }
  }

  return (
    <div className="modal-fundo">
      <div className="modal-caixa">
        <h2>Nova camada externa</h2>
        {erro && <div className="erro-mensagem">{erro}</div>}
        <label>
          Nome exibido no mapa
          <input value={nome} onChange={(e) => setNome(e.target.value)} placeholder="Hidrografia (IBGE)" />
        </label>
        <label style={{ marginTop: 12 }}>
          URL do serviço WMS
          <input
            value={urlWms}
            onChange={(e) => setUrlWms(e.target.value)}
            placeholder="https://geoservicos.ibge.gov.br/geoserver/wms"
          />
        </label>
        <label style={{ marginTop: 12 }}>
          Nome da camada (como aparece no GetCapabilities)
          <input value={nomeCamada} onChange={(e) => setNomeCamada(e.target.value)} placeholder="CCAR:Hidrografia_2016" />
        </label>
        <div className="acoes-rodape">
          <button type="button" className="secundario" onClick={onFechar}>
            Cancelar
          </button>
          <button type="button" onClick={aoSubmeter} disabled={criar.isPending || !nome || !urlWms || !nomeCamada}>
            Cadastrar
          </button>
        </div>
      </div>
    </div>
  );
}
