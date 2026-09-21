import L from "leaflet";
import { useEffect, useRef } from "react";
import { useMap } from "react-leaflet";

interface Props {
  ativo: boolean;
  onDesenhado: (poligono: GeoJSON.Polygon) => void;
}

const COR_LINHA = "#c62828";
const MINIMO_PONTOS = 3;

// Implementação própria de desenho de polígono — a lib leaflet-draw (não
// mantida desde ~2021) lança "ReferenceError: type is not defined" a cada
// clique quando processada pelo pre-bundling do Vite (código antigo que
// pressupõe modo não-estrito); o efeito colateral observado era o desenho
// terminar sozinho sempre com 3 pontos. Clique esquerdo adiciona vértice,
// clique direito finaliza (em vez do duplo-clique do leaflet-draw, que
// também brigava com o zoom-por-duplo-clique nativo do Leaflet).
export function FerramentaDesenho({ ativo, onDesenhado }: Props) {
  const map = useMap();
  const pontosRef = useRef<L.LatLng[]>([]);
  const linhaRef = useRef<L.Polyline | null>(null);
  const previaRef = useRef<L.Polyline | null>(null);
  const verticesRef = useRef<L.CircleMarker[]>([]);

  useEffect(() => {
    if (!ativo) return;

    function limpar() {
      pontosRef.current = [];
      linhaRef.current?.remove();
      linhaRef.current = null;
      previaRef.current?.remove();
      previaRef.current = null;
      verticesRef.current.forEach((v) => v.remove());
      verticesRef.current = [];
    }

    function redesenharContorno() {
      linhaRef.current?.remove();
      linhaRef.current =
        pontosRef.current.length >= 2
          ? L.polyline(pontosRef.current, { color: COR_LINHA, weight: 2 }).addTo(map)
          : null;
    }

    function aoClicar(evento: L.LeafletMouseEvent) {
      pontosRef.current.push(evento.latlng);
      verticesRef.current.push(
        L.circleMarker(evento.latlng, { radius: 5, color: COR_LINHA, weight: 2, fillColor: "#fff", fillOpacity: 1 }).addTo(map),
      );
      redesenharContorno();
    }

    function aoMoverMouse(evento: L.LeafletMouseEvent) {
      previaRef.current?.remove();
      previaRef.current = null;
      if (pontosRef.current.length === 0) return;
      const ultimoPonto = pontosRef.current[pontosRef.current.length - 1];
      previaRef.current = L.polyline([ultimoPonto, evento.latlng], {
        color: COR_LINHA,
        weight: 1.5,
        dashArray: "4 4",
      }).addTo(map);
    }

    function aoClicarComBotaoDireito(evento: L.LeafletMouseEvent) {
      evento.originalEvent.preventDefault();
      if (pontosRef.current.length < MINIMO_PONTOS) return;
      const anel = pontosRef.current.map((ponto): [number, number] => [ponto.lng, ponto.lat]);
      anel.push(anel[0]);
      onDesenhado({ type: "Polygon", coordinates: [anel] });
      limpar();
    }

    function aoPressionarTecla(evento: KeyboardEvent) {
      if (evento.key === "Escape") limpar();
    }

    map.doubleClickZoom.disable();
    map.on("click", aoClicar);
    map.on("mousemove", aoMoverMouse);
    map.on("contextmenu", aoClicarComBotaoDireito);
    document.addEventListener("keydown", aoPressionarTecla);

    return () => {
      map.doubleClickZoom.enable();
      map.off("click", aoClicar);
      map.off("mousemove", aoMoverMouse);
      map.off("contextmenu", aoClicarComBotaoDireito);
      document.removeEventListener("keydown", aoPressionarTecla);
      limpar();
    };
  }, [ativo, map, onDesenhado]);

  return null;
}
