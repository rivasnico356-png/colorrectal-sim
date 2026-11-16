// RF-001 1.1 y RF-009: texto de la política de tratamiento de datos personales (Ley 1581 de 2012)
export default function Politica({ volver }: { volver: () => void }) {
  return (
    <section className="politica">
      <h1>Política de tratamiento de datos personales</h1>
      <p className="meta">Versión 1.0 · Ley 1581 de 2012 y Decreto 1377 de 2013 (Colombia)</p>

      <div className="tarjeta">
        <h2>1. Responsable y alcance educativo</h2>
        <p>
          <strong>Colorrectal-Sim</strong> es una plataforma académica y educativa de simulación desarrollada en el marco del proyecto
          ONCO-AI_USC (Universidad Santiago de Cali). Su propósito es apoyar el aprendizaje sobre la detección e interpretación de
          hallazgos en colonoscopia. Los resultados generados por inteligencia artificial son experimentales y no reemplazan el
          diagnóstico ni la valoración de un profesional de la salud.
        </p>
      </div>

      <div className="tarjeta">
        <h2>2. Datos personales que recolectamos</h2>
        <ul>
          <li><strong>Datos de cuenta:</strong> nombre, correo electrónico, rango de edad, rol y contraseña protegida mediante hash (bcrypt).</li>
          <li><strong>Datos de actividad educativa:</strong> respuestas en etapas de simulación, nivel de confianza reportado, preguntas al tutor de IA, puntajes, niveles e insignias.</li>
          <li><strong>Datos sensibles de salud (opcional):</strong> imágenes de estudios propios que decidas subir. Antes de guardarlas se eliminan los metadatos (EXIF y DICOM) y los archivos se almacenan cifrados.</li>
        </ul>
      </div>

      <div className="tarjeta">
        <h2>3. Finalidades y autorizaciones</h2>
        <p>El tratamiento se realiza únicamente para fines educativos y de acuerdo con las autorizaciones que otorgues:</p>
        <ul>
          <li><strong>Política de tratamiento (obligatoria):</strong> crear y administrar tu cuenta, guardar tu progreso en los casos simulados y proteger la seguridad de tu sesión.</li>
          <li><strong>Tratamiento de datos sensibles de salud (opcional y revocable):</strong> procesar tus estudios propios con el modelo experimental de visión y guardar su interpretación.</li>
          <li><strong>Compartir avance con tu profesional de la salud (opcional y revocable):</strong> permitir que el profesional que vincules consulte tu progreso y los estudios que decidas compartirle.</li>
          <li><strong>Análisis académico seudonimizado:</strong> exportar estadísticas de desempeño reemplazando tu identidad por un código hash irreversible, sin nombre ni correo.</li>
        </ul>
      </div>

      <div className="tarjeta">
        <h2>4. Derechos del titular (Habeas Data)</h2>
        <p>En cualquier momento puedes ejercer tus derechos desde la sección <strong>Mis datos</strong>:</p>
        <ul>
          <li><strong>Conocer y consultar</strong> todos los datos personales, vínculos y autorizaciones registradas junto con su versión y fecha.</li>
          <li><strong>Actualizar y rectificar</strong> tu nombre y rango de edad.</li>
          <li><strong>Revocar</strong> las autorizaciones opcionales (datos sensibles y compartir avance) o terminar el vínculo con un profesional de la salud.</li>
          <li><strong>Suprimir tu cuenta:</strong> elimina tu nombre y correo, revoca las autorizaciones, cierra los vínculos activos y borra de forma definitiva tus estudios propios cifrados, interpretaciones y comentarios.</li>
        </ul>
      </div>

      <div className="tarjeta">
        <h2>5. Medidas de seguridad y trazabilidad</h2>
        <p>
          Aplicamos control de acceso por roles, contraseñas con hash seguro, invalidación de sesión al salir, cifrado en reposo para
          los estudios propios y registro en bitácora de las modificaciones de datos y de cada consulta realizada por profesionales
          vinculados.
        </p>
      </div>

      <button type="button" className="primario" onClick={volver}>Volver</button>
    </section>
  );
}
