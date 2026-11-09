import { useState } from "react";
import Ingreso from "./paginas/Ingreso";
import Registro from "./paginas/Registro";
import Catalogo from "./paginas/Catalogo";

type Pantalla = "ingreso" | "registro" | "catalogo";

export default function App() {
  const [token, setToken] = useState<string | null>(null);
  const [pantalla, setPantalla] = useState<Pantalla>("ingreso");

  const entrar = (t: string) => {
    setToken(t);
    setPantalla("catalogo");
  };
  const salir = () => {
    setToken(null);
    setPantalla("ingreso");
  };

  return (
    <div className="app">
      <header className="cabecera">
        <span className="marca">Colorrectal-Sim</span>
        {token && <button className="enlace" onClick={salir}>Cerrar sesión</button>}
      </header>
      <main>
        {pantalla === "ingreso" && <Ingreso alEntrar={entrar} irARegistro={() => setPantalla("registro")} />}
        {pantalla === "registro" && <Registro alTerminar={() => setPantalla("ingreso")} />}
        {pantalla === "catalogo" && token && <Catalogo token={token} />}
      </main>
      <footer className="pie">
        Plataforma educativa. Los resultados son experimentales de apoyo y no reemplazan la valoración de su médico.
      </footer>
    </div>
  );
}
