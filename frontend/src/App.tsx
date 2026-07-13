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
import Board from "./components/Board";
import ItemForm, { KIND_LABEL } from "./components/ItemForm";
import type { Item, ItemCreate, ItemKind, ItemUpdate, User } from "./types";

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

  // Filtro por tipo ("all" = mostrar todo) y visibilidad del formulario.
  const [kindFilter, setKindFilter] = useState<ItemKind | "all">("all");
  const [showForm, setShowForm] = useState(false);

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
    setShowForm(false); // creado el item, el formulario se recoge solo
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

  // El tablero muestra solo los items del tipo elegido ("all" = todos).
  // Esto es "estado derivado": no guardamos la lista filtrada en useState,
  // la calculamos en cada render a partir de items + kindFilter. Menos
  // estados = menos formas de que se desincronicen.
  const visibleItems = kindFilter === "all" ? items : items.filter((it) => it.kind === kindFilter);

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

      <div className="toolbar">
        {/* Filtros por tipo: un "chip" por cada tipo + uno para ver todo. */}
        <div className="filters">
          <button
            className={`chip ${kindFilter === "all" ? "active" : ""}`}
            onClick={() => setKindFilter("all")}
          >
            Todos
          </button>
          {Object.entries(KIND_LABEL).map(([value, label]) => (
            <button
              key={value}
              className={`chip ${kindFilter === value ? "active" : ""}`}
              onClick={() => setKindFilter(value as ItemKind)}
            >
              {label}
            </button>
          ))}
        </div>

        <button className="btn-primary" onClick={() => setShowForm((v) => !v)}>
          {showForm ? "Cerrar" : "+ Nueva meta"}
        </button>
      </div>

      {showForm && <ItemForm onCreate={handleCreate} />}

      {loadingItems && <div className="state-msg">Cargando items...</div>}
      {error && <div className="state-msg">Error: {error}</div>}

      {!loadingItems && !error && (
        <Board items={visibleItems} onUpdate={handleUpdate} onDelete={handleDelete} />
      )}
    </div>
  );
}
