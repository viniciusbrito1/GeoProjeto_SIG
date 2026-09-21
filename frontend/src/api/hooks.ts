import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { api } from "./client";
import type {
  AuditoriaRegistro,
  CamadaExterna,
  Demanda,
  Empenho,
  FeatureCollectionGeoJSON,
  Municipio,
  Ocorrencia,
  Orgao,
  Recurso,
} from "../types";

// RF-10: refletir mudanças em outras sessões em <=60s sem recarregar a página
// manualmente — 20s dá bastante folga sob a exigência e ainda é leve para a
// API (RNF-04 já garante que cada consulta responde em poucos segundos).
const INTERVALO_ATUALIZACAO_MS = 20_000;

export function useOrgaos() {
  return useQuery({ queryKey: ["orgaos"], queryFn: () => api.get<Orgao[]>("/orgaos") });
}

export function useMunicipios() {
  return useQuery({ queryKey: ["municipios"], queryFn: () => api.get<Municipio[]>("/municipios") });
}

export function useCamadasExternas() {
  return useQuery({ queryKey: ["camadas-externas"], queryFn: () => api.get<CamadaExterna[]>("/camadas-externas") });
}

export function useRecursos(filtros: Record<string, string | number | boolean | undefined> = {}) {
  const query = new URLSearchParams();
  Object.entries(filtros).forEach(([chave, valor]) => {
    if (valor !== undefined && valor !== "") query.set(chave, String(valor));
  });
  const sufixo = query.toString() ? `?${query.toString()}` : "";
  return useQuery({
    queryKey: ["recursos", filtros],
    queryFn: () => api.get<Recurso[]>(`/recursos${sufixo}`),
    refetchInterval: INTERVALO_ATUALIZACAO_MS,
  });
}

export function useRecursosGeoJSON() {
  return useQuery({
    queryKey: ["recursos-geojson"],
    queryFn: () => api.get<FeatureCollectionGeoJSON>("/recursos/geojson"),
    refetchInterval: INTERVALO_ATUALIZACAO_MS,
  });
}

export function useOcorrenciasGeoJSON() {
  return useQuery({
    queryKey: ["ocorrencias-geojson"],
    queryFn: () => api.get<FeatureCollectionGeoJSON>("/ocorrencias/geojson"),
    refetchInterval: INTERVALO_ATUALIZACAO_MS,
  });
}

export function useOcorrencias(statusFiltro?: string) {
  const sufixo = statusFiltro ? `?status_filtro=${statusFiltro}` : "";
  return useQuery({
    queryKey: ["ocorrencias", statusFiltro],
    queryFn: () => api.get<Ocorrencia[]>(`/ocorrencias${sufixo}`),
    refetchInterval: INTERVALO_ATUALIZACAO_MS,
  });
}

export function useOcorrencia(id: string | undefined) {
  return useQuery({
    queryKey: ["ocorrencia", id],
    queryFn: () => api.get<Ocorrencia>(`/ocorrencias/${id}`),
    enabled: !!id,
    refetchInterval: INTERVALO_ATUALIZACAO_MS,
  });
}

export function useEmpenhosDaOcorrencia(id: string | undefined) {
  return useQuery({
    queryKey: ["empenhos", id],
    queryFn: () => api.get<Empenho[]>(`/ocorrencias/${id}/empenhos`),
    enabled: !!id,
    refetchInterval: INTERVALO_ATUALIZACAO_MS,
  });
}

export function useRecursosCompativeis(demandaId: string | undefined) {
  return useQuery({
    queryKey: ["recursos-compativeis", demandaId],
    queryFn: () => api.get<Recurso[]>(`/recursos/compativeis/${demandaId}`),
    enabled: !!demandaId,
  });
}

export function useAuditoria(filtros: Record<string, string | undefined> = {}) {
  const query = new URLSearchParams();
  Object.entries(filtros).forEach(([chave, valor]) => valor && query.set(chave, valor));
  const sufixo = query.toString() ? `?${query.toString()}` : "";
  return useQuery({ queryKey: ["auditoria", filtros], queryFn: () => api.get<AuditoriaRegistro[]>(`/auditoria${sufixo}`) });
}

function useInvalidarPainelOperacional() {
  const queryClient = useQueryClient();
  return () =>
    Promise.all(
      ["recursos", "recursos-geojson", "ocorrencias", "ocorrencias-geojson", "ocorrencia", "empenhos", "recursos-compativeis"].map(
        (chave) => queryClient.invalidateQueries({ queryKey: [chave] }),
      ),
    );
}

export function useCriarRecurso() {
  const invalidar = useInvalidarPainelOperacional();
  return useMutation({
    mutationFn: (dados: unknown) => api.post<Recurso>("/recursos", dados),
    onSuccess: () => invalidar(),
  });
}

export function useAtualizarRecurso() {
  const invalidar = useInvalidarPainelOperacional();
  return useMutation({
    mutationFn: ({ id, dados }: { id: string; dados: unknown }) => api.put<Recurso>(`/recursos/${id}`, dados),
    onSuccess: () => invalidar(),
  });
}

export function useAlterarEstadoRecurso() {
  const invalidar = useInvalidarPainelOperacional();
  return useMutation({
    mutationFn: ({ id, estado }: { id: string; estado: string }) => api.patch<Recurso>(`/recursos/${id}/estado`, { estado }),
    onSuccess: () => invalidar(),
  });
}

export function useInativarRecurso() {
  const invalidar = useInvalidarPainelOperacional();
  return useMutation({
    mutationFn: (id: string) => api.delete<Recurso>(`/recursos/${id}`),
    onSuccess: () => invalidar(),
  });
}

export function useCriarOcorrencia() {
  const invalidar = useInvalidarPainelOperacional();
  return useMutation({
    mutationFn: (dados: unknown) => api.post<Ocorrencia>("/ocorrencias", dados),
    onSuccess: () => invalidar(),
  });
}

export function useAdicionarDemanda() {
  const invalidar = useInvalidarPainelOperacional();
  return useMutation({
    mutationFn: ({ ocorrenciaId, dados }: { ocorrenciaId: string; dados: Partial<Demanda> }) =>
      api.post<Ocorrencia>(`/ocorrencias/${ocorrenciaId}/demandas`, dados),
    onSuccess: () => invalidar(),
  });
}

export function useEncerrarOcorrencia() {
  const invalidar = useInvalidarPainelOperacional();
  return useMutation({
    mutationFn: (id: string) => api.post<Ocorrencia>(`/ocorrencias/${id}/encerrar`),
    onSuccess: () => invalidar(),
  });
}

export function useEmpenharRecurso() {
  const invalidar = useInvalidarPainelOperacional();
  return useMutation({
    mutationFn: (dados: { recurso_id: string; ocorrencia_id: string; demanda_id?: string }) =>
      api.post<Empenho>("/empenhos", dados),
    onSuccess: () => invalidar(),
  });
}

export function useLiberarEmpenho() {
  const invalidar = useInvalidarPainelOperacional();
  return useMutation({
    mutationFn: (empenhoId: string) => api.post<Empenho>(`/empenhos/${empenhoId}/liberar`),
    onSuccess: () => invalidar(),
  });
}
