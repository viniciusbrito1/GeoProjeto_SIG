import { Marker, MapContainer, TileLayer, useMapEvents } from "react-leaflet";

const CENTRO_INICIAL: [number, number] = [-20.05, -40.55];

function CapturaClique({ onEscolher }: { onEscolher: (lat: number, lon: number) => void }) {
  useMapEvents({
    click(e) {
      onEscolher(e.latlng.lat, e.latlng.lng);
    },
  });
  return null;
}

export function SeletorLocalizacao({
  lat,
  lon,
  onMudar,
}: {
  lat: number | null;
  lon: number | null;
  onMudar: (lat: number, lon: number) => void;
}) {
  const centro: [number, number] = lat != null && lon != null ? [lat, lon] : CENTRO_INICIAL;

  return (
    <div style={{ height: 220, borderRadius: 6, overflow: "hidden", border: "1px solid var(--cinza-300)" }}>
      <MapContainer center={centro} zoom={lat != null ? 12 : 8} style={{ height: "100%", width: "100%" }}>
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        <CapturaClique onEscolher={onMudar} />
        {lat != null && lon != null && <Marker position={[lat, lon]} />}
      </MapContainer>
    </div>
  );
}
