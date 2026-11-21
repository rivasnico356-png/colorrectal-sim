import { useState } from "react";

type Categoria = "Diagnóstico y estudios" | "Hallazgos y enfermedad" | "Tratamiento y seguimiento" | "Inteligencia artificial y datos";

interface Termino {
  termino: string;
  categoria: Categoria;
  definicion: string;
}

const CATEGORIAS: Categoria[] = [
  "Diagnóstico y estudios",
  "Hallazgos y enfermedad",
  "Tratamiento y seguimiento",
  "Inteligencia artificial y datos",
];

// RNF-008: glosario de términos médicos e IA en español claro y accesible.
const TERMINOS: Termino[] = [
  {
    termino: "Colonoscopia",
    categoria: "Diagnóstico y estudios",
    definicion: "Examen en el que el médico observa el interior del intestino grueso (colon y recto) con una cámara delgada y flexible para buscar pólipos u otras lesiones.",
  },
  {
    termino: "Tamizaje (cribado)",
    categoria: "Diagnóstico y estudios",
    definicion: "Pruebas preventivas que se realizan a personas sin síntomas para detectar el cáncer colorrectal o lesiones previas de forma temprana, cuando es más fácil tratarlo.",
  },
  {
    termino: "Sangre oculta en heces (FIT / SOH)",
    categoria: "Diagnóstico y estudios",
    definicion: "Prueba de laboratorio no invasiva que busca rastros microscópicos de sangre en la materia fecal que no se ven a simple vista.",
  },
  {
    termino: "Biopsia",
    categoria: "Diagnóstico y estudios",
    definicion: "Toma de una pequeña muestra de tejido durante un examen para analizarla en el microscopio y confirmar si las células son benignas o malignas.",
  },
  {
    termino: "DICOM",
    categoria: "Diagnóstico y estudios",
    definicion: "Formato estándar usado por clínicas y hospitales para guardar imágenes médicas junto con datos técnicos del equipo y del estudio.",
  },
  {
    termino: "Pólipo",
    categoria: "Hallazgos y enfermedad",
    definicion: "Crecimiento anormal de tejido en el revestimiento interno del colon o del recto. Muchos son benignos, pero algunos tipos pueden transformarse en cáncer con el tiempo.",
  },
  {
    termino: "Adenoma",
    categoria: "Hallazgos y enfermedad",
    definicion: "Tipo frecuente de pólipo considerado lesión precancerosa: no es cáncer todavía, pero retirarlo a tiempo reduce el riesgo de que evolucione a cáncer colorrectal.",
  },
  {
    termino: "Mucosa y submucosa",
    categoria: "Hallazgos y enfermedad",
    definicion: "Capas más internas de la pared del intestino. Saber hasta qué capa llega una lesión ayuda al equipo médico a definir el tratamiento adecuado.",
  },
  {
    termino: "Estadio (estadiaje TNM)",
    categoria: "Hallazgos y enfermedad",
    definicion: "Clasificación que indica qué tanto ha crecido un tumor en la pared del intestino (T), si compromete ganglios cercanos (N) o si se extendió a otros órganos (M).",
  },
  {
    termino: "Metástasis",
    categoria: "Hallazgos y enfermedad",
    definicion: "Diseminación de células tumorales desde el colon o el recto hacia otros órganos distantes, como el hígado o los pulmones.",
  },
  {
    termino: "Polipectomía",
    categoria: "Tratamiento y seguimiento",
    definicion: "Procedimiento realizado durante la colonoscopia para retirar un pólipo de forma segura y enviarlo a análisis de patología.",
  },
  {
    termino: "Resección (colectomía)",
    categoria: "Tratamiento y seguimiento",
    definicion: "Cirugía en la que se retira la parte del colon o del recto que contiene la lesión junto con los ganglios cercanos.",
  },
  {
    termino: "Quimioterapia",
    categoria: "Tratamiento y seguimiento",
    definicion: "Tratamiento con medicamentos diseñados para destruir células cancerosas o frenar su crecimiento, antes o después de una cirugía según cada caso.",
  },
  {
    termino: "Radioterapia",
    categoria: "Tratamiento y seguimiento",
    definicion: "Uso controlado de radiación dirigida sobre una zona específica (frecuente en cáncer de recto) para reducir el tamaño del tumor o evitar que regrese.",
  },
  {
    termino: "Seguimiento (vigilancia)",
    categoria: "Tratamiento y seguimiento",
    definicion: "Controles médicos y exámenes periódicos después de retirar pólipos o terminar un tratamiento para detectar a tiempo cualquier cambio nuevo.",
  },
  {
    termino: "Región de interés (ROI)",
    categoria: "Inteligencia artificial y datos",
    definicion: "Recuadro que marca el modelo experimental de visión sobre la zona de la imagen donde detecta rasgos parecidos a un pólipo.",
  },
  {
    termino: "Confianza del modelo de IA",
    categoria: "Inteligencia artificial y datos",
    definicion: "Porcentaje que indica qué tan parecida es una imagen a los ejemplos con los que aprendió el modelo. No representa una probabilidad de tener cáncer ni un diagnóstico.",
  },
  {
    termino: "Desidentificación y seudonimización",
    categoria: "Inteligencia artificial y datos",
    definicion: "Técnicas de protección de datos: la desidentificación elimina nombre y metadatos de las imágenes; la seudonimización reemplaza la identidad por un código irreversible al exportar datos académicos.",
  },
];

export default function Glosario({ volver }: { volver: () => void }) {
  const [buscar, setBuscar] = useState("");
  const [categoria, setCategoria] = useState("");

  const q = buscar.trim().toLowerCase();
  const filtrados = TERMINOS.filter((t) => {
    if (categoria && t.categoria !== categoria) return false;
    if (!q) return true;
    return t.termino.toLowerCase().includes(q) || t.definicion.toLowerCase().includes(q);
  });

  return (
    <section className="glosario">
      <h1>Glosario de términos médicos</h1>
      <p className="meta">
        Explicaciones sencillas de los términos más frecuentes en colonoscopia, cáncer colorrectal e inteligencia artificial aplicada a imágenes médicas.
      </p>

      <div className="filtros">
        <label>
          Buscar término
          <input
            type="search"
            placeholder="Ej. pólipo, biopsia, estadio…"
            value={buscar}
            onChange={(e) => setBuscar(e.target.value)}
          />
        </label>
        <label>
          Categoría
          <select value={categoria} onChange={(e) => setCategoria(e.target.value)}>
            <option value="">Todas las categorías</option>
            {CATEGORIAS.map((c) => (
              <option key={c} value={c}>{c}</option>
            ))}
          </select>
        </label>
      </div>

      {filtrados.length === 0 ? (
        <p className="aviso" role="status">No encontramos términos que coincidan con «{buscar}».</p>
      ) : (
        <dl className="glosario-lista">
          {filtrados.map((item) => (
            <div key={item.termino} className="tarjeta glosario-item">
              <span className="etiqueta">{item.categoria}</span>
              <dt>{item.termino}</dt>
              <dd>{item.definicion}</dd>
            </div>
          ))}
        </dl>
      )}

      <p className="rotulo">
        Este glosario es educativo e informativo. Ante cualquier duda sobre un examen, diagnóstico o tratamiento, consulte siempre a su médico.
      </p>
      <button type="button" className="primario" onClick={volver}>Volver</button>
    </section>
  );
}
