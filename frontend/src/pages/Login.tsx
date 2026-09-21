import { useState, type FormEvent } from "react";
import { Navigate } from "react-router-dom";

import { useAuth } from "../auth/AuthContext";
import { ErroApi } from "../api/client";

export function Login() {
  const { usuario, login } = useAuth();
  const [email, setEmail] = useState("");
  const [senha, setSenha] = useState("");
  const [erro, setErro] = useState<string | null>(null);
  const [enviando, setEnviando] = useState(false);

  if (usuario) return <Navigate to="/mapa" replace />;

  async function aoEnviar(evento: FormEvent) {
    evento.preventDefault();
    setErro(null);
    setEnviando(true);
    try {
      await login(email, senha);
    } catch (e) {
      setErro(e instanceof ErroApi ? e.message : "Não foi possível entrar. Tente novamente.");
    } finally {
      setEnviando(false);
    }
  }

  return (
    <div className="pagina-login">
      <div className="cartao-login">
        <h1>SISCOORD-DC</h1>
        <p className="subtitulo">Sistema de Coordenação Geoespacial de Recursos de Defesa Civil</p>
        {erro && <div className="erro-mensagem">{erro}</div>}
        <form onSubmit={aoEnviar}>
          <label>
            E-mail
            <input type="email" required value={email} onChange={(e) => setEmail(e.target.value)} autoFocus />
          </label>
          <label>
            Senha
            <input type="password" required value={senha} onChange={(e) => setSenha(e.target.value)} />
          </label>
          <button type="submit" disabled={enviando}>
            {enviando ? "Entrando..." : "Entrar"}
          </button>
        </form>
      </div>
    </div>
  );
}
