/**
 * Tipos de datos compartidos en el frontend.
 *
 * Estos tipos son el "espejo" en TypeScript de los schemas del backend. Definir
 * la forma de los datos aquí hace que el editor te autocomplete y que TS te
 * avise si usas un campo que no existe o con el tipo equivocado.
 */

// Los tres estados posibles. Es una "union de literales": la variable solo puede
// tener exactamente uno de estos textos, nada más.
export type CourseStatus = "todo" | "in_progress" | "done";

// Un curso tal como lo DEVUELVE la API (incluye id y fechas).
export interface Course {
  id: number;
  title: string;
  url: string | null;
  platform: string | null;
  status: CourseStatus;
  progress: number;
  notes: string | null;
  created_at: string; // las fechas viajan como texto ISO en el JSON
  updated_at: string;
}

// Lo que ENVIAMOS para crear un curso (sin id ni fechas: los pone el server).
export interface CourseCreate {
  title: string;
  url?: string | null;
  platform?: string | null;
  status?: CourseStatus;
  progress?: number;
  notes?: string | null;
}

// Lo que ENVIAMOS para actualizar: todo opcional (edición parcial con PATCH).
export interface CourseUpdate {
  title?: string;
  url?: string | null;
  platform?: string | null;
  status?: CourseStatus;
  progress?: number;
  notes?: string | null;
}
