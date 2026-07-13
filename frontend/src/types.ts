/**
 * Tipos de datos compartidos en el frontend.
 *
 * Estos tipos son el "espejo" en TypeScript de los schemas del backend. Definir
 * la forma de los datos aquí hace que el editor te autocomplete y que TS te
 * avise si usas un campo que no existe o con el tipo equivocado.
 */

// "Uniones de literales": la variable solo puede tener exactamente uno de
// estos textos. Son el espejo de los Enums de Python del backend.
export type ItemKind = "course" | "project" | "video" | "skill";
export type ItemStatus = "backlog" | "todo" | "in_progress" | "done";
export type ItemPriority = "low" | "medium" | "high" | "urgent";

// Un item tal como lo DEVUELVE la API (incluye id y fechas).
export interface Item {
  id: number;
  title: string;
  kind: ItemKind;
  url: string | null;
  platform: string | null;
  status: ItemStatus;
  priority: ItemPriority;
  due_date: string | null; // "2026-08-30" (las fechas viajan como texto en JSON)
  progress: number;
  notes: string | null;
  created_at: string;
  updated_at: string;
}

// Lo que ENVIAMOS para crear un item (sin id ni fechas de auditoría).
export interface ItemCreate {
  title: string;
  kind?: ItemKind;
  url?: string | null;
  platform?: string | null;
  status?: ItemStatus;
  priority?: ItemPriority;
  due_date?: string | null;
  progress?: number;
  notes?: string | null;
}

// Lo que ENVIAMOS para actualizar: todo opcional (edición parcial con PATCH).
export interface ItemUpdate {
  title?: string;
  kind?: ItemKind;
  url?: string | null;
  platform?: string | null;
  status?: ItemStatus;
  priority?: ItemPriority;
  due_date?: string | null;
  progress?: number;
  notes?: string | null;
}

// --- Auth ---

// La cuenta logueada (lo que devuelve GET /auth/me).
export interface User {
  id: number;
  email: string;
}

// Respuesta de /auth/register y /auth/login.
export interface TokenResponse {
  access_token: string;
  token_type: string;
}
