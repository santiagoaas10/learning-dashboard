/**
 * El tablero kanban: 4 columnas (una por estado) con drag & drop.
 *
 * Usamos el drag & drop NATIVO de HTML5 (sin librerías) para ver el mecanismo
 * por dentro. Son tres piezas que conversan:
 *
 * 1. La tarjeta es `draggable` y en onDragStart guarda su id en
 *    `dataTransfer` (un "sobre" de datos que viaja con el arrastre).
 * 2. La columna hace `preventDefault()` en onDragOver: por defecto el
 *    navegador NO permite soltar en ningún lado; prevenirlo dice "aquí sí".
 * 3. En onDrop la columna abre el sobre, lee el id y pide el PATCH de status.
 *
 * Limitación conocida: el DnD nativo no funciona con dedo en móvil. Por eso
 * cada tarjeta conserva su <select> de estado como alternativa.
 */
import { useState } from "react";

import type { Item, ItemStatus, ItemUpdate } from "../types";
import ItemCard from "./ItemCard";
import { STATUS_LABEL } from "./ItemForm";

// El orden de las columnas en pantalla, de "idea" a "terminado".
const COLUMNS: ItemStatus[] = ["backlog", "todo", "in_progress", "done"];

interface BoardProps {
  items: Item[];
  onUpdate: (id: number, data: ItemUpdate) => Promise<void>;
  onDelete: (id: number) => Promise<void>;
}

export default function Board({ items, onUpdate, onDelete }: BoardProps) {
  // Sobre qué columna está pasando el arrastre AHORA (para resaltarla).
  const [dragOverCol, setDragOverCol] = useState<ItemStatus | null>(null);

  function handleDrop(event: React.DragEvent, column: ItemStatus) {
    event.preventDefault();
    setDragOverCol(null);

    // Abrimos el "sobre": la tarjeta guardó aquí su id al empezar el arrastre.
    const id = Number(event.dataTransfer.getData("text/plain"));
    if (!id) return; // arrastraron algo que no es una tarjeta nuestra

    // Si ya está en esa columna no hay nada que hacer (nos ahorramos el PATCH).
    const item = items.find((it) => it.id === id);
    if (!item || item.status === column) return;

    void onUpdate(id, { status: column });
  }

  return (
    <div className="board">
      {COLUMNS.map((column) => {
        const columnItems = items.filter((it) => it.status === column);

        return (
          <section
            key={column}
            // La clase extra resalta la columna mientras arrastras encima.
            className={`column ${dragOverCol === column ? "drag-over" : ""}`}
            onDragOver={(e) => {
              e.preventDefault(); // sin esto, soltar aquí está prohibido
              setDragOverCol(column);
            }}
            onDragLeave={() => setDragOverCol(null)}
            onDrop={(e) => handleDrop(e, column)}
          >
            <h3 className="column-title">
              {STATUS_LABEL[column]}
              {/* Cuántas tarjetas hay en la columna, como en JIRA. */}
              <span className="column-count">{columnItems.length}</span>
            </h3>

            {columnItems.map((item) => (
              <ItemCard key={item.id} item={item} onUpdate={onUpdate} onDelete={onDelete} />
            ))}

            {columnItems.length === 0 && <div className="column-empty">Suelta tarjetas aquí</div>}
          </section>
        );
      })}
    </div>
  );
}
