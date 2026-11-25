import { FormEvent, useEffect, useState } from "react";
import { api, enviar, fecha, Rol } from "../api";

type Fila = { id_usuario: string; nombre: string; correo: string; rol: Rol; estado: string; fecha_registro: string };
const ROLES: Rol[] = ["Usuario", "Profesional de la salud", "Administrador"];

// Pantalla 13 · RF-001 1.1 y 1.5
export default function Admin() {
  const [filas, setFilas] = useState<Fila[]>([]);
  const [buscar, setBuscar] = useState("");
  const [msg, setMsg] = useState("");
  const [nueva, setNueva] = useState({ nombre: "", correo: "", contrasena: "", rol: "Profesional de la salud" as Rol });

  const cargar = () => api<Fila[]>(`/admin/usuarios${buscar ? `?buscar=${encodeURIComponent(buscar)}` : ""}`).then(setFilas)
    .catch((e) => setMsg(e.message));
  useEffect(() => { const t = setTimeout(cargar, 250); return () => clearTimeout(t); }, [buscar]);

  const cambiar = async (id: string, cambio: object) => {
    try { await enviar(`/admin/usuarios/${id}`, "PATCH", cambio); setMsg("Cambio registrado en la bitácora."); cargar(); }
    catch (e) { setMsg((e as Error).message); }
  };

  const crear = async (e: FormEvent) => {
    e.preventDefault();
    try { await enviar("/admin/usuarios", "POST", nueva); setMsg("Cuenta creada."); cargar(); }
    catch (err) { setMsg((err as Error).message); }
  };

  return (
    <section>
      <h1>Usuarios y roles</h1>
      {msg && <p className="aviso" role="status">{msg}</p>}
      <input placeholder="Buscar por nombre o correo" value={buscar} onChange={(e) => setBuscar(e.target.value)} aria-label="Buscar usuario" />
      <table>
        <thead><tr><th>Nombre</th><th>Correo</th><th>Rol</th><th>Estado</th><th>Registro</th></tr></thead>
        <tbody>{filas.map((f) => (
          <tr key={f.id_usuario}>
            <td>{f.nombre}</td><td>{f.correo}</td>
            <td><select value={f.rol} onChange={(e) => cambiar(f.id_usuario, { rol: e.target.value })} aria-label="Rol">
              {ROLES.map((r) => <option key={r}>{r}</option>)}</select></td>
            <td><button onClick={() => cambiar(f.id_usuario, { estado: f.estado === "activo" ? "inactivo" : "activo" })}>
              {f.estado === "activo" ? "Desactivar" : "Activar"}</button></td>
            <td>{fecha(f.fecha_registro)}</td>
          </tr>
        ))}</tbody>
      </table>
      <form className="tarjeta" onSubmit={crear}>
        <h2>Crear cuenta de profesional o administrador</h2>
        <label>Nombre<input value={nueva.nombre} onChange={(e) => setNueva({ ...nueva, nombre: e.target.value })} required /></label>
        <label>Correo<input type="email" value={nueva.correo} onChange={(e) => setNueva({ ...nueva, correo: e.target.value })} required /></label>
        <label>Contraseña inicial<input type="password" value={nueva.contrasena} minLength={8} required
          onChange={(e) => setNueva({ ...nueva, contrasena: e.target.value })} /></label>
        <label>Rol<select value={nueva.rol} onChange={(e) => setNueva({ ...nueva, rol: e.target.value as Rol })}>
          {ROLES.filter((r) => r !== "Usuario").map((r) => <option key={r}>{r}</option>)}</select></label>
        <button className="primario">Crear</button>
      </form>
    </section>
  );
}
