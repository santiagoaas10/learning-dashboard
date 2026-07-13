/**
 * Cliente de API: la única parte del frontend que sabe hablar con el backend.
 *
 * Concentrar aquí todas las llamadas `fetch` es un buen patrón: los componentes
 * solo llaman a estas funciones y no se preocupan por URLs, tokens ni por cómo
 * se hace la petición. Si mañana cambia la URL base, se toca un solo lugar.
 */

import type { Item, ItemCreate, ItemUpdate, TokenResponse, User } from "./types";

// Dónde vive la API. `import.meta.env` son las variables de entorno de Vite:
// en desarrollo no definimos nada y usamos localhost; en producción se define
// VITE_API_URL al hacer el build. El "??" usa el valor de la derecha solo si
// el de la izquierda es undefined.
const BASE_URL: string = import.meta.env.VITE_API_URL ?? "http://127.0.0.1:8000";

// --- Manejo del token de sesión ---
// Guardamos el JWT en localStorage: un almacén clave-valor del navegador que
// SOBREVIVE a recargas y a cerrar la pestaña. Así la sesión persiste sin
// pedir login cada vez.

const TOKEN_KEY = "learning_dashboard_token";

export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY);
}

export function saveToken(token: string): void {
  localStorage.setItem(TOKEN_KEY, token);
}

export function clearToken(): void {
  localStorage.removeItem(TOKEN_KEY);
}

/**
 * Error con el código HTTP incluido.
 *
 * Extender `Error` con el campo `status` deja que quien llame distinga casos:
 * un 401 significa "sesión vencida -> mostrar login", un 409 "email ya usado".
 */
export class ApiError extends Error {
  status: number;

  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

/**
 * Envoltura sobre fetch que centraliza headers, token y manejo de errores.
 *
 * fetch NO lanza error cuando el servidor responde 404 o 500 (solo si la red
 * falla). Por eso revisamos `response.ok` a mano y lanzamos si algo salió mal,
 * para que quien llame pueda hacer try/catch en un solo sitio.
 */
async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const headers: Record<string, string> = { "Content-Type": "application/json" };

  // Si hay sesión, mandamos el "carnet" en cada request. El backend lo
  // verifica y sabe quién somos sin que enviemos el email ni nada más.
  const token = getToken();
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const response = await fetch(`${BASE_URL}${path}`, { headers, ...options });

  if (!response.ok) {
    // Intentamos leer el "detail" que manda FastAPI (p.ej. "Email o
    // contraseña incorrectos."); si no se puede, un mensaje genérico.
    let message = `La API respondió ${response.status} en ${path}`;
    try {
      const body = (await response.json()) as { detail?: string };
      if (typeof body.detail === "string") message = body.detail;
    } catch {
      // el cuerpo no era JSON: nos quedamos con el mensaje genérico
    }
    throw new ApiError(response.status, message);
  }

  // 204 No Content (p.ej. al borrar) no trae cuerpo: no intentamos parsear JSON.
  if (response.status === 204) {
    return undefined as T;
  }

  return response.json() as Promise<T>;
}

// --- Auth ---

// POST /auth/register -> crea la cuenta y devuelve el token (queda logueado).
export function register(email: string, password: string): Promise<TokenResponse> {
  return request<TokenResponse>("/auth/register", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
}

// POST /auth/login -> verifica credenciales y devuelve el token.
export function login(email: string, password: string): Promise<TokenResponse> {
  return request<TokenResponse>("/auth/login", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
}

// GET /auth/me -> la cuenta dueña del token guardado (o 401 si venció).
export function me(): Promise<User> {
  return request<User>("/auth/me");
}

// --- Items (siempre del usuario logueado) ---

// GET /items -> lista de items
export function listItems(): Promise<Item[]> {
  return request<Item[]>("/items");
}

// POST /items -> crea y devuelve el item creado
export function createItem(data: ItemCreate): Promise<Item> {
  return request<Item>("/items", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

// PATCH /items/{id} -> actualiza parcialmente y devuelve el item
export function updateItem(id: number, data: ItemUpdate): Promise<Item> {
  return request<Item>(`/items/${id}`, {
    method: "PATCH",
    body: JSON.stringify(data),
  });
}

// DELETE /items/{id} -> borra (no devuelve cuerpo)
export function deleteItem(id: number): Promise<void> {
  return request<void>(`/items/${id}`, { method: "DELETE" });
}
