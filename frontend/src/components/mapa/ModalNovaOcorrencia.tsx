import { useState } from "react";

import { useCriarOcorrencia, useMunicipios } from "../../api/hooks";
import { ErroApi } from "../../api/client";
import type { SeveridadeOcorrencia, TipoRecurso } from "../../types";

interface LinhaDemanda {
  tipo_recurso: TipoRecurso;
  especialidade: string;
  quantidade_necessaria: number;
}

export function ModalNovaOcorrencia({
  poligono,
  onFechar,
  onCriado,
}: {
  poligono: GeoJSON.Polygon;
  onFechar: () => void;
  onCriado: () => void;
}) {
  const { data: municipios } = useMunicipios();
  const criarOcorrencia = useCriarOcorrencia();

  const [tipo, setTipo] = useState("Alagamento");
  const [severidade, setSeveridade] = useState<SeveridadeOcorrencia>("media");
  const [municipioCodigo, setMunicipioCodigo] = useState("");
  const [descricao, setDescricao] = useState("");
  const [demandas, setDemandas] = useState<LinhaDemanda[]>([{ tipo_recurso: "equipe", especialidade: "", quantidade_necessaria: 1 }]);
  const [erro, setErro] = useState<string | null>(null);
  const [enviando, setEnviando] = useState(false);

  function atualizarDemanda(indice: number, campo: keyof LinhaDemanda, valor: string | number) {
    setDemandas((atual) => atual.map((d, i) => (i === indice ? { ...d, [campo]: valor } : d)));
  }

  async function aoSubmeter() {
    if (!municipioCodigo) {
      setErro("Selecione o município atingido.");
      return;
    }
    setErro(null);
    setEnviando(true);
    try {
      await criarOcorrencia.mutateAsync({
        tipo,
        severidade,
        municipio_codigo_ibge: municipioCodigo,
        area_atingida: poligono,
        descricao: descricao || null,
        demandas: demandas
          .filter((d) => d.quantidade_necessaria > 0)
          .map((d) => ({ ...d, especialidade: d.especialidade || null })),
      });
      onCriado();
    } catch (e) {
      setErro(e instanceof ErroApi ? e.message : "Não foi possível registrar a ocorrência.");
    } finally {
      setEnviando(false);
    }
  }

  return (
    <div className="modal-fundo">
      <div className="modal-caixa">
        <h2>Nova ocorrência</h2>
        {erro && <div className="erro-mensagem">{erro}</div>}

        <div className="grade-formulario">
          <label>
            Tipo
            <input value={tipo} onChange={(e) => setTipo(e.target.value)} />
          </label>
          <label>
            Severidade
            <select value={severidade} onChange={(e) => setSeveridade(e.target.value as SeveridadeOcorrencia)}>
              <option value="baixa">Baixa</option>
              <option value="media">Média</option>
              <option value="alta">Alta</option>
              <option value="critica">Crítica</option>
            </select>
          </label>
        </div>

        <label style={{ marginTop: 14 }}>
          Município atingido
          <select value={municipioCodigo} onChange={(e) => setMunicipioCodigo(e.target.value)}>
            <option value="">Selecione...</option>
            {municipios?.map((m) => (
              <option key={m.codigo_ibge} value={m.codigo_ibge}>
                {m.nome}/{m.uf}
              </option>
            ))}
          </select>
        </label>

        <label style={{ marginTop: 14 }}>
          Descrição
          <textarea rows={2} value={descricao} onChange={(e) => setDescricao(e.target.value)} />
        </label>

        <h3 style={{ marginTop: 18, fontSize: 13, color: "var(--cinza-700)" }}>Demandas (RF-04)</h3>
        {demandas.map((d, i) => (
          <div className="grade-formulario" key={i} style={{ marginBottom: 8, gridTemplateColumns: "1fr 1fr 90px 30px" }}>
            <select value={d.tipo_recurso} onChange={(e) => atualizarDemanda(i, "tipo_recurso", e.target.value)}>
              <option value="equipe">Equipe</option>
              <option value="instalacao">Instalação</option>
              <option value="equipamento">Equipamento</option>
            </select>
            <input
              placeholder="Especialidade (opcional)"
              value={d.especialidade}
              onChange={(e) => atualizarDemanda(i, "especialidade", e.target.value)}
            />
            <input
              type="number"
              min={1}
              value={d.quantidade_necessaria}
              onChange={(e) => atualizarDemanda(i, "quantidade_necessaria", Number(e.target.value))}
            />
            <button type="button" className="secundario" onClick={() => setDemandas((atual) => atual.filter((_, idx) => idx !== i))}>
              ×
            </button>
          </div>
        ))}
        <button
          type="button"
          className="secundario"
          onClick={() => setDemandas((atual) => [...atual, { tipo_recurso: "equipe", especialidade: "", quantidade_necessaria: 1 }])}
        >
          + Adicionar demanda
        </button>

        <div className="acoes-rodape">
          <button type="button" className="secundario" onClick={onFechar}>
            Cancelar
          </button>
          <button type="button" onClick={aoSubmeter} disabled={enviando}>
            {enviando ? "Salvando..." : "Registrar ocorrência"}
          </button>
        </div>
      </div>
    </div>
  );
}
