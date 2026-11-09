import { useEffect, useState } from "react";
import { api, Caso } from "../api";

const NIVELES: Record<number, string> = { 1: "Básico", 2: "Intermedio", 3: "Avanzado" };

export default function Catalogo({ token }: { token: string }) {
  const [casos, setCasos] = useState<Caso[] | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    api<Caso[]>("/casos", {}, token).then(setCasos).catch((e) => setError(e.message));
  }, [token]);

  if (error) return <p className="error" role="alert">{error}</p>;
  if (!casos) return <p>Cargando casos…</p>;

  return (
    <section>
      <h1>Biblioteca de casos</h1>
      {casos.length === 0 && <p>Aún no hay casos publicados.</p>}
      <div className="rejilla">
        {casos.map((c) => (
          <article key={c.id_caso} className="tarjeta caso">
            <h2>{c.titulo}</h2>
            <p>{c.tema}</p>
            <p className="meta">{NIVELES[c.nivel_dificultad] ?? `Nivel ${c.nivel_dificultad}`} · {c.etapas} etapas</p>
            <button className="primario" disabled>Iniciar simulación (Ciclo 2)</button>
          </article>
        ))}
      </div>
    </section>
  );
}
