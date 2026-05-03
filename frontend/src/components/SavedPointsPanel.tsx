import { FormEvent, useEffect, useState } from "react";
import { ApiError } from "../api/client";
import type { MapPoint } from "../types/route";
import type {
  SavedPoint,
  SavedPointCreate,
  SavedPointUpdate,
} from "../types/savedPoint";

interface SavedPointsPanelProps {
  savedPoints: SavedPoint[];
  startPoint: MapPoint | null;
  endPoint: MapPoint | null;
  draftPoint: MapPoint | null;
  onCreate: (data: SavedPointCreate) => Promise<void>;
  onUpdate: (id: number, data: SavedPointUpdate) => Promise<void>;
  onDelete: (id: number) => Promise<void>;
  onUseAsStart: (point: MapPoint) => void;
  onUseAsEnd: (point: MapPoint) => void;
  onPickOnMap: () => void;
}

interface SavedPointForm {
  name: string;
  description: string;
  lat: string;
  lon: string;
}

const emptyForm: SavedPointForm = {
  name: "Новая точка",
  description: "",
  lat: "",
  lon: "",
};

function getErrorMessage(error: unknown): string {
  if (error instanceof ApiError || error instanceof Error) {
    return error.message;
  }
  return "Не удалось сохранить точку";
}

function formFromPoint(point: MapPoint, name = "Новая точка"): SavedPointForm {
  return {
    name,
    description: "",
    lat: point.lat.toFixed(6),
    lon: point.lon.toFixed(6),
  };
}

export default function SavedPointsPanel({
  savedPoints,
  startPoint,
  endPoint,
  draftPoint,
  onCreate,
  onUpdate,
  onDelete,
  onUseAsStart,
  onUseAsEnd,
  onPickOnMap,
}: SavedPointsPanelProps) {
  const [form, setForm] = useState<SavedPointForm>(emptyForm);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [editName, setEditName] = useState("");
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (draftPoint) {
      setForm(formFromPoint(draftPoint));
      setEditingId(null);
    }
  }, [draftPoint]);

  function updateForm(field: keyof SavedPointForm, value: string) {
    setForm((current) => ({ ...current, [field]: value }));
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setIsSaving(true);
    setError(null);

    try {
      await onCreate({
        name: form.name,
        lat: Number(form.lat),
        lon: Number(form.lon),
        description: form.description || null,
      });
      setForm(emptyForm);
    } catch (submitError) {
      setError(getErrorMessage(submitError));
    } finally {
      setIsSaving(false);
    }
  }

  async function handleRename(point: SavedPoint) {
    setError(null);
    try {
      await onUpdate(point.id, { name: editName });
      setEditingId(null);
      setEditName("");
    } catch (renameError) {
      setError(getErrorMessage(renameError));
    }
  }

  async function handleDelete(id: number) {
    setError(null);
    try {
      await onDelete(id);
    } catch (deleteError) {
      setError(getErrorMessage(deleteError));
    }
  }

  return (
    <section className="panel">
      <div className="panel-header">
        <h2>Сохранённые точки</h2>
        <span>{savedPoints.length}</span>
      </div>

      <div className="button-row wrap">
        <button
          type="button"
          onClick={() => startPoint && setForm(formFromPoint(startPoint, "Старт"))}
          disabled={!startPoint}
        >
          Взять старт
        </button>
        <button
          type="button"
          onClick={() => endPoint && setForm(formFromPoint(endPoint, "Финиш"))}
          disabled={!endPoint}
        >
          Взять финиш
        </button>
        <button type="button" onClick={onPickOnMap}>
          Клик на карте
        </button>
      </div>

      <form className="stack" onSubmit={handleSubmit}>
        <label>
          Название
          <input
            value={form.name}
            onChange={(event) => updateForm("name", event.target.value)}
            required
          />
        </label>
        <div className="form-grid">
          <label>
            Latitude
            <input
              type="number"
              step="0.000001"
              value={form.lat}
              onChange={(event) => updateForm("lat", event.target.value)}
              required
            />
          </label>
          <label>
            Longitude
            <input
              type="number"
              step="0.000001"
              value={form.lon}
              onChange={(event) => updateForm("lon", event.target.value)}
              required
            />
          </label>
        </div>
        <label>
          Описание
          <input
            value={form.description}
            onChange={(event) => updateForm("description", event.target.value)}
          />
        </label>
        {error && <p className="error-text">{error}</p>}
        <button className="button secondary" type="submit" disabled={isSaving}>
          {isSaving ? "Сохранение..." : "Сохранить точку"}
        </button>
      </form>

      {savedPoints.length === 0 ? (
        <p className="empty-state">Список точек пуст.</p>
      ) : (
        <div className="list">
          {savedPoints.map((point) => (
            <article className="list-item" key={point.id}>
              {editingId === point.id ? (
                <div className="inline-edit">
                  <input
                    value={editName}
                    onChange={(event) => setEditName(event.target.value)}
                  />
                  <button type="button" onClick={() => handleRename(point)}>
                    OK
                  </button>
                </div>
              ) : (
                <>
                  <strong>{point.name}</strong>
                  <span>{point.lat.toFixed(5)}, {point.lon.toFixed(5)}</span>
                  {point.description && <small>{point.description}</small>}
                </>
              )}
              <div className="row-actions">
                <button
                  type="button"
                  onClick={() => onUseAsStart({ lat: point.lat, lon: point.lon })}
                >
                  Старт
                </button>
                <button
                  type="button"
                  onClick={() => onUseAsEnd({ lat: point.lat, lon: point.lon })}
                >
                  Финиш
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setEditingId(point.id);
                    setEditName(point.name);
                  }}
                >
                  Имя
                </button>
                <button type="button" onClick={() => handleDelete(point.id)}>
                  Удалить
                </button>
              </div>
            </article>
          ))}
        </div>
      )}
    </section>
  );
}
