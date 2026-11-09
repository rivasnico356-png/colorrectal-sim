import { FormEvent, useState } from "react";
import { api } from "../api";

interface Props {
  alEntrar: (token: string) => void;
  irARegistro: () => void;
}

export default function Ingreso({ alEntrar, irARegistro }: Props) {
  const [correo, setCorreo] = useState("");
  const [contrasena, setContrasena] = useState("");
  const [error, setError] = useState("");
  const [cargando, setCargando] = useState(false);

  const enviar = async (e: FormEvent) => {
    e.preventDefault();
    setError("");
    setCargando(true);
    try {
      const r = await api<{ access_token: string }>("/auth/login", {
        method: "POST",
        body: JSON.stringify({ correo, contrasena }),
      });
      alEntrar(r.access_token);
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setCargando(false);
    }
  };

  return (
    <form className="tarjeta" onSubmit={enviar}>
      <h1>Iniciar sesión</h1>
      <label>Correo<input type="email" value={correo} onChange={(e) => setCorreo(e.target.value)} required /></label>
      <label>Contraseña<input type="password" value={contrasena} onChange={(e) => setContrasena(e.target.value)} required /></label>
      {error && <p className="error" role="alert">{error}</p>}
      <button className="primario" disabled={cargando}>{cargando ? "Ingresando…" : "Ingresar"}</button>
      <button type="button" className="enlace" onClick={irARegistro}>Crear una cuenta</button>
    </form>
  );
}
