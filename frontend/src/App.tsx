import { useEffect, useState } from "react";
import { api, enviar, fijarToken, Rol } from "./api";
import Admin from "./paginas/Admin";
import Catalogo from "./paginas/Catalogo";
import Estudios from "./paginas/Estudios";
import Glosario from "./paginas/Glosario";
import Ingreso from "./paginas/Ingreso";
import Politica from "./paginas/Politica";
import Privacidad from "./paginas/Privacidad";
import { EditorCasos, EstudiosCompartidos, PanelProfesional } from "./paginas/Profesional";
import Progreso from "./paginas/Progreso";
import { Recuperar, Restablecer } from "./paginas/Recuperar";
import Registro, { DatosRegistro, REGISTRO_INICIAL } from "./paginas/Registro";
import Simulacion from "./paginas/Simulacion";

type Pantalla = "ingreso" | "registro" | "recuperar" | "restablecer" | "politica" | "glosario" | "catalogo" | "simulacion" | "progreso"
  | "estudios" | "privacidad" | "panel" | "compartidos" | "casos" | "admin";
type Sesion = { token: string; rol: Rol };
type TamanoTexto = "normal" | "grande" | "muy-grande";

const TAMANOS_TEXTO: [TamanoTexto, string, string][] = [
  ["normal", "A", "Tamaño de letra normal"],
  ["grande", "A+", "Tamaño de letra grande"],
  ["muy-grande", "A++", "Tamaño de letra muy grande"],
];

// Menús según el rol (RF-001 1.4)
const MENU: Record<Rol, [Pantalla, string][]> = {
  Usuario: [["catalogo", "Casos"], ["progreso", "Mi progreso"], ["estudios", "Mis estudios"], ["privacidad", "Mis datos"]],
  "Profesional de la salud": [["panel", "Usuarios vinculados"], ["compartidos", "Estudios compartidos"], ["casos", "Casos clínicos"],
    ["privacidad", "Mis datos"]],
  Administrador: [["admin", "Usuarios y roles"], ["casos", "Casos clínicos"]],
};
const INICIO: Record<Rol, Pantalla> = { Usuario: "catalogo", "Profesional de la salud": "panel", Administrador: "admin" };

function leerSesion(): Sesion | null {
  try {
    const s = sessionStorage.getItem("sesion");
    return s ? (JSON.parse(s) as Sesion) : null;
  } catch {
    return null;
  }
}

function leerTamanoTexto(): TamanoTexto {
  try {
    const t = localStorage.getItem("tamano_texto");
    return t === "grande" || t === "muy-grande" ? t : "normal";
  } catch {
    return "normal";
  }
}

