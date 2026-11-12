import { useEffect, useState } from "react";
import { api, BASE, enviar, fecha, tokenActual } from "../api";

type Fila = { id_estudio: number; fecha_carga: string; procesado: boolean; compartido_con: string | null; comentarios_nuevos: number };
type Roi = { x: number; y: number; ancho: number; alto: number };
type Detalle = {
  id_estudio: number; advertencia_texto: boolean;
  interpretacion: { roi: Roi | Record<string, never>; clasificacion: string; confianza: number; explicacion: string; rotulo: string } | null;
  comentarios: { id_comentario: number; profesional: string; texto: string; fecha: string }[];
};
type Vinculo = { id_vinculo: number; nombre: string };

export function ImagenEstudio({ id, roi }: { id: number; roi?: Roi | Record<string, never> }) {
  const [url, setUrl] = useState<string | null>(null);
  useEffect(() => {
    let liberar = "";
    fetch(`${BASE}/estudios/${id}/imagen`, { headers: { Authorization: `Bearer ${tokenActual()}` } })
      .then((r) => r.blob()).then((b) => { liberar = URL.createObjectURL(b); setUrl(liberar); });
    return () => URL.revokeObjectURL(liberar);
  }, [id]);
  return (
    <div className="roi-contenedor">
      {url && <img src={url} alt="Imagen del estudio sin datos personales" />}
      {roi && "x" in roi && (
        <div className="roi" style={{ left: `${roi.x * 100}%`, top: `${roi.y * 100}%`, width: `${roi.ancho * 100}%`, height: `${roi.alto * 100}%` }} />
      )}
    </div>
  );
}

// Pantalla 09 · RF-010
export default function Estudios() {
  const [filas, setFilas] = useState<Fila[]>([]);
  const [vinculos, setVinculos] = useState<Vinculo[]>([]);
  const [detalle, setDetalle] = useState<Detalle | null>(null);
  const [archivo, setArchivo] = useState<File | null>(null);
  const [confirma, setConfirma] = useState(false);
  const [msg, setMsg] = useState("");
  const [cargando, setCargando] = useState(false);

  const cargar = () => Promise.all([api<Fila[]>("/estudios"), api<Vinculo[]>("/vinculos")])
    .then(([f, v]) => { setFilas(f); setVinculos(v); }).catch((e) => setMsg(e.message));
  useEffect(() => { cargar(); }, []);

  const abrir = async (id: number) => setDetalle(await api<Detalle>(`/estudios/${id}`));

  const subir = async () => {
    if (!archivo) return;
    setCargando(true);
    setMsg("");
    const f = new FormData();
    f.append("archivo", archivo);
    f.append("confirma_sin_datos_visibles", String(confirma));
    try {
      const r = await enviar<{ id_estudio: number; procesado: boolean; advertencia: string | null }>("/estudios", "POST", f);
      setMsg(r.advertencia ?? (r.procesado ? "Estudio cargado e interpretado." : "Estudio cargado. El modelo de visión aún no está disponible."));
      await cargar();
      await abrir(r.id_estudio);
    } catch (e) { setMsg((e as Error).message); } finally { setCargando(false); }
  };

  return (
    <section>
      <h1>Mis estudios</h1>
      {msg && <p className="aviso" role="status">{msg}</p>}
      <div className="tarjeta">
        <h2>Cargar un estudio</h2>
        <p className="meta">JPG, PNG o DICOM, hasta 20 MB. Antes de guardarlo quitamos los datos personales del archivo y lo guardamos cifrado.</p>
        <label>Archivo del estudio
          <input type="file" accept=".jpg,.jpeg,.png,.dcm" onChange={(e) => setArchivo(e.target.files?.[0] ?? null)} /></label>
        <label className="casilla"><input type="checkbox" checked={confirma} onChange={(e) => setConfirma(e.target.checked)} />
          Confirmo que la imagen no muestra mi nombre, documento ni otros datos escritos sobre ella.</label>
        <button className="primario" onClick={subir} disabled={!archivo || cargando}>{cargando ? "Analizando… (puede tardar unos segundos)" : "Cargar"}</button>
      </div>
      <table>
        <thead><tr><th>Fecha</th><th>Estado</th><th>Compartido con</th><th></th></tr></thead>
        <tbody>{filas.map((f) => (
          <tr key={f.id_estudio}>
            <td>{fecha(f.fecha_carga)}</td>
            <td>{f.procesado ? "Procesado" : "Pendiente"}{f.comentarios_nuevos > 0 && <strong> · {f.comentarios_nuevos} comentario nuevo</strong>}</td>
            <td>
              <select value={vinculos.find((v) => v.nombre === f.compartido_con)?.id_vinculo ?? ""} aria-label="Compartir con"
                onChange={(e) => enviar(`/estudios/${f.id_estudio}/compartir`, "PUT", { id_vinculo: e.target.value ? Number(e.target.value) : null })
                  .then(cargar).catch((er) => setMsg(er.message))}>
                <option value="">No compartido</option>
                {vinculos.map((v) => <option key={v.id_vinculo} value={v.id_vinculo}>{v.nombre}</option>)}
              </select>
            </td>
            <td className="acciones">
              <button onClick={() => abrir(f.id_estudio)}>Ver</button>
              <button className="enlace" onClick={() => {
                if (confirm("¿Eliminar este estudio y su interpretación? No se puede deshacer."))
                  enviar(`/estudios/${f.id_estudio}`, "DELETE").then(() => { setDetalle(null); cargar(); });
              }}>Eliminar</button>
            </td>
          </tr>
        ))}</tbody>
      </table>
      {detalle && <VistaEstudio d={detalle} />}
    </section>
  );
}

export function VistaEstudio({ d, comentar }: { d: Detalle; comentar?: (texto: string) => void }) {
  const [texto, setTexto] = useState("");
  const i = d.interpretacion;
  return (
    <div className="tarjeta">
      <div className="columnas dos">
        <ImagenEstudio id={d.id_estudio} roi={i?.roi} />
        <div>
          {i ? (
            <>
              <h2>{i.clasificacion} · confianza {i.confianza} %</h2>
              <p className="rotulo">{i.rotulo}</p>
              <p className="meta">La confianza indica qué tan parecido es lo que ve el modelo a los ejemplos con que fue entrenado; no es una probabilidad de enfermedad.</p>
              <p>{i.explicacion}</p>
            </>
          ) : <p>El modelo de visión aún no está disponible para este estudio.</p>}
          {d.advertencia_texto && <p className="aviso">La imagen podría tener texto sobreimpreso. Revisa que no muestre tus datos.</p>}
          <h3>Comentarios de tu profesional</h3>
          {d.comentarios.length === 0 && <p className="meta">Sin comentarios.</p>}
          {d.comentarios.map((c) => <p key={c.id_comentario}><strong>{c.profesional}:</strong> {c.texto} <small className="meta">{fecha(c.fecha)}</small></p>)}
          {comentar && (
            <form className="fila" onSubmit={(e) => { e.preventDefault(); comentar(texto); setTexto(""); }}>
              <label>Comentario educativo<textarea value={texto} onChange={(e) => setTexto(e.target.value)} minLength={3} required /></label>
              <button>Comentar</button>
            </form>
          )}
        </div>
      </div>
    </div>
  );
}

export type { Detalle };
