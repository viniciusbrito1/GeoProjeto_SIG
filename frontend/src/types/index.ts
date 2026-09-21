export type Perfil = "coordenador" | "operador" | "consulta";
export type TipoRecurso = "equipe" | "instalacao" | "equipamento";
export type EstadoRecurso = "disponivel" | "empenhado" | "indisponivel" | "inativo";
export type SeveridadeOcorrencia = "baixa" | "media" | "alta" | "critica";
export type StatusOcorrencia = "aberta" | "encerrada";
export type StatusEmpenho = "ativo" | "liberado";

export interface GeoJSONPoint {
  type: "Point";
  coordinates: [number, number];
}

export interface GeoJSONMultiPolygon {
  type: "MultiPolygon";
  coordinates: number[][][][];
}

export interface UsuarioAutenticado {
  id: string;
  nome: string;
  email: string;
  perfil: Perfil;
}

export interface Orgao {
  id: string;
  nome: string;
  sigla: string;
}

export interface Municipio {
  codigo_ibge: string;
  nome: string;
  uf: string;
}

export interface Recurso {
  id: string;
  tipo: TipoRecurso;
  nome: string;
  orgao_id: string;
  orgao_sigla: string | null;
  especialidade: string | null;
  capacidade_valor: number | null;
  capacidade_unidade: string | null;
  localizacao: GeoJSONPoint;
  estado: EstadoRecurso;
  ativo: boolean;
  criado_em: string;
  atualizado_em: string;
  distancia_m: number | null;
}

export interface Demanda {
  id: string;
  ocorrencia_id: string;
  tipo_recurso: TipoRecurso;
  especialidade: string | null;
  quantidade_necessaria: number;
  quantidade_empenhada: number;
  saldo_descoberto: number;
}

export interface Ocorrencia {
  id: string;
  tipo: string;
  severidade: SeveridadeOcorrencia;
  municipio_codigo_ibge: string;
  municipio_nome: string | null;
  area_atingida: GeoJSONMultiPolygon;
  descricao: string | null;
  status: StatusOcorrencia;
  criado_por: string;
  criado_em: string;
  encerrado_em: string | null;
  demandas: Demanda[];
}

export interface Empenho {
  id: string;
  recurso_id: string;
  recurso_nome: string | null;
  ocorrencia_id: string;
  demanda_id: string | null;
  status: StatusEmpenho;
  autor_empenho_id: string;
  empenhado_em: string;
  autor_liberacao_id: string | null;
  liberado_em: string | null;
}

export interface AuditoriaRegistro {
  id: number;
  tabela: string;
  operacao: string;
  registro_id: string | null;
  usuario_id: string | null;
  usuario_nome: string | null;
  dados_antes: Record<string, unknown> | null;
  dados_depois: Record<string, unknown> | null;
  criado_em: string;
}

export interface CamadaExterna {
  id: string;
  nome: string;
  url_wms: string;
  nome_camada: string;
  ativa: boolean;
}

export interface FeatureCollectionGeoJSON<P = Record<string, unknown>> {
  type: "FeatureCollection";
  crs?: { type: "name"; properties: { name: string } };
  features: Array<{ type: "Feature"; geometry: GeoJSON.Geometry; properties: P }>;
}
