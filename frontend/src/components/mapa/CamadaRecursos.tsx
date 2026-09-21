import L from "leaflet";
import { GeoJSON } from "react-leaflet";

import { useRecursosGeoJSON } from "../../api/hooks";
import type { EstadoRecurso, TipoRecurso } from "../../types";
import { iconeRecurso, ROTULOS_ESTADO, ROTULOS_TIPO } from "./simbologia";

interface PropriedadesRecursoFeature {
  id: string;
  nome: string;
  tipo: TipoRecurso;
  estado: EstadoRecurso;
  orgao: string | null;
  especialidade: string | null;
}

export function CamadaRecursos({ visivel }: { visivel: boolean }) {
  const { data, dataUpdatedAt } = useRecursosGeoJSON();

  if (!visivel || !data) return null;

  return (
    <GeoJSON
      // react-leaflet não faz diff da prop `data` de um GeoJSON já montado
      // (limitação conhecida da lib) — a key força remontar a cada poll do
      // RF-10, garantindo que estado/posição fiquem sempre em dia.
      key={`recursos-${data.features.length}-${dataUpdatedAt}`}
      data={data as unknown as GeoJSON.GeoJsonObject}
      pointToLayer={(feature, latlng) => {
        const props = feature.properties as PropriedadesRecursoFeature;
        return L.marker(latlng, { icon: iconeRecurso(props.tipo, props.estado) });
      }}
      onEachFeature={(feature, layer) => {
        const p = feature.properties as PropriedadesRecursoFeature;
        layer.bindPopup(
          `<div class="popup-recurso"><b>${p.nome}</b>` +
            `Tipo: ${ROTULOS_TIPO[p.tipo]}<br/>` +
            `Estado: ${ROTULOS_ESTADO[p.estado]}<br/>` +
            `Órgão: ${p.orgao ?? "—"}<br/>` +
            (p.especialidade ? `Especialidade: ${p.especialidade}` : "") +
            `</div>`,
        );
      }}
    />
  );
}
