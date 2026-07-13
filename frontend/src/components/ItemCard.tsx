/**
 * Tarjeta que muestra UN item y permite editarlo rápido.
 *
 * Desde aquí puedes cambiar el estado, ajustar el progreso y borrar el item.
 * La tarjeta no habla con la API directamente: avisa a su padre (App) mediante
 * las funciones que recibe por props. Así App es el "dueño" de los datos y la
 * tarjeta solo se encarga de mostrarlos. Este patrón se llama "lifting state up".
 */
import type { Item, ItemStatus, ItemUpdate } from "../types";
import { KIND_LABEL, PRIORITY_LABEL, STATUS_LABEL } from "./ItemForm";

interface ItemCardProps {
  item: Item;
  onUpdate: (id: number, data: ItemUpdate) => Promise<void>;
  onDelete: (id: number) => Promise<void>;
}

/**
 * ¿Está vencida esta fecha límite?
 *
 * `due` viene como "2026-08-30". Comparamos contra el día de HOY en formato
 * ISO: la comparación de strings funciona porque el formato YYYY-MM-DD ordena
 * alfabético = cronológico. Un item hecho nunca se marca vencido.
 */
function isOverdue(item: Item): boolean {
  if (!item.due_date || item.status === "done") return false;
  const today = new Date().toISOString().slice(0, 10); // "2026-07-12"
  return item.due_date < today;
}

export default function ItemCard({ item, onUpdate, onDelete }: ItemCardProps) {
  const overdue = isOverdue(item);

  return (
    <div className="card">
      <div className="item-head">
        <div className="item-title">
          {/* Si el item tiene link, el título es clickeable; si no, es texto plano. */}
          {item.url ? (
            <a href={item.url} target="_blank" rel="noreferrer">
              {item.title}
            </a>
          ) : (
            item.title
          )}
        </div>
        {/* Las clases de los badges cambian según el valor -> color por CSS. */}
        <div className="badges">
          <span className={`badge kind-${item.kind}`}>{KIND_LABEL[item.kind]}</span>
          <span className={`badge prio-${item.priority}`}>{PRIORITY_LABEL[item.priority]}</span>
          <span className={`badge ${item.status}`}>{STATUS_LABEL[item.status]}</span>
        </div>
      </div>

      <div className="muted">
        {item.platform && <span>{item.platform}</span>}
        {item.platform && item.due_date && <span> · </span>}
        {item.due_date && (
          <span className={overdue ? "overdue" : ""}>
            {overdue ? "⚠️ Venció el " : "Para el "}
            {item.due_date}
          </span>
        )}
      </div>

      {/* Barra de progreso: el ancho del relleno es el porcentaje. */}
      <div className="progress-track">
        <div className="progress-fill" style={{ width: `${item.progress}%` }} />
      </div>
      <div className="muted" style={{ marginTop: 4 }}>
        {item.progress}% completado
      </div>

      <div className="actions">
        {/* Cambiar estado: al elegir otra opción, se hace PATCH inmediatamente. */}
        <select
          value={item.status}
          onChange={(e) => onUpdate(item.id, { status: e.target.value as ItemStatus })}
        >
          {Object.entries(STATUS_LABEL).map(([value, label]) => (
            <option key={value} value={value}>
              {label}
            </option>
          ))}
        </select>

        {/* Ajustar progreso con un deslizador de 0 a 100. */}
        <input
          type="range"
          min={0}
          max={100}
          value={item.progress}
          onChange={(e) => onUpdate(item.id, { progress: Number(e.target.value) })}
          style={{ flex: 1, minWidth: 120 }}
        />

        <button className="btn-danger" onClick={() => onDelete(item.id)}>
          Borrar
        </button>
      </div>
    </div>
  );
}
