import type L from "leaflet";
import { useMapEvents } from "react-leaflet";

export function CapturadorClique({ ativo, onClique }: { ativo: boolean; onClique: (latlng: L.LatLng) => void }) {
  useMapEvents({
    click(evento) {
      if (ativo) onClique(evento.latlng);
    },
  });
  return null;
}
