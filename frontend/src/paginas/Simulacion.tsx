import { FormEvent, useEffect, useRef, useState } from "react";
import { api, enviar, EstadoIntento, MEDIA, Recurso, Retro } from "../api";

type Resumen = {
  titulo: string; puntaje_total: number; aciertos: number; etapas: number; tiempo_segundos: number;
  siguio_ia: number; rechazo_ia: number; errores_ia: number; errores_ia_detectados: number;
};

const CONFIANZA = ["Nada seguro", "Poco seguro", "Algo seguro", "Seguro", "Muy seguro"];

// Pantallas 04 a 07 · RF-003, RF-004, RF-005
export default function Simulacion({ idCaso, volver }: { idCaso: number; volver: () => void }) {
  const [aviso, setAviso] = useState<string | null>(null);
  const [intento, setIntento] = useState<number | null>(null);
  const [estado, setEstado] = useState<EstadoIntento | null>(null);
  const [retro, setRetro] = useState<Retro | null>(null);
  const [resumen, setResumen] = useState<Resumen | null>(null);
  const [error, setError] = useState("");

  const iniciar = async (acepto: boolean) => {
    setError("");
    try {
      const r = await enviar<{ id_intento: number }>("/intentos", "POST", { id_caso: idCaso, acepto_aviso: acepto });
      setIntento(r.id_intento);
    } catch (e) {
      const err = e as Error & { estado?: number };
      if (err.estado === 422) {
        const a = await api<{ aviso: string }>("/simulacion/aviso");
        setAviso(a.aviso);
      } else setError(err.message);
    }
  };

  useEffect(() => {
    iniciar(false);
  }, [idCaso]);

  const cargar = async (id: number) => {
    const e = await api<EstadoIntento>(`/intentos/${id}`);
    setEstado(e);
    if (e.estado === "finalizado") setResumen(await api<Resumen>(`/intentos/${id}/resumen`));
  };

  useEffect(() => {
    if (intento) cargar(intento).catch((e) => setError(e.message));
  }, [intento]);

  if (error) return <div className="tarjeta"><p className="error" role="alert">{error}</p><button onClick={volver}>Volver</button></div>;

  // Pantalla 04 · Aviso de alcance (RF-003 3.1)
  if (!intento && aviso)
    return (
      <div className="tarjeta estrecha">
        <h1>Antes de empezar</h1>
        <p>{aviso}</p>
        <button className="primario" onClick={() => iniciar(true)}>Entiendo y quiero continuar</button>
        <button className="enlace" onClick={volver}>Volver al catálogo</button>
      </div>
    );

  if (resumen) return <ResumenCaso r={resumen} volver={volver} />;
  if (!estado) return <p>Cargando caso…</p>;

  if (retro)
    return (
      <Retroalimentacion r={retro} continuar={() => { setRetro(null); cargar(intento!); }} />
    );

  return estado.etapa ? (
    <EtapaVista estado={estado} alDecidir={setRetro} />
  ) : (
    <p>Cargando…</p>
  );
}

function Visor({ recurso, roi }: { recurso: Recurso; roi?: { x: number; y: number; ancho: number; alto: number } | null }) {
  const [zoom, setZoom] = useState(1);
  const fuente = (
    <p className="meta">Fuente: {recurso.dataset ?? "dataset público"}{recurso.licencia ? ` · Licencia: ${recurso.licencia}` : ""}</p>
  );
  if (recurso.tipo === "video") return <VisorVideo recurso={recurso} fuente={fuente} />;
  return (
    <figure className="visor">
      <div className="lienzo">
        <div className="roi-contenedor" style={{ transform: `scale(${zoom})`, transformOrigin: "top left" }}>
          <img src={MEDIA + recurso.url} alt="Imagen de colonoscopia de la etapa" />
          {roi && <div className="roi" style={{ left: `${roi.x * 100}%`, top: `${roi.y * 100}%`, width: `${roi.ancho * 100}%`, height: `${roi.alto * 100}%` }} />}
        </div>
      </div>
      <div className="controles">
        <button onClick={() => setZoom((z) => Math.max(1, z - 0.5))} aria-label="Alejar">−</button>
        <span>{Math.round(zoom * 100)} %</span>
        <button onClick={() => setZoom((z) => Math.min(4, z + 0.5))} aria-label="Acercar">+</button>
      </div>
      {fuente}
    </figure>
  );
}

