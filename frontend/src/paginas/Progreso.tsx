import { useEffect, useState } from "react";
import { api, fecha } from "../api";

export interface DatosProgreso {
  puntaje_acumulado: number; nivel: string | null; siguiente_nivel_desde: number | null;
  porcentaje_aciertos: number | null; tasa_deteccion_errores_ia: number | null;
  calibracion: { confianza_en_aciertos: number | null; confianza_en_errores: number | null; explicacion: string };
  evolucion: { fecha: string; titulo: string; puntaje_total: number }[];
  insignias: { nombre: string; criterio: string }[];
}
export interface Intento {
  id_intento: number; titulo: string; estado: string; puntaje_total: number | null; fecha_inicio: string;
  aciertos: number; decisiones: number;
}

export function VistaProgreso({ p, historial }: { p: DatosProgreso; historial: Intento[] }) {
  const max = Math.max(100, ...p.evolucion.map((e) => e.puntaje_total));
  return (
    <>
      <dl className="cifras">
        <div><dt>Nivel</dt><dd>{p.nivel ?? "—"}</dd></div>
        <div><dt>Puntaje</dt><dd>{p.puntaje_acumulado}</dd></div>
        <div><dt>Aciertos</dt><dd>{p.porcentaje_aciertos ?? "—"} %</dd></div>
        <div><dt>Errores de la IA detectados</dt><dd>{p.tasa_deteccion_errores_ia ?? "—"} %</dd></div>
      </dl>
      {p.siguiente_nivel_desde && <p className="meta">Te faltan {p.siguiente_nivel_desde - p.puntaje_acumulado} puntos para el siguiente nivel.</p>}
      <h2>Evolución del puntaje</h2>
      {p.evolucion.length === 0 ? <p>Aún no has terminado casos.</p> : (
        <div className="barras" role="img" aria-label="Puntaje de cada caso terminado">
          {p.evolucion.map((e, i) => (
            <div key={i} title={`${e.titulo}: ${e.puntaje_total}`} style={{ height: `${(100 * e.puntaje_total) / max}%` }}>
              <span>{e.puntaje_total}</span>
            </div>
          ))}
        </div>
      )}
      <h2>Calibración de tu confianza</h2>
      <p>Cuando aciertas declaras en promedio <strong>{p.calibracion.confianza_en_aciertos ?? "—"}</strong> de 5; cuando te equivocas,
        <strong> {p.calibracion.confianza_en_errores ?? "—"}</strong> de 5. {p.calibracion.explicacion}</p>
      {p.insignias.length > 0 && (
        <>
          <h2>Insignias</h2>
          <ul className="insignias">{p.insignias.map((i) => <li key={i.nombre} title={i.criterio}>🏅 {i.nombre}</li>)}</ul>
        </>
      )}
      <h2>Historial de intentos</h2>
      <table>
        <thead><tr><th>Fecha</th><th>Caso</th><th>Estado</th><th>Aciertos</th><th>Puntaje</th></tr></thead>
        <tbody>
          {historial.map((h) => (
            <tr key={h.id_intento}>
              <td>{fecha(h.fecha_inicio)}</td><td>{h.titulo}</td><td>{h.estado.replace("_", " ")}</td>
              <td>{h.aciertos}/{h.decisiones}</td><td>{h.puntaje_total ?? "—"}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </>
  );
}

// Pantalla 08 · RF-008 8.1 y 8.2
export default function Progreso() {
  const [p, setP] = useState<DatosProgreso | null>(null);
  const [h, setH] = useState<Intento[]>([]);
  const [error, setError] = useState("");
  useEffect(() => {
    Promise.all([api<DatosProgreso>("/progreso"), api<Intento[]>("/progreso/historial")])
      .then(([a, b]) => { setP(a); setH(b); }).catch((e) => setError(e.message));
  }, []);
  if (error) return <p className="error">{error}</p>;
  if (!p) return <p>Cargando progreso…</p>;
  return <section><h1>Mi progreso</h1><VistaProgreso p={p} historial={h} /></section>;
}
