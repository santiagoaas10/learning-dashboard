/**
 * Componente raíz de la app.
 *
 * App es el "cerebro": maneja la sesión (¿quién está logueado?) y los items.
 * Los componentes hijos (AuthForm, ItemForm, ItemCard) solo muestran datos y
 * avisan a App cuando el usuario hace algo.
 *
 * La app tiene dos "pantallas" y App decide cuál mostrar:
 * - Sin sesión -> AuthForm (login/registro).
 * - Con sesión -> el dashboard con los items del usuario.
 */
import { useEffect, useState } from "react";

import * as api from "./api";
import AuthForm from "./components/AuthForm";
import ItemCard from "./components/ItemCard";
import ItemForm from "./components/ItemForm";
import type { Item, ItemCreate, ItemUpdate, User } from "./types";

export default function App() {
  // --- Estado de sesión ---
  // `user === null` puede significar dos cosas: "aún no sé" (mientras verifico
  // el token guardado) o "no hay sesión". `checkingSession` distingue ambas
  // para no mostrar un flash del login a quien SÍ tiene sesión válida.
  const [user, setUser] = useState<User | null>(null);
  const [checkingSession, setCheckingSession] = useState(true);

  // --- Estado de los items ---
  const [items, setItems] = useState<Item[]>([]);
  const [loadingItems, setLoadingItems] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Al abrir la página: si hay un token guardado, preguntamos a la API quién
  // somos. Si responde 401 (token vencido), lo borramos y mostramos el login.
  useEffect(() => {
    if (!api.getToken()) {
      setCheckingSession(false);
      return;
    }
    api
      .me()
      .then(setUser)
      .catch(() => api.clearToken())
      .finally(() => setCheckingSession(false));
  }, []);

  // Cuando hay usuario, cargamos SUS items. Este efecto depende de [user]:
  // corre al loguearse y se "resetea" al hacer logout.
  useEffect(() => {
    if (user === null) {
      setItems([]);
      return;
    }
    setLoadingItems(true);
    api
      .listItems()
      .then(setItems)
      .catch(handleApiError)
      .finally(() => setLoadingItems(false));
  }, [user]);

  /** Si la sesión venció (401) cerramos sesión; otros errores se muestran. */
  function handleApiError(e: unknown) {
    if (e instanceof api.ApiError && e.status === 401) {
      handleLogout();
      return;
    }
    setError(e instanceof Error ? e.message : "Algo salió mal");
  }

  // Login o registro: pedimos el token, lo guardamos y preguntamos quién somos.
  // Los errores NO se atrapan aquí: se dejan subir para que AuthForm los muestre.
  async function handleAuth(mode: "login" | "register", email: string, password: string) {
    const { access_token } =
      mode === "login" ? await api.login(email, password) : await api.register(email, password);
    api.saveToken(access_token);
    setUser(await api.me());
  }

  function handleLogout() {
    api.clearToken(); // sin token no hay sesión: borrarlo ES el logout
    setUser(null);
  }

  // --- CRUD de items (igual que antes, pero ahora siempre autenticado) ---

  async function handleCreate(data: ItemCreate) {
    const created = await api.createItem(data);
    setItems((prev) => [...prev, created]);
  }

  async function handleUpdate(id: number, data: ItemUpdate) {
    try {
      const updated = await api.updateItem(id, data);
      setItems((prev) => prev.map((it) => (it.id === id ? updated : it)));
    } catch (e) {
      handleApiError(e);
    }
  }

  async function handleDelete(id: number) {
    try {
      await api.deleteItem(id);
      setItems((prev) => prev.filter((it) => it.id !== id));
    } catch (e) {
      handleApiError(e);
    }
  }

  // --- Render ---

  // Mientras verificamos el token guardado no mostramos nada "comprometido".
  if (checkingSession) {
    return <div className="state-msg">Cargando...</div>;
  }

  // Sin sesión: solo el formulario de login/registro.
  if (user === null) {
    return <AuthForm onSubmit={handleAuth} />;
  }

  // Con sesión: el dashboard.
  return (
    <div className="container">
      <header className="topbar">
        <div>
          <h1>Learning Dashboard</h1>
          <p className="subtitle">Cursos, proyectos, videos y habilidades en un solo lugar.</p>
        </div>
        <div className="session">
          <span className="muted">{user.email}</span>
          <button className="btn-ghost" onClick={handleLogout}>
            Salir
          </button>
        </div>
      </header>

      <ItemForm onCreate={handleCreate} />

      {loadingItems && <div className="state-msg">Cargando items...</div>}
      {error && <div className="state-msg">Error: {error}</div>}
      {!loadingItems && !error && items.length === 0 && (
        <div className="state-msg">Aún no hay nada. ¡Agrega tu primera meta arriba!</div>
      )}

      {items.map((item) => (
        <ItemCard key={item.id} item={item} onUpdate={handleUpdate} onDelete={handleDelete} />
      ))}
    </div>
  );
}
