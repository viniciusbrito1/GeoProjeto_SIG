import L from "leaflet";
import { useMemo, useState } from "react";
import { Circle, MapContainer, TileLayer } from "react-leaflet";

import { useCamadasExternas, useRecursos } from "../api/hooks";
import { useAuth } from "../auth/AuthContext";
import { CamadaOcorrencias } from "../components/mapa/CamadaOcorrencias";
import { CamadaRecursos } from "../components/mapa/CamadaRecursos";
import { CamadaExternaWMS, CamadaGeoServer } from "../components/mapa/CamadaWMS";
import { CapturadorClique } from "../components/mapa/CapturadorClique";
import { FerramentaDesenho } from "../components/mapa/FerramentaDesenho";
import { Legenda } from "../components/mapa/Legenda";
import { ModalNovaOcorrencia } from "../components/mapa/ModalNovaOcorrencia";
import { ROTULOS_ESTADO, ROTULOS_TIPO } from "../components/mapa/simbologia";

const CENTRO_INICIAL: [number, number] = [-20.05, -40.55]; // Espírito Santo

type Modo = "navegar" | "desenhar-ocorrencia" | "buscar-raio";

export function Mapa() {
  const { temPerfil } = useAuth();
  const podeOperar = temPerfil("coordenador", "operador");

  const [modo, setModo] = useState<Modo>("navegar");
  const [poligonoDesenhado, setPoligonoDesenhado] = useState<GeoJSON.Polygon | null>(null);
  const [centroBusca, setCentroBusca] = useState<L.LatLng | null>(null);
  const [raioKm, setRaioKm] = useState(10);

  const [camadas, setCamadas] = useState({
    recursos: true,
    ocorrencias: true,
    geoServerRecursos: false,
    geoServerOcorrencias: false,
  });
  const { data: camadasExternas } = useCamadasExternas();
  const [externasVisiveis, setExternasVisiveis] = useState<Record<string, boolean>>({});
  const [externasIndisponiveis, setExternasIndisponiveis] = useState<Record<string, boolean>>({});

  const filtrosBusca = useMemo(
    () =>
      centroBusca
        ? { lat: centroBusca.lat, lon: centroBusca.lng, raio_m: raioKm * 1000, estado: "disponivel" }
        : undefined,
    [centroBusca, raioKm],
  );
  const { data: resultadosBusca } = useRecursos(filtrosBusca ?? {});

  function alternarCamada(chave: keyof typeof camadas) {
    setCamadas((atual) => ({ ...atual, [chave]: !atual[chave] }));
  }

  function iniciarModo(novoModo: Modo) {
    setModo((atual) => (atual === novoModo ? "navegar" : novoModo));
    setPoligonoDesenhado(null);
    setCentroBusca(null);
  }

  return (
    <div className="mapa-shell">
      <div className="mapa-container">
        <div className="ferramentas-mapa">
          {podeOperar && (
            <button className={modo === "desenhar-ocorrencia" ? "" : "secundario"} onClick={() => iniciarModo("desenhar-ocorrencia")}>
              ✏️ Nova ocorrência
            </button>
          )}
          {/* RF-07 é leitura — disponível para os três perfis, inclusive Consulta */}
          <button className={modo === "buscar-raio" ? "" : "secundario"} onClick={() => iniciarModo("buscar-raio")}>
            🎯 Buscar por raio (RF-07)
          </button>
        </div>

        {modo === "desenhar-ocorrencia" && (
          <div className="dica-desenho">
            Clique no mapa para adicionar pontos da área atingida. Clique com o botão direito para finalizar
            (mínimo 3 pontos) · Esc cancela.
          </div>
        )}

        <MapContainer center={CENTRO_INICIAL} zoom={8} style={{ height: "100%", width: "100%" }}>
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />

          <CamadaRecursos visivel={camadas.recursos} />
          <CamadaOcorrencias visivel={camadas.ocorrencias} />
          <CamadaGeoServer visivel={camadas.geoServerRecursos} camada="siscoord:recursos" />
          <CamadaGeoServer visivel={camadas.geoServerOcorrencias} camada="siscoord:ocorrencias" />

          {camadasExternas?.map((c) => (
            <CamadaExternaWMS
              key={c.id}
              visivel={!!externasVisiveis[c.id]}
              urlWms={c.url_wms}
              camada={c.nome_camada}
              onStatusChange={(indisponivel) => setExternasIndisponiveis((atual) => ({ ...atual, [c.id]: indisponivel }))}
            />
          ))}

          <FerramentaDesenho ativo={modo === "desenhar-ocorrencia"} onDesenhado={setPoligonoDesenhado} />
          <CapturadorClique ativo={modo === "buscar-raio"} onClique={setCentroBusca} />
          {centroBusca && <Circle center={centroBusca} radius={raioKm * 1000} pathOptions={{ color: "#2f6690" }} />}
        </MapContainer>
      </div>

      <div className="painel-camadas">
        <h3 style={{ marginTop: 0 }}>Camadas operacionais</h3>
        <div className="item-camada">
          <input type="checkbox" checked={camadas.recursos} onChange={() => alternarCamada("recursos")} />
          Recursos (tempo real)
        </div>
        <div className="item-camada">
          <input type="checkbox" checked={camadas.ocorrencias} onChange={() => alternarCamada("ocorrencias")} />
          Áreas atingidas
        </div>

        <h3>Camadas OGC · GeoServer (RF-11)</h3>
        <div className="item-camada">
          <input type="checkbox" checked={camadas.geoServerRecursos} onChange={() => alternarCamada("geoServerRecursos")} />
          WMS: recursos
        </div>
        <div className="item-camada">
          <input type="checkbox" checked={camadas.geoServerOcorrencias} onChange={() => alternarCamada("geoServerOcorrencias")} />
          WMS: ocorrências
        </div>

        {camadasExternas && camadasExternas.length > 0 && (
          <>
            <h3>Camadas externas (RF-15)</h3>
            {camadasExternas.map((c) => (
              <div className="item-camada" key={c.id}>
                <input
                  type="checkbox"
                  checked={!!externasVisiveis[c.id]}
                  onChange={() => setExternasVisiveis((atual) => ({ ...atual, [c.id]: !atual[c.id] }))}
                />
                {c.nome}
                {externasIndisponiveis[c.id] && externasVisiveis[c.id] && (
                  <span style={{ color: "var(--vermelho)", fontSize: 11 }}> (indisponível)</span>
                )}
              </div>
            ))}
          </>
        )}

        <Legenda />

        {modo === "buscar-raio" && (
          <>
            <h3>Busca por raio</h3>
            <p style={{ fontSize: 12.5, color: "var(--cinza-700)" }}>Clique no mapa para definir o centro.</p>
            <label>
              Raio: {raioKm} km
              <input type="range" min={1} max={100} value={raioKm} onChange={(e) => setRaioKm(Number(e.target.value))} />
            </label>
            {centroBusca && (
              <div style={{ marginTop: 10 }}>
                {(resultadosBusca ?? []).length === 0 && <p className="lista-vazia">Nenhum recurso disponível no raio.</p>}
                {resultadosBusca?.map((r) => (
                  <div key={r.id} className="cartao" style={{ marginBottom: 8, padding: 10 }}>
                    <b>{r.nome}</b>
                    <div style={{ fontSize: 12, color: "var(--cinza-700)" }}>
                      {ROTULOS_TIPO[r.tipo]} · {ROTULOS_ESTADO[r.estado]}
                      {r.distancia_m != null && <> · {(r.distancia_m / 1000).toFixed(1)} km</>}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </>
        )}
      </div>

      {poligonoDesenhado && (
        <ModalNovaOcorrencia
          poligono={poligonoDesenhado}
          onFechar={() => {
            setPoligonoDesenhado(null);
            setModo("navegar");
          }}
          onCriado={() => {
            setPoligonoDesenhado(null);
            setModo("navegar");
          }}
        />
      )}
    </div>
  );
}
