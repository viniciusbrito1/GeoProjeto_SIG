import { WMSTileLayer } from "react-leaflet";

const GEOSERVER_URL = (import.meta.env.VITE_GEOSERVER_URL as string | undefined) ?? "/geoserver";

export function CamadaGeoServer({ visivel, camada }: { visivel: boolean; camada: string }) {
  if (!visivel) return null;
  return (
    <WMSTileLayer
      url={`${GEOSERVER_URL}/wms`}
      layers={camada}
      format="image/png"
      transparent
      version="1.3.0"
      attribution="GeoServer / SISCOORD-DC"
    />
  );
}

// RF-15: consumir camada WMS externa sem que uma falha do provedor derrube o
// sistema — cada tile que falha simplesmente não é desenhado (comportamento
// nativo do <img> de tile); `onStatusChange` só torna essa realidade visível
// na UI (o painel de camadas mostra um aviso) em vez de deixá-la silenciosa.
export function CamadaExternaWMS({
  visivel,
  urlWms,
  camada,
  onStatusChange,
}: {
  visivel: boolean;
  urlWms: string;
  camada: string;
  onStatusChange?: (indisponivel: boolean) => void;
}) {
  if (!visivel) return null;
  return (
    <WMSTileLayer
      url={urlWms}
      layers={camada}
      format="image/png"
      transparent
      eventHandlers={{
        tileerror: () => onStatusChange?.(true),
        tileload: () => onStatusChange?.(false),
      }}
    />
  );
}
