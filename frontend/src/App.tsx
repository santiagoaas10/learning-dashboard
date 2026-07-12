/**
 * Componente raíz de la app.
 *
 * App es el "cerebro": guarda la lista de cursos en estado, la carga desde la
 * API al iniciar, y define qué pasa al crear/editar/borrar. Los componentes
 * hijos (CourseForm, CourseCard) solo muestran datos y avisan a App.
 *
 * Idea clave de React: cuando el estado cambia (setCourses), React vuelve a
 * pintar la interfaz automáticamente para reflejarlo. No tocamos el HTML a mano.
 */
import { useEffect, useState } from "react";

import * as api from "./api";
import CourseCard from "./components/CourseCard";
import CourseForm from "./components/CourseForm";
import type { Course, CourseCreate, CourseUpdate } from "./types";

export default function App() {
  // Estado principal: la lista de cursos que se muestra en pantalla.
  const [courses, setCourses] = useState<Course[]>([]);
  const [loading, setLoading] = useState(true); // true mientras carga la primera vez
  const [error, setError] = useState<string | null>(null); // mensaje si algo falla

  // useEffect con [] corre UNA vez, justo después del primer render. Es el lugar
  // típico para "cargar datos al abrir la página".
  useEffect(() => {
    api
      .listCourses()
      .then(setCourses) // si sale bien, guardamos los cursos
      .catch((e: Error) => setError(e.message)) // si falla, mostramos el error
      .finally(() => setLoading(false)); // en ambos casos, dejamos de "cargar"
  }, []);

  // Crear: llama a la API y agrega el curso devuelto al final de la lista.
  async function handleCreate(data: CourseCreate) {
    const created = await api.createCourse(data);
    setCourses((prev) => [...prev, created]); // copia la lista y añade el nuevo
  }

  // Actualizar: pide el PATCH y reemplaza ese curso por la versión actualizada.
  async function handleUpdate(id: number, data: CourseUpdate) {
    const updated = await api.updateCourse(id, data);
    setCourses((prev) => prev.map((c) => (c.id === id ? updated : c)));
  }

  // Borrar: pide el DELETE y saca ese curso de la lista.
  async function handleDelete(id: number) {
    await api.deleteCourse(id);
    setCourses((prev) => prev.filter((c) => c.id !== id));
  }

  return (
    <div className="container">
      <h1>Learning Dashboard</h1>
      <p className="subtitle">Los cursos que quiero hacer, en un solo lugar.</p>

      <CourseForm onCreate={handleCreate} />

      {/* Renderizado condicional: mostramos un mensaje según el estado. */}
      {loading && <div className="state-msg">Cargando cursos...</div>}
      {error && <div className="state-msg">Error: {error}</div>}
      {!loading && !error && courses.length === 0 && (
        <div className="state-msg">Aún no hay cursos. ¡Agrega el primero arriba!</div>
      )}

      {/* La lista: por cada curso pintamos una tarjeta.
          `key` ayuda a React a identificar cada elemento de forma eficiente. */}
      {courses.map((course) => (
        <CourseCard
          key={course.id}
          course={course}
          onUpdate={handleUpdate}
          onDelete={handleDelete}
        />
      ))}
    </div>
  );
}
