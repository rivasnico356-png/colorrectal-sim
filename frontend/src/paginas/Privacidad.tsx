import { FormEvent, useEffect, useState } from "react";
import { api, enviar, fecha } from "../api";

type Autorizacion = { tipo: string; aceptada: boolean; version_politica: string; fecha_aceptacion: string | null };
type Vinculo = { id_vinculo: number; nombre: string; correo: string; autoriza_compartir: boolean };
const NOMBRES: Record<string, string> = {
  politica_tratamiento: "Política de tratamiento de datos (Ley 1581 de 2012)",
  datos_sensibles: "Tratamiento de datos sensibles de salud",
  compartir_avance: "Compartir mi avance con mi profesional de la salud",
};

// RF-009 y RF-001 1.6
export default function Privacidad({ alSuprimir }: { alSuprimir: () => void }) {
  const [aut, setAut] = useState<Autorizacion[]>([]);
  const [vinc, setVinc] = useState<Vinculo[]>([]);
  const [perfil, setPerfil] = useState<{ nombre: string; correo: string; rango_edad: string } | null>(null);
  const [correoProf, setCorreoProf] = useState("");
  const [nombre, setNombre] = useState("");
  const [clave, setClave] = useState("");
  const [msg, setMsg] = useState("");

  const cargar = async () => {
    const d = await api<{ perfil: { nombre: string; correo: string; rango_edad: string }; autorizaciones: Autorizacion[] }>("/privacidad/mis-datos");
    setPerfil(d.perfil);
    setNombre(d.perfil.nombre);
    setAut(d.autorizaciones);
    setVinc(await api<Vinculo[]>("/vinculos"));
  };
  useEffect(() => { cargar().catch((e) => setMsg(e.message)); }, []);

  const accion = async (f: () => Promise<unknown>, ok: string) => {
    setMsg("");
    try { await f(); setMsg(ok); await cargar(); } catch (e) { setMsg((e as Error).message); }
  };

  const vincular = (e: FormEvent) => {
    e.preventDefault();
    const compartir = aut.find((a) => a.tipo === "compartir_avance")?.aceptada ?? false;
    accion(() => enviar("/vinculos", "POST", { correo_profesional: correoProf, autoriza_compartir: compartir }), "Vínculo creado.");
    setCorreoProf("");
  };

  return (
    <section className="privacidad">
      <h1>Mis datos y privacidad</h1>
      {msg && <p className="aviso" role="status">{msg}</p>}
      <div className="tarjeta">
        <h2>Mis datos</h2>
        {perfil && <p>{perfil.correo} · Rango de edad {perfil.rango_edad}</p>}
        <form className="fila" onSubmit={(e) => { e.preventDefault(); accion(() => enviar("/usuarios/me", "PATCH", { nombre }), "Datos actualizados."); }}>
          <label>Nombre<input value={nombre} onChange={(e) => setNombre(e.target.value)} minLength={2} /></label>
          <button>Guardar</button>
        </form>
      </div>
      <div className="tarjeta">
        <h2>Autorizaciones</h2>
        {aut.map((a) => (
          <label key={a.tipo} className="casilla">
            <input type="checkbox" checked={a.aceptada} disabled={a.tipo === "politica_tratamiento"}
              onChange={(e) => accion(() => enviar(`/privacidad/autorizaciones/${a.tipo}`, "PUT", { aceptada: e.target.checked }), "Autorización actualizada.")} />
            <span>{NOMBRES[a.tipo] ?? a.tipo}<small className="meta"> · versión {a.version_politica} · {fecha(a.fecha_aceptacion)}</small></span>
          </label>
        ))}
      </div>
      <div className="tarjeta">
        <h2>Mi profesional de la salud</h2>
        {vinc.map((v) => (
          <div key={v.id_vinculo} className="fila">
            <span>{v.nombre} ({v.correo}) · {v.autoriza_compartir ? "ve tu avance" : "no ve tu avance"}</span>
            <button onClick={() => accion(() => enviar(`/vinculos/${v.id_vinculo}`, "PATCH", { autoriza_compartir: !v.autoriza_compartir }), "Vínculo actualizado.")}>
              {v.autoriza_compartir ? "Dejar de compartir" : "Compartir"}
            </button>
            <button className="enlace" onClick={() => accion(() => enviar(`/vinculos/${v.id_vinculo}`, "DELETE"), "Vínculo terminado.")}>Desvincular</button>
          </div>
        ))}
        <form className="fila" onSubmit={vincular}>
          <label>Correo de tu profesional<input type="email" value={correoProf} onChange={(e) => setCorreoProf(e.target.value)} required /></label>
          <button>Vincular</button>
        </form>
      </div>
      <div className="tarjeta peligro">
        <h2>Suprimir mi cuenta</h2>
        <p>Se borran tus datos personales y no podrás volver a entrar. Esta acción no se puede deshacer.</p>
        <form className="fila" onSubmit={(e) => {
          e.preventDefault();
          enviar("/usuarios/me", "DELETE", { contrasena: clave, confirmar: true }).then(alSuprimir).catch((er) => setMsg(er.message));
        }}>
          <label>Confirma con tu contraseña<input type="password" value={clave} onChange={(e) => setClave(e.target.value)} required /></label>
          <button className="peligro">Suprimir cuenta</button>
        </form>
      </div>
    </section>
  );
}
