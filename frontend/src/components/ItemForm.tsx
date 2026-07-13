/**
 * Formulario para crear un item nuevo (curso, proyecto, video o habilidad).
 *
 * Este es un componente "controlado": cada campo del formulario está atado a una
 * variable de estado de React (useState). Lo que se ve en el input SIEMPRE
 * refleja el estado, y al escribir actualizamos ese estado. Es el patrón
 * estándar de formularios en React.
 */
import { useState } from "react";

import type { ItemCreate, ItemKind, ItemPriority, ItemStatus } from "../types";

// Etiquetas en español para cada valor interno (que queda en inglés).
// Exportamos las de kind/priority porque las tarjetas también las usan.
export const KIND_LABEL: Record<ItemKind, string> = {
  course: "Curso",
  project: "Proyecto",
  video: "Video",
  skill: "Habilidad",
};

export const PRIORITY_LABEL: Record<ItemPriority, string> = {
  low: "Baja",
  medium: "Media",
  high: "Alta",
  urgent: "Urgente",
};

export const STATUS_LABEL: Record<ItemStatus, string> = {
  backlog: "Backlog",
  todo: "Por hacer",
  in_progress: "En curso",
  done: "Hecho",
};

interface ItemFormProps {
  onCreate: (data: ItemCreate) => Promise<void>;
}

export default function ItemForm({ onCreate }: ItemFormProps) {
  // Un estado por cada campo editable del formulario.
  const [title, setTitle] = useState("");
  const [kind, setKind] = useState<ItemKind>("course");
  const [url, setUrl] = useState("");
  const [platform, setPlatform] = useState("");
  const [priority, setPriority] = useState<ItemPriority>("medium");
  const [dueDate, setDueDate] = useState(""); // el input date da "" o "2026-08-30"
  const [status, setStatus] = useState<ItemStatus>("backlog");
  const [saving, setSaving] = useState(false); // para deshabilitar el botón mientras guarda

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault(); // evita que el navegador recargue la página
    if (!title.trim()) return; // no creamos items sin título

    setSaving(true);
    try {
      // Mandamos solo lo que tiene valor; los vacíos van como null.
      await onCreate({
        title: title.trim(),
        kind,
        url: url.trim() || null,
        platform: platform.trim() || null,
        priority,
        due_date: dueDate || null,
        status,
      });
      // Limpiamos los campos de texto para el siguiente item. Dejamos kind,
      // priority y status como estaban: si estás cargando 5 videos seguidos,
      // no quieres re-elegir "Video" cada vez.
      setTitle("");
      setUrl("");
      setPlatform("");
      setDueDate("");
    } finally {
      setSaving(false); // pase lo que pase, reactivamos el botón
    }
  }

  return (
    <form className="card" onSubmit={handleSubmit}>
      <div className="row" style={{ marginBottom: 12 }}>
        <div style={{ flex: 2 }}>
          <label htmlFor="title">Título *</label>
          <input
            id="title"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="Ej: Neetcode - Estructuras de datos"
          />
        </div>
        <div>
          <label htmlFor="kind">Tipo</label>
          <select id="kind" value={kind} onChange={(e) => setKind(e.target.value as ItemKind)}>
            {/* Generamos las <option> desde el diccionario de etiquetas:
                una sola fuente de verdad en vez de opciones escritas a mano. */}
            {Object.entries(KIND_LABEL).map(([value, label]) => (
              <option key={value} value={value}>
                {label}
              </option>
            ))}
          </select>
        </div>
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
      </div>

      <div className="row" style={{ marginBottom: 12 }}>
        <div>
          <label htmlFor="priority">Prioridad</label>
          <select
            id="priority"
            value={priority}
            onChange={(e) => setPriority(e.target.value as ItemPriority)}
          >
            {Object.entries(PRIORITY_LABEL).map(([value, label]) => (
              <option key={value} value={value}>
                {label}
              </option>
            ))}
          </select>
        </div>
        <div>
          <label htmlFor="due">Fecha límite (opcional)</label>
          <input id="due" type="date" value={dueDate} onChange={(e) => setDueDate(e.target.value)} />
        </div>
        <div>
          <label htmlFor="status">Columna</label>
          <select
            id="status"
            value={status}
            onChange={(e) => setStatus(e.target.value as ItemStatus)}
          >
            {Object.entries(STATUS_LABEL).map(([value, label]) => (
              <option key={value} value={value}>
                {label}
              </option>
            ))}
          </select>
        </div>
      </div>

      <button type="submit" className="btn-primary" disabled={saving}>
        {saving ? "Guardando..." : "Agregar"}
      </button>
    </form>
  );
}
