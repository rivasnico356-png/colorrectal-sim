import { FormEvent, useEffect, useState } from "react";
import { api, enviar, TEMAS } from "../api";
import { DatosProgreso, Intento, VistaProgreso } from "./Progreso";

type Panel = { usuarios: number; puntaje_promedio: number | null; casos_completados: number;
  por_caso: { id_caso: number; titulo: string; decisiones: number; pct_aciertos: number | null; pct_acepta_ia: number | null }[] };
type Vinculado = { id_vinculo: number; id_persona: string; nombre: string; correo: string; autoriza_compartir: boolean };
type CasoEditor = { id_caso: number; titulo: string; tema: string; nivel_dificultad: number; estado: string; autor: string; es_autor: boolean };
type Opcion = { texto: string; puntaje: number; retroalimentacion: string; fuente: string; es_correcta: boolean; recomendada_ia: boolean };

// Pantalla 12 · RF-008 8.3/8.4 y RF-007 7.2
export function PanelProfesional() {
  const [panel, setPanel] = useState<Panel | null>(null);
  const [vinc, setVinc] = useState<Vinculado[]>([]);
  const [detalle, setDetalle] = useState<{ nombre: string; progreso: DatosProgreso; historial: Intento[] } | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    Promise.all([api<Panel>("/profesional/panel"), api<Vinculado[]>("/vinculos")])
      .then(([p, v]) => { setPanel(p); setVinc(v); }).catch((e) => setError(e.message));
  }, []);

  const verDetalle = async (v: Vinculado) => {
    try {
      const d = await api<{ progreso: DatosProgreso; historial: Intento[] }>(`/profesional/usuarios/${v.id_persona}/avance`);
      setDetalle({ nombre: v.nombre, ...d });
    } catch (e) {
      setError((e as Error).message);
    }
  };

  const exportar = async () => {
    const csv = await api<string>("/exportacion/interacciones.csv");
    const url = URL.createObjectURL(new Blob([csv], { type: "text/csv" }));
    const a = document.createElement("a");
    a.href = url;
    a.download = "interacciones.csv";
    a.click();
    URL.revokeObjectURL(url);
  };

  if (error) return <p className="error">{error}</p>;
  if (!panel) return <p>Cargando panel…</p>;
  return (
    <section>
      <h1>Usuarios vinculados</h1>
      <p className="meta">Solo se incluyen las personas que autorizaron compartir su avance contigo.</p>
      <dl className="cifras">
        <div><dt>Usuarios</dt><dd>{panel.usuarios}</dd></div>
        <div><dt>Puntaje promedio</dt><dd>{panel.puntaje_promedio ?? "—"}</dd></div>
        <div><dt>Casos completados</dt><dd>{panel.casos_completados}</dd></div>
      </dl>
      <table>
        <thead><tr><th>Caso</th><th>Decisiones</th><th>% aciertos</th><th>% aceptación de la IA</th></tr></thead>
        <tbody>{panel.por_caso.map((c) => (
          <tr key={c.id_caso}><td>{c.titulo}</td><td>{c.decisiones}</td><td>{c.pct_aciertos ?? "—"}</td><td>{c.pct_acepta_ia ?? "—"}</td></tr>
        ))}</tbody>
      </table>
      <button onClick={exportar}>Exportar datos seudonimizados (CSV)</button>
      <h2>Avance individual</h2>
      {vinc.map((v) => (
        <div key={v.id_vinculo} className="fila">
          <span>{v.nombre}</span>
          {v.autoriza_compartir ? <button onClick={() => verDetalle(v)}>Ver avance</button> : <span className="meta">No autorizó compartir</span>}
        </div>
      ))}
      {detalle && <div className="tarjeta"><h2>{detalle.nombre}</h2><VistaProgreso p={detalle.progreso} historial={detalle.historial} /></div>}
    </section>
  );
}

const OPCION_VACIA: Opcion = { texto: "", puntaje: 0, retroalimentacion: "", fuente: "", es_correcta: false, recomendada_ia: false };