// RF-003 3.3b: reproducir, pausar y avanzar cuadro a cuadro (se asumen 25 cuadros por segundo)
function VisorVideo({ recurso, fuente }: { recurso: Recurso; fuente: JSX.Element }) {
  const video = useRef<HTMLVideoElement>(null);
  const CUADRO = 1 / 25;
  const mover = (cuadros: number) => {
    const v = video.current;
    if (!v) return;
    v.pause();
    v.currentTime = Math.min(Math.max(0, v.currentTime + cuadros * CUADRO), v.duration || v.currentTime);
  };
  return (
    <figure className="visor">
      <video ref={video} src={MEDIA + recurso.url} controls preload="metadata" playsInline />
      <div className="controles">
        <button type="button" onClick={() => mover(-1)} aria-label="Cuadro anterior">⏮</button>
        <button type="button" onClick={() => (video.current?.paused ? video.current.play() : video.current?.pause())} aria-label="Reproducir o pausar">⏯</button>
        <button type="button" onClick={() => mover(1)} aria-label="Cuadro siguiente">⏭</button>
      </div>
      {fuente}
    </figure>
  );
}

// Pantalla 05 · Resolver etapa (RF-003 3.2–3.5, RF-004)
function EtapaVista({ estado, alDecidir }: { estado: EstadoIntento; alDecidir: (r: Retro) => void }) {
  const etapa = estado.etapa!;
  const [opcion, setOpcion] = useState<number | null>(null);
  const [confianza, setConfianza] = useState<number | null>(null);
  const [error, setError] = useState("");
  const inicio = useRef(Date.now());

  const confirmar = async (e: FormEvent) => {
    e.preventDefault();
    if (!opcion || !confianza) return setError("Elige una opción y tu nivel de confianza.");
    try {
      alDecidir(await enviar<Retro>(`/intentos/${estado.id_intento}/decisiones`, "POST", {
        id_etapa: etapa.id_etapa, id_opcion: opcion, confianza, tiempo_ms: Date.now() - inicio.current,
      }));
    } catch (err) {
      setError((err as Error).message);
    }
  };

  const sugerida = etapa.opciones.find((o) => o.id_opcion === etapa.recomendacion_ia.id_opcion);

  return (
    <section className="etapa">
      <header>
        <p className="meta">{estado.titulo} · Etapa {estado.progreso.actual} de {estado.progreso.total}</p>
        <progress value={estado.progreso.actual - 1} max={estado.progreso.total} />
      </header>
      {estado.progreso.actual === 1 && estado.contexto_simulado && (
        <div className="tarjeta contexto"><strong>Paciente simulado:</strong> {estado.contexto_simulado}</div>
      )}
      <div className="columnas">
        <div>
          {etapa.recursos.map((r, i) => <Visor key={r.url} recurso={r} roi={i === 0 ? etapa.modelo_vision?.roi : null} />)}
          {etapa.modelo_vision && !etapa.modelo_vision.disponible && (
            <p className="aviso">El resultado del modelo de visión estará disponible cuando el modelo experimental esté listo.</p>
          )}
          {etapa.modelo_vision?.disponible && (
            <div className="tarjeta">
              <strong>Modelo de visión: {etapa.modelo_vision.clasificacion} · confianza {etapa.modelo_vision.confianza} %</strong>
              <p className="meta">{etapa.modelo_vision.que_significa}</p>
              <p className="rotulo">{etapa.modelo_vision.rotulo}</p>
            </div>
          )}
        </div>
        <form className="tarjeta" onSubmit={confirmar}>
          <h2>{etapa.enunciado}</h2>
          <fieldset>
            <legend>¿Qué decides?</legend>
            {etapa.opciones.map((o) => (
              <label key={o.id_opcion} className="casilla">
                <input type="radio" name="opcion" checked={opcion === o.id_opcion} onChange={() => setOpcion(o.id_opcion)} />
                {o.texto}
              </label>
            ))}
          </fieldset>
          <fieldset>
            <legend>¿Qué tan seguro estás?</legend>
            <div className="escala">
              {CONFIANZA.map((t, i) => (
                <button type="button" key={t} className={confianza === i + 1 ? "activa" : ""} onClick={() => setConfianza(i + 1)}>
                  {i + 1}<small>{t}</small>
                </button>
              ))}
            </div>
          </fieldset>
          {error && <p className="error" role="alert">{error}</p>}
          <button className="primario">Confirmar decisión</button>
        </form>
        <Tutor estado={estado} sugerida={sugerida?.texto} />
      </div>
    </section>
  );
}

