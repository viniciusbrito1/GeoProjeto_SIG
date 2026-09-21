import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { api, ErroApi } from "../api/client";
import type { Perfil } from "../types";

interface Usuario {
  id: string;
  nome: string;
  email: string;
  perfil: Perfil;
  ativo: boolean;
  criado_em: string;
}

export function Usuarios() {
  const queryClient = useQueryClient();
  const { data: usuarios, isLoading } = useQuery({ queryKey: ["usuarios"], queryFn: () => api.get<Usuario[]>("/usuarios") });
  const inativar = useMutation({
    mutationFn: (id: string) => api.patch<Usuario>(`/usuarios/${id}/inativar`),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["usuarios"] }),
  });

  const [modalAberto, setModalAberto] = useState(false);

  return (
    <div className="conteudo-padding">
      <div className="topo-pagina">
        <h1>Usuários</h1>
        <button onClick={() => setModalAberto(true)}>+ Novo usuário</button>
      </div>

      <table>
        <thead>
          <tr>
            <th>Nome</th>
            <th>E-mail</th>
            <th>Perfil</th>
            <th>Situação</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {isLoading && (
            <tr>
              <td colSpan={5}>Carregando...</td>
            </tr>
          )}
          {usuarios?.map((u) => (
            <tr key={u.id}>
              <td>{u.nome}</td>
              <td>{u.email}</td>
              <td style={{ textTransform: "capitalize" }}>{u.perfil}</td>
              <td>{u.ativo ? "Ativo" : "Inativo"}</td>
              <td>
                {u.ativo && (
                  <button className="perigo" onClick={() => inativar.mutate(u.id)}>
                    Inativar
                  </button>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      {modalAberto && <ModalNovoUsuario onFechar={() => setModalAberto(false)} />}
    </div>
  );
}

function ModalNovoUsuario({ onFechar }: { onFechar: () => void }) {
  const queryClient = useQueryClient();
  const criar = useMutation({
    mutationFn: (dados: { nome: string; email: string; senha: string; perfil: Perfil }) => api.post<Usuario>("/usuarios", dados),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["usuarios"] });
      onFechar();
    },
  });

  const [nome, setNome] = useState("");
  const [email, setEmail] = useState("");
  const [senha, setSenha] = useState("");
  const [perfil, setPerfil] = useState<Perfil>("consulta");
  const [erro, setErro] = useState<string | null>(null);

  async function aoSubmeter() {
    setErro(null);
    try {
      await criar.mutateAsync({ nome, email, senha, perfil });
    } catch (e) {
      setErro(e instanceof ErroApi ? e.message : "Não foi possível criar o usuário.");
    }
  }

  return (
    <div className="modal-fundo">
      <div className="modal-caixa">
        <h2>Novo usuário</h2>
        {erro && <div className="erro-mensagem">{erro}</div>}
        <label>
          Nome
          <input value={nome} onChange={(e) => setNome(e.target.value)} />
        </label>
        <label style={{ marginTop: 12 }}>
          E-mail
          <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} />
        </label>
        <label style={{ marginTop: 12 }}>
          Senha provisória
          <input type="password" value={senha} onChange={(e) => setSenha(e.target.value)} minLength={8} />
        </label>
        <label style={{ marginTop: 12 }}>
          Perfil (RF-12)
          <select value={perfil} onChange={(e) => setPerfil(e.target.value as Perfil)}>
            <option value="consulta">Consulta — somente leitura</option>
            <option value="operador">Operador — escrita restrita</option>
            <option value="coordenador">Coordenador — escrita total</option>
          </select>
        </label>
        <div className="acoes-rodape">
          <button type="button" className="secundario" onClick={onFechar}>
            Cancelar
          </button>
          <button type="button" onClick={aoSubmeter} disabled={criar.isPending || !nome || !email || senha.length < 8}>
            Criar
          </button>
        </div>
      </div>
    </div>
  );
}
