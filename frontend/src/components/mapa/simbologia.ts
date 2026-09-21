import L from "leaflet";

import type { EstadoRecurso, TipoRecurso } from "../../types";

// RF-09: tipo e estado devem ser distinguíveis ao mesmo tempo — forma = tipo, cor = estado.
export const CORES_ESTADO: Record<EstadoRecurso, string> = {
  disponivel: "#2e7d32",
  empenhado: "#e65100",
  indisponivel: "#757575",
  inativo: "#1a1d21",
};

export const ROTULOS_ESTADO: Record<EstadoRecurso, string> = {
  disponivel: "Disponível",
  empenhado: "Empenhado",
  indisponivel: "Indisponível",
  inativo: "Inativo",
};

export const ROTULOS_TIPO: Record<TipoRecurso, string> = {
  equipe: "Equipe",
  instalacao: "Instalação",
  equipamento: "Equipamento",
};

export const CORES_SEVERIDADE: Record<string, string> = {
  baixa: "#f9a825",
  media: "#e65100",
  alta: "#c62828",
  critica: "#6a1b9a",
};

function formaSvg(tipo: TipoRecurso, cor: string): string {
  switch (tipo) {
    case "equipe":
      return `<circle cx="12" cy="12" r="9" fill="${cor}" stroke="#ffffff" stroke-width="2"/>`;
    case "instalacao":
      return `<rect x="3" y="3" width="18" height="18" rx="2" fill="${cor}" stroke="#ffffff" stroke-width="2"/>`;
    case "equipamento":
      return `<polygon points="12,2 22,21 2,21" fill="${cor}" stroke="#ffffff" stroke-width="2"/>`;
  }
}

export function iconeRecurso(tipo: TipoRecurso, estado: EstadoRecurso): L.DivIcon {
  const svg = `<svg width="24" height="24" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">${formaSvg(tipo, CORES_ESTADO[estado])}</svg>`;
  return L.divIcon({
    html: svg,
    className: "icone-recurso",
    iconSize: [24, 24],
    iconAnchor: [12, 12],
    popupAnchor: [0, -14],
  });
}

export function svgLegendaForma(tipo: TipoRecurso): string {
  return `<svg width="16" height="16" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">${formaSvg(tipo, "#4a4f57")}</svg>`;
}