// Panel del tutor IA (RF-004 4.1–4.5, RNF-007)
function Tutor({ estado, sugerida }: { estado: EstadoIntento; sugerida?: string }) {
  const etapa = estado.etapa!;
  const [mensajes, setMensajes] = useState<{ de: "tu" | "ia"; texto: string }[]>([]);
  const [pregunta, setPregunta] = useState("");
  const [restantes, setRestantes] = useState(etapa.tutor.consultas_restantes);
  const [cargando, setCargando] = useState(false);
  const [aviso, setAviso] = useState("");

  const consultar = async (texto?: string) => {
    setCargando(true);
    setAviso("");
    if (texto) setMensajes((m) => [...m, { de: "tu", texto }]);
    try {
      const r = await enviar<{ texto: string; consultas_restantes: number; aviso: string | null }>(
        `/intentos/${estado.id_intento}/etapas/${etapa.id_etapa}/tutor`, "POST", texto ? { pregunta: texto } : {});
      setMensajes((m) => [...m, { de: "ia", texto: r.texto }]);
      setRestantes(r.consultas_restantes);
      if (r.aviso) setAviso(r.aviso);
    } catch (e) {
      setAviso((e as Error).message);
    } finally {
      setCargando(false);
      setPregunta("");
    }
  };

  return (
    <aside className="tarjeta tutor">
      <h2>Tutor IA</h2>
      <p><strong>Sugerencia:</strong> {etapa.recomendacion_ia.texto}{sugerida ? ` (opción: ${sugerida})` : ""}</p>
      <p className="rotulo">{etapa.recomendacion_ia.rotulo}</p>
      <button type="button" onClick={() => consultar()} disabled={cargando}>¿Por qué sugiere esto?</button>
      <div className="chat" aria-live="polite">
        {mensajes.map((m, i) => <p key={i} className={m.de}>{m.texto}</p>)}
        {cargando && <p className="ia cargando">El tutor está escribiendo…</p>}
      </div>
      {aviso && <p className="aviso">{aviso}</p>}
      <form onSubmit={(e) => { e.preventDefault(); if (pregunta.trim()) consultar(pregunta.trim()); }}>
        <input value={pregunta} onChange={(e) => setPregunta(e.target.value)} maxLength={500} disabled={!restantes || cargando}
          placeholder={restantes ? "Pregunta sobre el caso" : "Sin preguntas disponibles en esta etapa"} aria-label="Pregunta al tutor" />
        <p className="meta">Te quedan {restantes} de {etapa.tutor.maximo} preguntas en esta etapa.</p>
      </form>
    </aside>
  );
}

// Pantalla 06 · Retroalimentación (RF-005 5.1–5.3)
function Retroalimentacion({ r, continuar }: { r: Retro; continuar: () => void }) {
  const titulo = { correcto: "¡Correcto!", parcial: "Respuesta parcialmente correcta", incorrecto: "No es la respuesta esperada" };
  return (
    <div className={`tarjeta estrecha retro ${r.resultado}`}>
      <h1>{titulo[r.resultado]}</h1>
      <p className="puntaje">+{r.puntaje} puntos</p>
      {r.resultado !== "correcto" && <p><strong>Respuesta esperada:</strong> {r.respuesta_esperada}</p>}
      {r.explicacion_de_tu_opcion && <p><strong>Sobre tu elección:</strong> {r.explicacion_de_tu_opcion}</p>}
      <p>{r.explicacion}</p>
      {r.fuente && <p className="meta">Fuente: {r.fuente}</p>}
      {r.ia_estaba_equivocada && (
        <p className="aviso">
          En esta etapa la IA estaba equivocada a propósito. {r.detectaste_error_ia ? "¡La cuestionaste bien!" : "Seguiste su sugerencia."}
        </p>
      )}
      {!r.ia_estaba_equivocada && <p className="meta">{r.siguio_ia ? "Seguiste la sugerencia de la IA." : "No seguiste la sugerencia de la IA."}</p>}
      {r.nivel_nuevo && <p className="logro">🎉 Subiste al nivel {r.nivel_nuevo}</p>}
      {r.insignias_nuevas.map((i) => <p key={i} className="logro">🏅 Nueva insignia: {i}</p>)}
      <button className="primario" onClick={continuar}>{r.intento_finalizado ? "Ver resumen" : "Siguiente etapa"}</button>
    </div>
  );
}

// Pantalla 07 · Resumen del caso (RF-005 5.4)
function ResumenCaso({ r, volver }: { r: Resumen; volver: () => void }) {
  const min = Math.floor(r.tiempo_segundos / 60);
  return (
    <div className="tarjeta estrecha">
      <h1>Resumen: {r.titulo}</h1>
      <dl className="cifras">
        <div><dt>Puntaje</dt><dd>{r.puntaje_total}</dd></div>
        <div><dt>Aciertos</dt><dd>{r.aciertos} de {r.etapas}</dd></div>
        <div><dt>Tiempo</dt><dd>{min} min {r.tiempo_segundos % 60} s</dd></div>
        <div><dt>Siguió a la IA</dt><dd>{r.siguio_ia}</dd></div>
        <div><dt>Rechazó a la IA</dt><dd>{r.rechazo_ia}</dd></div>
        <div><dt>Errores de la IA detectados</dt><dd>{r.errores_ia_detectados} de {r.errores_ia}</dd></div>
      </dl>
      <button className="primario" onClick={volver}>Volver al catálogo</button>
    </div>
  );
}
