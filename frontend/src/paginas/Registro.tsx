import { FormEvent, useState } from "react";
import { enviar } from "../api";

const RANGOS = ["18-29", "30-39", "40-49", "50-59", "60-69", "70+"];

export default function Registro({ alTerminar }: { alTerminar: () => void }) {
  const [f, setF] = useState({
    nombre: "", correo: "", contrasena: "", rango_edad: "40-49",
    acepta_politica: false, autoriza_datos_sensibles: false, autoriza_compartir: false,
  });
  const [error, setError] = useState("");
  const cambiar = (campo: string, valor: string | boolean) => setF({ ...f, [campo]: valor });

  const registrar = async (e: FormEvent) => {
    e.preventDefault();
    setError("");
    try {
      await enviar("/auth/registro", "POST", f);
      alTerminar();
    } catch (err) {
      setError((err as Error).message);
    }
  };

  return (
    <form className="tarjeta estrecha" onSubmit={registrar}>
      <h1>Crear cuenta</h1>
      <label>Nombre<input value={f.nombre} onChange={(e) => cambiar("nombre", e.target.value)} required /></label>
      <label>Correo<input type="email" value={f.correo} onChange={(e) => cambiar("correo", e.target.value)} required /></label>
      <label>Contraseña (mínimo 8 caracteres, con letras y números)
        <input type="password" minLength={8} maxLength={72} value={f.contrasena}
          onChange={(e) => cambiar("contrasena", e.target.value)} required />
      </label>
      <label>Rango de edad
        <select value={f.rango_edad} onChange={(e) => cambiar("rango_edad", e.target.value)}>
          {RANGOS.map((r) => <option key={r}>{r}</option>)}
        </select>
      </label>
      <label className="casilla">
        <input type="checkbox" checked={f.acepta_politica} onChange={(e) => cambiar("acepta_politica", e.target.checked)} required />
        Acepto la política de tratamiento de datos personales (Ley 1581 de 2012).
      </label>
      <label className="casilla">
        <input type="checkbox" checked={f.autoriza_datos_sensibles}
          onChange={(e) => cambiar("autoriza_datos_sensibles", e.target.checked)} />
        Autorizo el tratamiento de mis datos sensibles de salud (opcional).
      </label>
      <label className="casilla">
        <input type="checkbox" checked={f.autoriza_compartir}
          onChange={(e) => cambiar("autoriza_compartir", e.target.checked)} />
        Autorizo compartir mi avance con mi profesional de la salud (opcional).
      </label>
      {error && <p className="error" role="alert">{error}</p>}
      <button className="primario">Registrarme</button>
      <button type="button" className="enlace" onClick={alTerminar}>Ya tengo cuenta</button>
    </form>
  );
}
