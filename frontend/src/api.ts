// Cliente de la API. La URL base viene de VITE_API_URL (ver .env.example).
const BASE = import.meta.env.VITE_API_URL ?? "http://localhost:8000/api/v1";

export class ErrorApi extends Error {
  constructor(mensaje: string, public estado: number) {
    super(mensaje);
  }
}

export async function api<T>(ruta: string, opciones: RequestInit = {}, token?: string): Promise<T> {
  const r = await fetch(`${BASE}${ruta}`, {
    ...opciones,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...opciones.headers,
    },
  });
  if (!r.ok) {
    const cuerpo = await r.json().catch(() => ({}));
    const detalle = typeof cuerpo.detail === "string" ? cuerpo.detail : "Revisa los datos e inténtalo de nuevo.";
    throw new ErrorApi(detalle, r.status);
  }
  return r.json() as Promise<T>;
}

export interface Caso {
  id_caso: string;
  titulo: string;
  tema: string;
  nivel_dificultad: number;
  etapas: number;
}
