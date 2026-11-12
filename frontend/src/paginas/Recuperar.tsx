import { FormEvent, useState } from "react";
import { enviar } from "../api";

// RF-001 1.3 · pedir el enlace
export function Recuperar({ volver }: { volver: () => void }) {
  const [correo, setCorreo] = useState("");
  const [msg, setMsg] = useState("");
  const pedir = async (e: FormEvent) => {
    e.preventDefault();
    const r = await enviar<{ mensaje: string }>("/auth/recuperar", "POST", { correo }).catch((er) => ({ mensaje: er.message }));
    setMsg(r.mensaje);
  };
  return (
    <form className="tarjeta estrecha" onSubmit={pedir}>
      <h1>Recuperar contraseña</h1>
      <label>Correo<input type="email" value={correo} onChange={(e) => setCorreo(e.target.value)} required /></label>
      {msg && <p className="aviso" role="status">{msg}</p>}
      <button className="primario">Enviar enlace</button>
      <button type="button" className="enlace" onClick={volver}>Volver</button>
    </form>
  );
}

// RF-001 1.3 · crear la nueva contraseña con el enlace recibido
export function Restablecer({ token, terminar }: { token: string; terminar: () => void }) {
  const [clave, setClave] = useState("");
  const [error, setError] = useState("");
  const guardar = async (e: FormEvent) => {
    e.preventDefault();
    try { await enviar("/auth/restablecer", "POST", { token, contrasena: clave }); terminar(); }
    catch (er) { setError((er as Error).message); }
  };
  return (
    <form className="tarjeta estrecha" onSubmit={guardar}>
      <h1>Nueva contraseña</h1>
      <label>Contraseña (mínimo 8 caracteres, con letras y números)
        <input type="password" minLength={8} maxLength={72} value={clave} onChange={(e) => setClave(e.target.value)} required /></label>
      {error && <p className="error" role="alert">{error}</p>}
      <button className="primario">Guardar</button>
    </form>
  );
}
