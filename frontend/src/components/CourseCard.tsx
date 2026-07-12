/**
 * Tarjeta que muestra UN curso y permite editarlo rápido.
 *
 * Desde aquí puedes cambiar el estado, ajustar el progreso y borrar el curso.
 * La tarjeta no habla con la API directamente: avisa a su padre (App) mediante
 * las funciones que recibe por props. Así App es el "dueño" de los datos y la
 * tarjeta solo se encarga de mostrarlos. Este patrón se llama "lifting state up".
 */
import type { Course, CourseStatus, CourseUpdate } from "../types";

interface CourseCardProps {
  course: Course;
  onUpdate: (id: number, data: CourseUpdate) => Promise<void>;
  onDelete: (id: number) => Promise<void>;
}

// Texto legible en español para cada estado (el valor interno queda en inglés).
const STATUS_LABEL: Record<CourseStatus, string> = {
  todo: "Por hacer",
  in_progress: "En curso",
  done: "Hecho",
};

export default function CourseCard({ course, onUpdate, onDelete }: CourseCardProps) {
  return (
    <div className="card">
      <div className="course-head">
        <div className="course-title">
          {/* Si el curso tiene link, el título es clickeable; si no, es texto plano. */}
          {course.url ? (
            <a href={course.url} target="_blank" rel="noreferrer">
              {course.title}
            </a>
          ) : (
            course.title
          )}
        </div>
        {/* La clase del badge cambia según el estado -> color distinto por CSS. */}
        <span className={`badge ${course.status}`}>{STATUS_LABEL[course.status]}</span>
      </div>

      {course.platform && <div className="muted">{course.platform}</div>}

      {/* Barra de progreso: el ancho del relleno es el porcentaje. */}
      <div className="progress-track">
        <div className="progress-fill" style={{ width: `${course.progress}%` }} />
      </div>
      <div className="muted" style={{ marginTop: 4 }}>
        {course.progress}% completado
      </div>

      <div className="actions">
        {/* Cambiar estado: al elegir otra opción, se hace PATCH inmediatamente. */}
        <select
          value={course.status}
          onChange={(e) => onUpdate(course.id, { status: e.target.value as CourseStatus })}
        >
          <option value="todo">Por hacer</option>
          <option value="in_progress">En curso</option>
          <option value="done">Hecho</option>
        </select>

        {/* Ajustar progreso con un deslizador de 0 a 100. */}
        <input
          type="range"
          min={0}
          max={100}
          value={course.progress}
          onChange={(e) => onUpdate(course.id, { progress: Number(e.target.value) })}
          style={{ flex: 1, minWidth: 120 }}
        />

        <button className="btn-danger" onClick={() => onDelete(course.id)}>
          Borrar
        </button>
      </div>
    </div>
  );
}