// Pantallas 10 y 11 · RF-002 2.1–2.5
export function EditorCasos() {
  const [casos, setCasos] = useState<CasoEditor[]>([]);
  const [msg, setMsg] = useState("");
  const [abierto, setAbierto] = useState<number | null>(null);
  const [nuevo, setNuevo] = useState({ titulo: "", tema: TEMAS[0], nivel_dificultad: 1, descripcion: "", contexto_simulado: "" });

  const cargar = () => api<CasoEditor[]>("/editor/casos").then(setCasos).catch((e) => setMsg(e.message));
  useEffect(() => { cargar(); }, []);

  const crear = async (e: FormEvent) => {
    e.preventDefault();
    try {
      const r = await enviar<{ id_caso: number }>("/editor/casos", "POST", nuevo);
      setMsg("Caso creado en borrador. Agrega sus etapas.");
      setAbierto(r.id_caso);
      cargar();
    } catch (err) { setMsg((err as Error).message); }
  };

  const revisar = async (id: number, accion: string) => {
    const fuente_clinica = accion === "aprobar" ? prompt("Fuente clínica de respaldo") : null;
    if (accion === "aprobar" && !fuente_clinica) return;
    try { await enviar(`/editor/casos/${id}/revision`, "POST", { accion, fuente_clinica }); setMsg("Estado actualizado."); cargar(); }
    catch (err) { setMsg((err as Error).message); }
  };

  return (
    <section>
      <h1>Casos clínicos</h1>
      {msg && <p className="aviso" role="status">{msg}</p>}
      <table>
        <thead><tr><th>Caso</th><th>Autor</th><th>Estado</th><th>Acciones</th></tr></thead>
        <tbody>{casos.map((c) => (
          <tr key={c.id_caso}>
            <td>{c.titulo}</td><td>{c.autor}</td><td>{c.estado}</td>
            <td className="acciones">
              {c.es_autor && <button onClick={() => setAbierto(c.id_caso)}>Etapas</button>}
              {!c.es_autor && c.estado === "borrador" && <button onClick={() => revisar(c.id_caso, "aprobar")}>Aprobar</button>}
              {!c.es_autor && c.estado === "revisado" && <button onClick={() => revisar(c.id_caso, "publicar")}>Publicar</button>}
              {!c.es_autor && c.estado !== "publicado" && <button className="enlace" onClick={() => revisar(c.id_caso, "devolver")}>Devolver</button>}
            </td>
          </tr>
        ))}</tbody>
      </table>
      {abierto && <EditorEtapa idCaso={abierto} alGuardar={(m) => { setMsg(m); cargar(); }} />}
      <form className="tarjeta" onSubmit={crear}>
        <h2>Nuevo caso</h2>
        <label>Título<input value={nuevo.titulo} onChange={(e) => setNuevo({ ...nuevo, titulo: e.target.value })} minLength={5} required /></label>
        <label>Tema<select value={nuevo.tema} onChange={(e) => setNuevo({ ...nuevo, tema: e.target.value })}>{TEMAS.map((t) => <option key={t}>{t}</option>)}</select></label>
        <label>Nivel (1 a 5)<input type="number" min={1} max={5} value={nuevo.nivel_dificultad}
          onChange={(e) => setNuevo({ ...nuevo, nivel_dificultad: Number(e.target.value) })} /></label>
        <label>Descripción en lenguaje sencillo<textarea value={nuevo.descripcion} minLength={20} required
          onChange={(e) => setNuevo({ ...nuevo, descripcion: e.target.value })} /></label>
        <label>Datos del paciente simulado<textarea value={nuevo.contexto_simulado} minLength={10} required
          onChange={(e) => setNuevo({ ...nuevo, contexto_simulado: e.target.value })} /></label>
        <button className="primario">Crear caso</button>
      </form>
    </section>
  );
}

