/**
 * Pantalla de login / registro.
 *
 * Un solo componente para ambos casos: un estado `mode` decide si el submit
 * llama a /auth/login o a /auth/register, y un link abajo permite alternar.
 * Compartirlos evita duplicar el formulario entero (los campos son idénticos).
 */
import { useState } from "react";

interface AuthFormProps {
  // App decide qué hacer con las credenciales (llamar a la API, guardar el
  // token...). Este componente solo recolecta email/contraseña y avisa.
  onSubmit: (mode: "login" | "register", email: string, password: string) => Promise<void>;
}

export default function AuthForm({ onSubmit }: AuthFormProps) {
  const [mode, setMode] = useState<"login" | "register">("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [sending, setSending] = useState(false);

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault(); // que el navegador no recargue la página
    setError(null);
    setSending(true);
    try {
      await onSubmit(mode, email.trim(), password);
      // Si sale bien no limpiamos nada: App cambia de pantalla y este
      // componente desaparece.
    } catch (e) {
      // Mostramos el mensaje que mandó la API (p.ej. "Email o contraseña
      // incorrectos.") en vez de fallar en silencio.
      setError(e instanceof Error ? e.message : "Algo salió mal");
    } finally {
      setSending(false);
    }
  }

  return (
    <div className="auth-wrap">
      <form className="card auth-card" onSubmit={handleSubmit}>
        <h2>{mode === "login" ? "Iniciar sesión" : "Crear cuenta"}</h2>

        <div style={{ marginBottom: 12 }}>
          <label htmlFor="email">Email</label>
          <input
            id="email"
            type="email" // el navegador valida el formato y muestra teclado de email en móvil
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="tu@email.com"
            required
            autoComplete="email"
          />
        </div>

        <div style={{ marginBottom: 16 }}>
          <label htmlFor="password">Contraseña</label>
          <input
            id="password"
            type="password" // oculta lo escrito
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="Mínimo 8 caracteres"
            required
            minLength={8}
            // Pista para el gestor de contraseñas del navegador: en registro
            // ofrece generar una nueva; en login ofrece la guardada.
            autoComplete={mode === "register" ? "new-password" : "current-password"}
          />
        </div>

        {error && <div className="auth-error">{error}</div>}

        <button type="submit" className="btn-primary" disabled={sending} style={{ width: "100%" }}>
          {sending ? "Un momento..." : mode === "login" ? "Entrar" : "Registrarme"}
        </button>

        <p className="auth-switch">
          {mode === "login" ? "¿No tienes cuenta?" : "¿Ya tienes cuenta?"}{" "}
          <button
            type="button" // sin esto, un botón dentro de un form hace submit
            className="link-btn"
            onClick={() => {
              setMode(mode === "login" ? "register" : "login");
              setError(null); // el error de un modo no aplica al otro
            }}
          >
            {mode === "login" ? "Regístrate" : "Inicia sesión"}
          </button>
        </p>
      </form>
    </div>
  );
}
