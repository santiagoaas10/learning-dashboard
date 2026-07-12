/**
 * Cliente de API: la única parte del frontend que sabe hablar con el backend.
 *
 * Concentrar aquí todas las llamadas `fetch` es un buen patrón: los componentes
 * solo llaman a estas funciones y no se preocupan por URLs ni por cómo se hace
 * la petición. Si mañana cambia la URL base, se toca un solo lugar.
 */

import type { Course, CourseCreate, CourseUpdate } from "./types";

// Dónde vive la API. Al desplegar, esto vendría de una variable de entorno.
const BASE_URL = "http://127.0.0.1:8000";

/**
 * Envoltura sobre fetch que centraliza el manejo de errores.
 *
 * fetch NO lanza error cuando el servidor responde 404 o 500 (solo si la red
 * falla). Por eso revisamos `response.ok` a mano y lanzamos si algo salió mal,
 * para que quien llame pueda hacer try/catch en un solo sitio.
 */
async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });

  if (!response.ok) {
    throw new Error(`La API respondió ${response.status} en ${path}`);
  }

  // 204 No Content (p.ej. al borrar) no trae cuerpo: no intentamos parsear JSON.
  if (response.status === 204) {
    return undefined as T;
  }

  return response.json() as Promise<T>;
}

// --- Funciones concretas, una por operación del CRUD ---

// GET /courses -> lista de cursos
export function listCourses(): Promise<Course[]> {
  return request<Course[]>("/courses");
}

// POST /courses -> crea y devuelve el curso creado
export function createCourse(data: CourseCreate): Promise<Course> {
  return request<Course>("/courses", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

// PATCH /courses/{id} -> actualiza parcialmente y devuelve el curso
export function updateCourse(id: number, data: CourseUpdate): Promise<Course> {
  return request<Course>(`/courses/${id}`, {
    method: "PATCH",
    body: JSON.stringify(data),
  });
}

// DELETE /courses/{id} -> borra (no devuelve cuerpo)
export function deleteCourse(id: number): Promise<void> {
  return request<void>(`/courses/${id}`, { method: "DELETE" });
}
