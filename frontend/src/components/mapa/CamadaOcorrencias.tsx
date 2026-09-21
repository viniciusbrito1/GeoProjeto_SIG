import { GeoJSON } from "react-leaflet";

import { useOcorrenciasGeoJSON } from "../../api/hooks";
import type { SeveridadeOcorrencia, StatusOcorrencia } from "../../types";
import { CORES_SEVERIDADE } from "./simbologia";

interface PropriedadesOcorrenciaFeature {
  id: string;
  tipo: string;
  severidade: SeveridadeOcorrencia;
  status: StatusOcorrencia;
  municipio_codigo_ibge: string;
}

export function CamadaOcorrencias({ visivel }: { visivel: boolean }) {
  const { data, dataUpdatedAt } = useOcorrenciasGeoJSON();

  if (!visivel || !data) return null;

  return (
    <GeoJSON
      key={`ocorrencias-${data.features.length}-${dataUpdatedAt}`}
      data={data as unknown as GeoJSON.GeoJsonObject}
      style={(feature) => {
        const p = feature?.properties as PropriedadesOcorrenciaFeature;
        const cor = CORES_SEVERIDADE[p.severidade] ?? "#c62828";
        return {
          color: cor,
          weight: 2,
          fillColor: cor,
          fillOpacity: p.status === "encerrada" ? 0.08 : 0.28,
          dashArray: p.status === "encerrada" ? "6 4" : undefined,
        };
      }}
      onEachFeature={(feature, layer) => {
        const p = feature.properties as PropriedadesOcorrenciaFeature;
        layer.bindPopup(
          `<div class="popup-ocorrencia"><b>${p.tipo}</b>` +
            `Severidade: ${p.severidade}<br/>` +
            `Status: ${p.status}<br/>` +
            `<a href="/ocorrencias/${p.id}">Ver detalhes »</a></div>`,
        );
      }}
    />
  );
}