export default function App() {
  const [sesion, setSesion] = useState<Sesion | null>(leerSesion);
  const tokenEnlace = window.location.hash.startsWith("#restablecer=") ? window.location.hash.slice(13) : "";
  const [pantalla, setPantalla] = useState<Pantalla>(tokenEnlace ? "restablecer" : sesion ? INICIO[sesion.rol] : "ingreso");
  const [origenPolitica, setOrigenPolitica] = useState<Pantalla>("registro");
  const [origenGlosario, setOrigenGlosario] = useState<Pantalla>("ingreso");
  const [tamanoTexto, setTamanoTexto] = useState<TamanoTexto>(leerTamanoTexto);
  const [datosRegistro, setDatosRegistro] = useState<DatosRegistro>(REGISTRO_INICIAL);
  const [caso, setCaso] = useState<number | null>(null);
  const [avisos, setAvisos] = useState(0);

  // RNF-008: aplica y guarda la preferencia de tamaño de letra
  useEffect(() => {
    document.documentElement.dataset.texto = tamanoTexto;
    try {
      localStorage.setItem("tamano_texto", tamanoTexto);
    } catch {
      /* el almacenamiento del navegador puede no estar disponible */
    }
  }, [tamanoTexto]);

  // RF-010 10.4: aviso de comentarios nuevos del profesional
  useEffect(() => {
    if (sesion?.rol !== "Usuario") return;
    const revisar = () => api<{ comentarios_nuevos: number }>("/notificaciones").then((r) => setAvisos(r.comentarios_nuevos)).catch(() => undefined);
    revisar();
    const t = setInterval(revisar, 60000);
    return () => clearInterval(t);
  }, [sesion, pantalla]);

  useEffect(() => {
    fijarToken(sesion?.token ?? null);
    try {
      if (sesion) sessionStorage.setItem("sesion", JSON.stringify(sesion));
      else sessionStorage.removeItem("sesion");
    } catch {
      /* el almacenamiento del navegador puede no estar disponible */
    }
  }, [sesion]);

  const entrar = (token: string, rol: Rol) => {
    fijarToken(token);
    setSesion({ token, rol });
    setPantalla(INICIO[rol]);
  };

  const salir = async () => {
    await enviar("/auth/logout", "POST").catch(() => undefined); // RF-001 1.2b
    setSesion(null);
    setPantalla("ingreso");
  };

  const abrirGlosario = () => {
    if (pantalla !== "glosario") setOrigenGlosario(pantalla);
    setPantalla("glosario");
  };

  if (sesion) fijarToken(sesion.token);

  return (
    <div className="app">
      <header className="cabecera">
        <span className="marca">
          <img src="/isotipo.png" alt="" className="marca-logo" width={44} height={44} />
          <span>Colorrectal-Sim</span>
        </span>
        <div className="cabecera-acciones">
          <nav aria-label="Navegación principal">
            {sesion && MENU[sesion.rol].map(([p, t]) => (
              <button key={p} type="button" className={`enlace ${pantalla === p ? "actual" : ""}`} onClick={() => setPantalla(p)}>
                {t}{p === "estudios" && avisos > 0 && <span className="contador" aria-label={`${avisos} comentarios nuevos`}>{avisos}</span>}
              </button>
            ))}
            <button type="button" className={`enlace ${pantalla === "glosario" ? "actual" : ""}`} onClick={abrirGlosario}>
              Glosario
            </button>
            {sesion && <button type="button" className="enlace" onClick={salir}>Cerrar sesión</button>}
          </nav>
          <div className="tamano-texto" role="group" aria-label="Tamaño de letra">
            {TAMANOS_TEXTO.map(([valor, rotulo, descripcion]) => (
              <button
                key={valor}
                type="button"
                className={tamanoTexto === valor ? "activo" : ""}
                aria-label={descripcion}
                aria-pressed={tamanoTexto === valor}
                title={descripcion}
                onClick={() => setTamanoTexto(valor)}
              >
                {rotulo}
              </button>
            ))}
          </div>
        </div>
      </header>
      <main>
        {sesion && pantalla === INICIO[sesion.rol] && (
          <div className="bienvenida-logo">
            <img src="/logo.png" alt="Colorrectal-Sim" className="logo-inicio" />
          </div>
        )}
        {pantalla === "ingreso" && <Ingreso alEntrar={entrar} irARegistro={() => setPantalla("registro")} irARecuperar={() => setPantalla("recuperar")} />}
        {pantalla === "recuperar" && <Recuperar volver={() => setPantalla("ingreso")} />}
        {pantalla === "restablecer" && <Restablecer token={tokenEnlace} terminar={() => { window.location.hash = ""; setPantalla("ingreso"); }} />}
        {pantalla === "registro" && (
          <Registro
            datos={datosRegistro}
            setDatos={setDatosRegistro}
            alTerminar={() => { setDatosRegistro(REGISTRO_INICIAL); setPantalla("ingreso"); }}
            irAPolitica={() => { setOrigenPolitica("registro"); setPantalla("politica"); }}
          />
        )}
        {pantalla === "politica" && <Politica volver={() => setPantalla(origenPolitica)} />}
        {pantalla === "glosario" && <Glosario volver={() => setPantalla(origenGlosario)} />}
        {pantalla === "catalogo" && <Catalogo abrir={(id) => { setCaso(id); setPantalla("simulacion"); }} />}
        {pantalla === "simulacion" && caso && <Simulacion idCaso={caso} volver={() => setPantalla("catalogo")} />}
        {pantalla === "progreso" && <Progreso />}
        {pantalla === "estudios" && <Estudios />}
        {pantalla === "compartidos" && <EstudiosCompartidos />}
        {pantalla === "privacidad" && (
          <Privacidad
            alSuprimir={() => { setSesion(null); setPantalla("ingreso"); }}
            irAPolitica={() => { setOrigenPolitica("privacidad"); setPantalla("politica"); }}
          />
        )}
        {pantalla === "panel" && <PanelProfesional />}
        {pantalla === "casos" && <EditorCasos />}
        {pantalla === "admin" && <Admin />}
      </main>
      <footer className="pie">
        Plataforma educativa de simulación. Los resultados de la IA son experimentales de apoyo a la detección e interpretación y no
        reemplazan la valoración de su médico.
      </footer>
    </div>
  );
}
