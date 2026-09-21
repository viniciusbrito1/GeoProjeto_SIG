import { CORES_ESTADO, CORES_SEVERIDADE, ROTULOS_ESTADO, ROTULOS_TIPO, svgLegendaForma } from "./simbologia";
import type { TipoRecurso } from "../../types";

export function Legenda() {
  return (
    <div>
      <h3>Recursos · forma = tipo</h3>
      {(Object.keys(ROTULOS_TIPO) as TipoRecurso[]).map((tipo) => (
        <div className="item-camada" key={tipo}>
          <span dangerouslySetInnerHTML={{ __html: svgLegendaForma(tipo) }} />
          {ROTULOS_TIPO[tipo]}
        </div>
      ))}

      <h3>Recursos · cor = estado</h3>
      {Object.entries(ROTULOS_ESTADO).map(([estado, rotulo]) => (
        <div className="item-camada" key={estado}>
          <span className="legenda-simbolo" style={{ background: CORES_ESTADO[estado as keyof typeof CORES_ESTADO] }} />
          {rotulo}
        </div>
      ))}

      <h3>Ocorrências · severidade</h3>
      {Object.entries(CORES_SEVERIDADE).map(([severidade, cor]) => (
        <div className="item-camada" key={severidade}>
          <span className="legenda-simbolo" style={{ background: cor }} />
          {severidade}
        </div>
      ))}
    </div>
  );
}
