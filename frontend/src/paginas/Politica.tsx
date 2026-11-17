// RF-001 1.1 y RF-009: texto de la política de tratamiento de datos personales (Ley 1581 de 2012 y Decreto 1377 de 2013)
export default function Politica({ volver }: { volver: () => void }) {
  return (
    <section className="politica">
      <h1>Política de tratamiento de datos personales</h1>
      <p className="meta">
        Versión 1.0 · Fecha de entrada en vigencia: 9 de noviembre de 2026 · Ley 1581 de 2012 y Decreto 1377 de 2013 (Colombia)
      </p>

      <div className="tarjeta">
        <h2>1. Responsable, contacto y alcance educativo</h2>
        <p>
          <strong>Colorrectal-Sim</strong> es una plataforma académica y educativa de simulación desarrollada por el equipo
          <strong> Medical programmers</strong> en el marco del proyecto <strong>ONCO-AI_USC 2026 B</strong> (Línea 2 ONCO-SIM,
          Universidad Santiago de Cali, Cali, Colombia). Su propósito es apoyar el aprendizaje sobre la detección e interpretación de
          hallazgos en colonoscopia. Los resultados generados por inteligencia artificial son experimentales y no reemplazan la
          valoración de un profesional de la salud.
        </p>
        <p className="meta">
          <strong>Canal de contacto del responsable:</strong> módulo <strong>Mis datos</strong> dentro de la plataforma y canal de
          atención del proyecto en <code>https://github.com/rivasnico356-png/colorrectal-sim/issues</code>.
        </p>
      </div>

      <div className="tarjeta">
        <h2>2. Datos personales que recolectamos</h2>
        <ul>
          <li><strong>Datos de cuenta:</strong> nombre, correo electrónico, rango de edad, rol y contraseña protegida mediante hash (bcrypt).</li>
          <li><strong>Datos de actividad educativa:</strong> respuestas en etapas de simulación, nivel de confianza reportado, preguntas al tutor de IA, puntajes, niveles e insignias.</li>
          <li><strong>Datos sensibles de salud (opcional):</strong> imágenes de estudios propios que decidas subir. Antes de guardarlas se eliminan los metadatos (EXIF y DICOM) y los archivos se almacenan cifrados (Fernet).</li>
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
        <p>En cualquier momento puedes ejercer tus derechos directamente desde la sección <strong>Mis datos</strong>:</p>
        <ul>
          <li><strong>Conocer y consultar</strong> todos los datos personales, vínculos y autorizaciones registradas junto con su versión y fecha.</li>
          <li><strong>Actualizar y rectificar</strong> tu nombre y rango de edad.</li>
          <li><strong>Revocar</strong> las autorizaciones opcionales (datos sensibles y compartir avance) o terminar el vínculo con un profesional de la salud.</li>
          <li><strong>Suprimir tu cuenta:</strong> elimina tu nombre y correo, revoca las autorizaciones, cierra los vínculos activos y borra de forma definitiva tus estudios propios cifrados, interpretaciones y comentarios.</li>
        </ul>
      </div>

      <div className="tarjeta">
        <h2>5. Procedimiento para consultas y reclamos (Decreto 1377 de 2013, art. 13)</h2>
        <p>
          Además de las opciones inmediatas disponibles en la sección <strong>Mis datos</strong>, el titular o sus causahabientes
          pueden presentar consultas o reclamos a través del canal de contacto del responsable:
        </p>
        <ul>
          <li>
            <strong>Consultas (art. 14, Ley 1581 de 2012):</strong> se atenderán en un término máximo de <strong>diez (10) días hábiles</strong> contados
            a partir de la fecha de recibo. Si no fuere posible atenderla dentro de dicho término, se informarán los motivos de la
            demora y la fecha de respuesta, que no superará los <strong>cinco (5) días hábiles</strong> siguientes al vencimiento del primer plazo.
          </li>
          <li>
            <strong>Reclamos de corrección, actualización, supresión o revocatoria (art. 15, Ley 1581 de 2012):</strong> se atenderán
            en un término máximo de <strong>quince (15) días hábiles</strong> contados a partir del día siguiente a la fecha de su recibo.
            Si el reclamo está incompleto, se requerirá al interesado dentro de los cinco (5) días hábiles siguientes para subsanar las
            fallas. Cuando no sea posible atenderlo dentro del término inicial, se informarán los motivos y la nueva fecha de respuesta,
            sin superar los <strong>ocho (8) días hábiles</strong> siguientes al vencimiento del primer término.
          </li>
        </ul>
      </div>

      <div className="tarjeta">
        <h2>6. Medidas de seguridad y vigencia</h2>
        <p>
          Aplicamos control de acceso por roles, contraseñas con hash seguro (bcrypt), invalidación de sesión al salir, cifrado en
          reposo (Fernet) para los estudios propios y registro en bitácora de las modificaciones de datos y de cada consulta realizada
          por profesionales vinculados.
        </p>
        <p className="meta">
          <strong>Vigencia:</strong> esta política rige desde el 9 de noviembre de 2026 (versión 1.0). Los datos personales se
          conservan mientras la cuenta permanezca activa con fines educativos o hasta que la persona titular solicite su supresión.
        </p>
      </div>

      <button type="button" className="primario" onClick={volver}>Volver</button>
    </section>
  );
}
