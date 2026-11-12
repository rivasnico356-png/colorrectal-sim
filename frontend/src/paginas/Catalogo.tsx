import { useEffect, useState } from "react";
import { api, Caso, TEMAS } from "../api";

const NIVELES: Record<number, string> = { 1: "Muy básico", 2: "Básico", 3: "Intermedio", 4: "Avanzado", 5: "Experto" };
const ESTADOS = { no_iniciado: "No iniciado", en_curso: "En curso", completado: "Completado" };

// Pantalla 03 · RF-002 2.6 y RF-006 6.1
export default function Catalogo({ abrir }: { abrir: (idCaso: number) => void }) {
  const [casos, setCasos] = useState<Caso[] | null>(null);
  const [tema, setTema] = useState("");
  const [estado, setEstado] = useState("");
  const [buscar, setBuscar] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    const q = new URLSearchParams();
    if (tema) q.set("tema", tema);
    if (estado) q.set("estado", estado);
    if (buscar.trim()) q.set("buscar", buscar.trim());
    const t = setTimeout(() => {
      api<Caso[]>(`/casos?${q}`).then(setCasos).catch((e) => setError(e.message));
    }, 250);
    return () => clearTimeout(t);
  }, [tema, estado, buscar]);

  return (
    <section>
      <h1>Biblioteca de casos</h1>
      <div className="filtros">
        <input placeholder="Buscar caso" value={buscar} onChange={(e) => setBuscar(e.target.value)} aria-label="Buscar caso" />
        <select value={tema} onChange={(e) => setTema(e.target.value)} aria-label="Tema">
          <option value="">Todos los temas</option>
          {TEMAS.map((t) => <option key={t}>{t}</option>)}
        </select>
        <select value={estado} onChange={(e) => setEstado(e.target.value)} aria-label="Estado">
          <option value="">Todos los estados</option>
          {Object.entries(ESTADOS).map(([v, t]) => <option key={v} value={v}>{t}</option>)}
        </select>
      </div>
      {error && <p className="error" role="alert">{error}</p>}
      {!casos && !error && <p>Cargando casos…</p>}
      {casos?.length === 0 && <p>No hay casos publicados con esos filtros.</p>}
      <div className="rejilla">
        {casos?.map((c) => (
          <article key={c.id_caso} className={`tarjeta caso ${c.bloqueado ? "bloqueado" : ""}`}>
            <span className={`etiqueta ${c.estado_usuario}`}>{ESTADOS[c.estado_usuario]}</span>
            <h2>{c.titulo}</h2>
            {c.descripcion && <p>{c.descripcion}</p>}
            <p className="meta">{c.tema} · {NIVELES[c.nivel_dificultad]} · {c.etapas} etapas</p>
            {c.bloqueado ? (
              <p className="aviso">🔒 {c.requisito}</p>
            ) : (
              <button className="primario" onClick={() => abrir(c.id_caso)}>
                {c.estado_usuario === "en_curso" ? "Continuar" : c.estado_usuario === "completado" ? "Repetir" : "Iniciar simulación"}
              </button>
            )}
          </article>
        ))}
      </div>
    </section>
  );
}
