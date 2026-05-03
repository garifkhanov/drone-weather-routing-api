import { FormEvent, useEffect, useState } from "react";
import { createDrone, deleteDrone, updateDrone } from "../api/dronesApi";
import { ApiError } from "../api/client";
import type { Drone, DroneCreate } from "../types/drone";

interface DronePanelProps {
  drones: Drone[];
  selectedDroneId: number | null;
  onDronesChange: (drones: Drone[]) => void;
  onSelectDrone: (droneId: number | null) => void;
}

const emptyDroneForm: DroneCreate = {
  name: "Test Drone",
  max_range_km: 100,
  max_wind_speed_ms: 10,
  max_gust_ms: 15,
  max_precipitation_mm: 0.5,
  cruise_speed_kmh: 50,
};

function getErrorMessage(error: unknown): string {
  if (error instanceof ApiError || error instanceof Error) {
    return error.message;
  }
  return "Не удалось сохранить профиль дрона";
}

export default function DronePanel({
  drones,
  selectedDroneId,
  onDronesChange,
  onSelectDrone,
}: DronePanelProps) {
  const [form, setForm] = useState<DroneCreate>(emptyDroneForm);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!selectedDroneId && drones.length > 0) {
      onSelectDrone(drones[0].id);
    }
  }, [drones, onSelectDrone, selectedDroneId]);

  function updateForm(field: keyof DroneCreate, value: string) {
    setForm((current) => ({
      ...current,
      [field]: field === "name" ? value : Number(value),
    }));
  }

  function startEdit(drone: Drone) {
    setEditingId(drone.id);
    setForm({
      name: drone.name,
      max_range_km: drone.max_range_km,
      max_wind_speed_ms: drone.max_wind_speed_ms,
      max_gust_ms: drone.max_gust_ms,
      max_precipitation_mm: drone.max_precipitation_mm,
      cruise_speed_kmh: drone.cruise_speed_kmh,
    });
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setIsSaving(true);
    setError(null);

    try {
      if (editingId) {
        const updatedDrone = await updateDrone(editingId, form);
        onDronesChange(
          drones.map((drone) => (drone.id === editingId ? updatedDrone : drone)),
        );
      } else {
        const createdDrone = await createDrone(form);
        onDronesChange([...drones, createdDrone]);
        onSelectDrone(createdDrone.id);
      }
      setEditingId(null);
      setForm(emptyDroneForm);
    } catch (saveError) {
      setError(getErrorMessage(saveError));
    } finally {
      setIsSaving(false);
    }
  }

  async function handleDelete(droneId: number) {
    setError(null);
    try {
      await deleteDrone(droneId);
      const nextDrones = drones.filter((drone) => drone.id !== droneId);
      onDronesChange(nextDrones);
      if (selectedDroneId === droneId) {
        onSelectDrone(nextDrones[0]?.id ?? null);
      }
    } catch (deleteError) {
      setError(getErrorMessage(deleteError));
    }
  }

  return (
    <section className="panel">
      <div className="panel-header">
        <h2>Дроны</h2>
        <span>{drones.length}</span>
      </div>

      {drones.length === 0 ? (
        <p className="empty-state">Профилей пока нет. Создайте первый дрон.</p>
      ) : (
        <div className="list">
          {drones.map((drone) => (
            <article
              className={
                selectedDroneId === drone.id ? "list-item selected" : "list-item"
              }
              key={drone.id}
            >
              <button
                className="text-button"
                type="button"
                onClick={() => onSelectDrone(drone.id)}
              >
                <strong>{drone.name}</strong>
                <span>{drone.max_range_km} км, ветер до {drone.max_wind_speed_ms} м/с</span>
              </button>
              <div className="row-actions">
                <button type="button" onClick={() => startEdit(drone)}>
                  Редактировать
                </button>
                <button type="button" onClick={() => handleDelete(drone.id)}>
                  Удалить
                </button>
              </div>
            </article>
          ))}
        </div>
      )}

      <form className="stack" onSubmit={handleSubmit}>
        <h3>{editingId ? "Редактировать дрон" : "Новый дрон"}</h3>
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
            Дальность, км
            <input
              type="number"
              min="1"
              step="0.1"
              value={form.max_range_km}
              onChange={(event) => updateForm("max_range_km", event.target.value)}
              required
            />
          </label>
          <label>
            Ветер, м/с
            <input
              type="number"
              min="0.1"
              step="0.1"
              value={form.max_wind_speed_ms}
              onChange={(event) => updateForm("max_wind_speed_ms", event.target.value)}
              required
            />
          </label>
          <label>
            Порывы, м/с
            <input
              type="number"
              min="0.1"
              step="0.1"
              value={form.max_gust_ms}
              onChange={(event) => updateForm("max_gust_ms", event.target.value)}
              required
            />
          </label>
          <label>
            Осадки, мм
            <input
              type="number"
              min="0"
              step="0.1"
              value={form.max_precipitation_mm}
              onChange={(event) =>
                updateForm("max_precipitation_mm", event.target.value)
              }
              required
            />
          </label>
          <label>
            Скорость, км/ч
            <input
              type="number"
              min="1"
              step="0.1"
              value={form.cruise_speed_kmh}
              onChange={(event) => updateForm("cruise_speed_kmh", event.target.value)}
              required
            />
          </label>
        </div>
        {error && <p className="error-text">{error}</p>}
        <div className="button-row">
          <button className="button primary" type="submit" disabled={isSaving}>
            {isSaving ? "Сохранение..." : editingId ? "Сохранить" : "Добавить"}
          </button>
          {editingId && (
            <button
              className="button secondary"
              type="button"
              onClick={() => {
                setEditingId(null);
                setForm(emptyDroneForm);
              }}
            >
              Отмена
            </button>
          )}
        </div>
      </form>
    </section>
  );
}
