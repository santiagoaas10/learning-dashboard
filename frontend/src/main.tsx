/**
 * Punto de entrada del frontend.
 *
 * Aquí React "monta" la app dentro del <div id="root"> de index.html.
 * A partir de este punto, todo lo que se ve en pantalla lo controla React.
 */
import React from "react";
import ReactDOM from "react-dom/client";

import App from "./App";
import "./index.css";

// document.getElementById("root")! -> el "!" le dice a TS "confía, no es null"
// (sabemos que ese div existe porque está en index.html).
ReactDOM.createRoot(document.getElementById("root")!).render(
  // StrictMode es una ayuda de desarrollo: avisa de prácticas problemáticas.
  // No afecta la app en producción.
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);
