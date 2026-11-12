import { FormEvent, useState } from "react";
import { enviar, Rol } from "../api";

interface Props {
  alEntrar: (token: string, rol: Rol) => void;
  irARegistro: () => void;
}

export default function Ingreso({ alEntrar, irARegistro }: Props) {
  const [correo, setCorreo] = useState("");
  const [contrasena, setContrasena] = useState("");
  const [error, setError] = useState("");
  const [cargando, setCargando] = useState(false);

  const entrar = async (e: FormEvent) => {
    e.preventDefault();
    setError("");
    setCargando(true);
    try {
      const r = await enviar<{ access_token: string; rol: Rol }>("/auth/login", "POST", { correo, contrasena });
      alEntrar(r.access_token, r.rol);
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setCargando(false);
    }
  };

  return (
    <form className="tarjeta estrecha" onSubmit={entrar}>
      <h1>Iniciar sesión</h1>
      <label>Correo<input type="email" value={correo} onChange={(e) => setCorreo(e.target.value)} required /></label>
      <label>Contraseña<input type="password" value={contrasena} onChange={(e) => setContrasena(e.target.value)} required /></label>
      {error && <p className="error" role="alert">{error}</p>}
      <button className="primario" disabled={cargando}>{cargando ? "Ingresando…" : "Ingresar"}</button>
      <button type="button" className="enlace" onClick={irARegistro}>Crear una cuenta</button>
    </form>
  );
}
