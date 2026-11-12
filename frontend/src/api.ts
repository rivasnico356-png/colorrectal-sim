// Cliente de la API. La URL base viene de VITE_API_URL (ver .env.example).
export const BASE = import.meta.env.VITE_API_URL ?? "http://localhost:8000/api/v1";
export const MEDIA = BASE.replace(/\/api\/v1\/?$/, "");

export class ErrorApi extends Error {
  constructor(mensaje: string, public estado: number) {
    super(mensaje);
  }
}

let token: string | null = null;
export const fijarToken = (t: string | null) => {
  token = t;
};

export async function api<T>(ruta: string, opciones: RequestInit = {}): Promise<T> {
  const esFormulario = opciones.body instanceof FormData;
  const r = await fetch(`${BASE}${ruta}`, {
    ...opciones,
    headers: {
      ...(esFormulario ? {} : { "Content-Type": "application/json" }),
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...opciones.headers,
    },
  });
  if (!r.ok) {
    const cuerpo = await r.json().catch(() => ({}));
    const detalle = typeof cuerpo.detail === "string" ? cuerpo.detail : "Revisa los datos e inténtalo de nuevo.";
    throw new ErrorApi(detalle, r.status);
  }
  if (r.status === 204) return undefined as T;
  const tipo = r.headers.get("content-type") ?? "";
  return (tipo.includes("json") ? r.json() : r.text()) as Promise<T>;
}

export const enviar = <T,>(ruta: string, metodo: string, cuerpo?: unknown) =>
  api<T>(ruta, { method: metodo, body: cuerpo instanceof FormData ? cuerpo : JSON.stringify(cuerpo ?? {}) });

export type Rol = "Usuario" | "Profesional de la salud" | "Administrador";

export interface Caso {
  id_caso: number;
  titulo: string;
  tema: string;
  nivel_dificultad: number;
  descripcion: string | null;
  etapas: number;
  estado_usuario: "no_iniciado" | "en_curso" | "completado";
  bloqueado: boolean;
  requisito: string | null;
}

export interface Recurso {
  tipo: "imagen" | "video";
  url: string;
  licencia: string | null;
  dataset: string | null;
  fuente_url: string | null;
}

export interface Etapa {
  id_etapa: number;
  orden: number;
  enunciado: string;
  recursos: Recurso[];
  opciones: { id_opcion: number; texto: string }[];
  recomendacion_ia: { texto: string; id_opcion: number | null; rotulo: string };
  modelo_vision: { disponible: boolean } | null;
  tutor: { consultas_restantes: number; maximo: number };
}

export interface EstadoIntento {
  id_intento: number;
  titulo: string;
  descripcion: string | null;
  contexto_simulado: string | null;
  estado: string;
  progreso: { actual: number; total: number };
  etapa: Etapa | null;
}

export interface Retro {
  resultado: "correcto" | "parcial" | "incorrecto";
  puntaje: number;
  respuesta_esperada: string | null;
  explicacion: string | null;
  fuente: string | null;
  explicacion_de_tu_opcion: string | null;
  siguio_ia: boolean;
  ia_estaba_equivocada: boolean;
  detectaste_error_ia: boolean;
  intento_finalizado: boolean;
  nivel_nuevo: string | null;
  insignias_nuevas: string[];
}

export const TEMAS = ["tamizaje", "pólipos", "estadios", "tratamiento", "seguimiento"];
export const fecha = (f: string | null) => (f ? new Date(f).toLocaleDateString("es-CO") : "—");