function EditorEtapa({ idCaso, alGuardar }: { idCaso: number; alGuardar: (m: string) => void }) {
  const [orden, setOrden] = useState(1);
  const [enunciado, setEnunciado] = useState("");
  const [recomendacion, setRecomendacion] = useState("");
  const [opciones, setOpciones] = useState<Opcion[]>([{ ...OPCION_VACIA, es_correcta: true, puntaje: 100 }, { ...OPCION_VACIA, recomendada_ia: true }]);
  const [archivo, setArchivo] = useState<File | null>(null);
  const [dataset, setDataset] = useState("");
  const [licencia, setLicencia] = useState("");
  const [datasets, setDatasets] = useState<{ id_dataset: number; nombre: string; licencia: string }[]>([]);
  useEffect(() => { api<typeof datasets>("/datasets").then(setDatasets); }, []);

  const cambiar = (i: number, c: Partial<Opcion>) =>
    setOpciones(opciones.map((o, j) => {
      const base = { ...o };
      if (c.es_correcta) base.es_correcta = false;
      if (c.recomendada_ia) base.recomendada_ia = false;
      return j === i ? { ...o, ...c } : base;
    }));

  const guardar = async (e: FormEvent) => {
    e.preventDefault();
    try {
      const r = await enviar<{ id_etapa: number }>(`/editor/casos/${idCaso}/etapas`, "PUT",
        { orden, enunciado, recomendacion_ia: recomendacion, opciones });
      if (archivo) {
        const f = new FormData();
        f.append("archivo", archivo);
        f.append("id_dataset", dataset);
        f.append("licencia", licencia);
        await enviar(`/editor/etapas/${r.id_etapa}/recursos`, "POST", f);
      }
      alGuardar(`Etapa ${orden} guardada. El caso queda en borrador hasta su revisión.`);
    } catch (err) { alGuardar((err as Error).message); }
  };

  return (
    <form className="tarjeta" onSubmit={guardar}>
      <h2>Etapa del caso #{idCaso}</h2>
      <label>Orden<input type="number" min={1} value={orden} onChange={(e) => setOrden(Number(e.target.value))} /></label>
      <label>Enunciado<textarea value={enunciado} onChange={(e) => setEnunciado(e.target.value)} minLength={10} required /></label>
      <label>Recomendación de la IA (texto que verá el usuario)<textarea value={recomendacion} minLength={10} required
        onChange={(e) => setRecomendacion(e.target.value)} /></label>
      {opciones.map((o, i) => (
        <fieldset key={i}>
          <legend>Opción {i + 1}</legend>
          <label>Texto<input value={o.texto} onChange={(e) => cambiar(i, { texto: e.target.value })} required /></label>
          <label>Puntaje (0 a 100)<input type="number" min={0} max={100} value={o.puntaje} onChange={(e) => cambiar(i, { puntaje: Number(e.target.value) })} /></label>
          <label>Explicación<textarea value={o.retroalimentacion} minLength={10} required onChange={(e) => cambiar(i, { retroalimentacion: e.target.value })} /></label>
          <label>Fuente<input value={o.fuente} minLength={5} required onChange={(e) => cambiar(i, { fuente: e.target.value })} /></label>
          <label className="casilla"><input type="radio" name="correcta" checked={o.es_correcta} onChange={() => cambiar(i, { es_correcta: true })} />Solución esperada</label>
          <label className="casilla"><input type="radio" name="ia" checked={o.recomendada_ia} onChange={() => cambiar(i, { recomendada_ia: true })} />La IA recomienda esta opción</label>
        </fieldset>
      ))}
      <p className="meta">Si la IA recomienda una opción que no es la solución esperada, la etapa queda marcada como error intencional (no lo verá el usuario).</p>
      <button type="button" onClick={() => setOpciones([...opciones, { ...OPCION_VACIA }])}>Agregar opción</button>
      <fieldset>
        <legend>Imagen o video (JPG, PNG o MP4)</legend>
        <input type="file" accept=".jpg,.jpeg,.png,.mp4" onChange={(e) => setArchivo(e.target.files?.[0] ?? null)} />
        <label>Dataset público<select value={dataset} onChange={(e) => {
          setDataset(e.target.value);
          setLicencia(datasets.find((d) => String(d.id_dataset) === e.target.value)?.licencia ?? "");
        }} required={!!archivo}>
          <option value="">Elige el dataset</option>
          {datasets.map((d) => <option key={d.id_dataset} value={d.id_dataset}>{d.nombre}</option>)}
        </select></label>
        <label>Licencia<input value={licencia} onChange={(e) => setLicencia(e.target.value)} required={!!archivo} /></label>
      </fieldset>
      <button className="primario">Guardar etapa</button>
    </form>
  );
}
