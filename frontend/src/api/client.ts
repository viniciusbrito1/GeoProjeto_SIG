const TOKEN_STORAGE_KEY = "siscoord_token";

export function obterToken(): string | null {
  return localStorage.getItem(TOKEN_STORAGE_KEY);
}

export function salvarToken(token: string): void {
  localStorage.setItem(TOKEN_STORAGE_KEY, token);
}

export function limparToken(): void {
  localStorage.removeItem(TOKEN_STORAGE_KEY);
}

export class ErroApi extends Error {
  status: number;
  constructor(status: number, mensagem: string) {
    super(mensagem);
    this.status = status;
  }
}

interface ErroValidacaoFastAPI {
  loc?: Array<string | number>;
  msg?: string;
}

// O `detail` de erro de negócio (ErroNegocio) é sempre string, mas o de erro
// de validação automática do FastAPI/Pydantic (422) é uma lista de objetos —
// sem tratar os dois formatos, `new Error(detail)` vira o inútil "[object
// Object]" quando detail é a lista.
function formatarDetalheErro(detail: unknown, status: number): string {
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) {
    const mensagens = (detail as ErroValidacaoFastAPI[]).map((item) => {
      const campo = item.loc?.filter((parte) => parte !== "body").join(".");
      return campo ? `${campo}: ${item.msg ?? "valor inválido"}` : (item.msg ?? "valor inválido");
    });
    if (mensagens.length > 0) return mensagens.join("; ");
  }
  return `Erro ${status}`;
}

async function requisitar<T>(caminho: string, opcoes: RequestInit = {}): Promise<T> {
  const token = obterToken();
  const cabecalhos: Record<string, string> = {
    ...(opcoes.body ? { "Content-Type": "application/json" } : {}),
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...(opcoes.headers as Record<string, string> | undefined),
  };

  const resposta = await fetch(`/api${caminho}`, { ...opcoes, headers: cabecalhos });

  if (resposta.status === 401) {
    limparToken();
    window.location.href = "/login";
    throw new ErroApi(401, "Sessão expirada.");
  }

  if (!resposta.ok) {
    let detalhe = `Erro ${resposta.status}`;
    try {
      const corpo = await resposta.json();
      detalhe = formatarDetalheErro(corpo.detail, resposta.status);
    } catch {
      /* resposta sem corpo JSON */
    }
    throw new ErroApi(resposta.status, detalhe);
  }

  if (resposta.status === 204) return undefined as T;
  const tipoConteudo = resposta.headers.get("content-type") ?? "";
  if (!tipoConteudo.includes("application/json")) return (await resposta.blob()) as unknown as T;
  return (await resposta.json()) as T;
}

export async function baixarArquivo(caminho: string, nomeArquivo: string): Promise<void> {
  const blob = await requisitar<Blob>(caminho);
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = nomeArquivo;
  link.click();
  URL.revokeObjectURL(url);
}

export const api = {
  get: <T>(caminho: string) => requisitar<T>(caminho),
  post: <T>(caminho: string, corpo?: unknown) =>
    requisitar<T>(caminho, { method: "POST", body: corpo !== undefined ? JSON.stringify(corpo) : undefined }),
  put: <T>(caminho: string, corpo?: unknown) =>
    requisitar<T>(caminho, { method: "PUT", body: corpo !== undefined ? JSON.stringify(corpo) : undefined }),
  patch: <T>(caminho: string, corpo?: unknown) =>
    requisitar<T>(caminho, { method: "PATCH", body: corpo !== undefined ? JSON.stringify(corpo) : undefined }),
  delete: <T>(caminho: string) => requisitar<T>(caminho, { method: "DELETE" }),
};
