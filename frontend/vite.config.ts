import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Configuración de Vite (el servidor de desarrollo y el empaquetador).
// El plugin de React habilita JSX y el "hot reload" (recarga instantánea al guardar).
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173, // el mismo puerto que autorizamos en el CORS del backend
  },
});
