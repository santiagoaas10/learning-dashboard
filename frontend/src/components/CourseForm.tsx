/**
 * Formulario para crear un curso nuevo.
 *
 * Este es un componente "controlado": cada campo del formulario está atado a una
 * variable de estado de React (useState). Lo que se ve en el input SIEMPRE
 * refleja el estado, y al escribir actualizamos ese estado. Es el patrón
 * estándar de formularios en React.
 */
import { useState } from "react";

import type { CourseCreate, CourseStatus } from "../types";

// `props`: los datos/funciones que este componente recibe de su padre (App).
// Aquí recibe una sola cosa: qué hacer cuando se envía el formulario.
interface CourseFormProps {
  onCreate: (data: CourseCreate) => Promise<void>;
}

export default function CourseForm({ onCreate }: CourseFormProps) {
  // Un estado por cada campo editable del formulario.
  const [title, setTitle] = useState("");
  const [url, setUrl] = useState("");
  const [platform, setPlatform] = useState("");
  const [status, setStatus] = useState<CourseStatus>("todo");
  const [saving, setSaving] = useState(false); // para deshabilitar el botón mientras guarda

  // Se ejecuta al enviar el formulario.
  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault(); // evita que el navegador recargue la página (comportamiento por defecto)
    if (!title.trim()) return; // no creamos cursos sin título

    setSaving(true);
    try {
      // Mandamos solo lo que tiene valor; los vacíos van como null.
      await onCreate({
        title: title.trim(),
        url: url.trim() || null,
        platform: platform.trim() || null,
        status,
      });
      // Limpiamos el formulario para el siguiente curso.
      setTitle("");
      setUrl("");
      setPlatform("");
      setStatus("todo");
    } finally {
      setSaving(false); // pase lo que pase, reactivamos el botón
    }
  }

  return (
    <form className="card" onSubmit={handleSubmit}>
      <div style={{ marginBottom: 12 }}>
        <label htmlFor="title">Título del curso *</label>
        <input
          id="title"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="Ej: Neetcode - Estructuras de datos"
        />
      </div>

      <div className="row" style={{ marginBottom: 12 }}>
        <div>
          <label htmlFor="url">Link (opcional)</label>
          <input
            id="url"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="https://..."
          />
        </div>
        <div>
          <label htmlFor="platform">Plataforma (opcional)</label>
          <input
            id="platform"
            value={platform}
            onChange={(e) => setPlatform(e.target.value)}
            placeholder="Udemy, YouTube..."
          />
        </div>
        <div>
          <label htmlFor="status">Estado</label>
          <select
            id="status"
            value={status}
            onChange={(e) => setStatus(e.target.value as CourseStatus)}
          >
            <option value="todo">Por hacer</option>
            <option value="in_progress">En curso</option>
            <option value="done">Hecho</option>
          </select>
        </div>
      </div>

      <button type="submit" className="btn-primary" disabled={saving}>
        {saving ? "Guardando..." : "Agregar curso"}
      </button>
    </form>
  );
}
