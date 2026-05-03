import type { Drone } from "../types/drone";
import type { MapMode, MapPoint } from "../types/route";
import type { WeatherPoint } from "../types/weather";

interface RoutePlannerPanelProps {
  selectedDrone: Drone | null;
  startPoint: MapPoint | null;
  endPoint: MapPoint | null;
  startWeather: WeatherPoint | null;
  endWeather: WeatherPoint | null;
  mapMode: MapMode;
  departureTime: string;
  gridSize: number;
  corridorWidthKm: number;
  isPlanning: boolean;
  onMapModeChange: (mode: MapMode) => void;
  onDepartureTimeChange: (value: string) => void;
  onGridSizeChange: (value: number) => void;
  onCorridorWidthChange: (value: number) => void;
  onPlanRoute: () => void;
}

function pointLabel(point: MapPoint | null): string {
  if (!point) {
    return "не выбрана";
  }
  return `${point.lat.toFixed(5)}, ${point.lon.toFixed(5)}`;
}

function weatherLine(weather: WeatherPoint | null): string {
  if (!weather) {
    return "Погода не загружена";
  }
  const temperature =
    weather.temperature_c === null || weather.temperature_c === undefined
      ? "темп. нет данных"
      : `темп. ${weather.temperature_c} °C`;
  const humidity =
    weather.relative_humidity_percent === null ||
    weather.relative_humidity_percent === undefined
      ? "влажн. нет данных"
      : `влажн. ${weather.relative_humidity_percent} %`;
  const cloudCover =
    weather.cloud_cover_percent === null || weather.cloud_cover_percent === undefined
      ? "облачн. нет данных"
      : `облачн. ${weather.cloud_cover_percent} %`;

  return `ветер ${weather.wind_speed_ms} м/с, порывы ${weather.wind_gust_ms} м/с, осадки ${weather.precipitation_mm} мм, ${temperature}, ${humidity}, ${cloudCover}, code ${weather.weather_code ?? "нет"}`;
}

export default function RoutePlannerPanel({
  selectedDrone,
  startPoint,
  endPoint,
  startWeather,
  endWeather,
  mapMode,
  departureTime,
  gridSize,
  corridorWidthKm,
  isPlanning,
  onMapModeChange,
  onDepartureTimeChange,
  onGridSizeChange,
  onCorridorWidthChange,
  onPlanRoute,
}: RoutePlannerPanelProps) {
  const canPlan = Boolean(selectedDrone && startPoint && endPoint && !isPlanning);

  return (
    <section className="panel">
      <div className="panel-header">
        <h2>Планировщик</h2>
      </div>

      <div className="mode-grid">
        {(["start", "end", "weather", "save"] as MapMode[]).map((mode) => (
          <button
            className={mapMode === mode ? "active" : ""}
            type="button"
            key={mode}
            onClick={() => onMapModeChange(mode)}
          >
            {mode === "start" && "Старт"}
            {mode === "end" && "Финиш"}
            {mode === "weather" && "Погода"}
            {mode === "save" && "Сохранить"}
          </button>
        ))}
      </div>

      <div className="summary-card">
        <strong>Активный дрон</strong>
        <span>{selectedDrone ? selectedDrone.name : "не выбран"}</span>
      </div>

      <div className="point-card">
        <strong>Старт</strong>
        <span>{pointLabel(startPoint)}</span>
        <small>{weatherLine(startWeather)}</small>
        <button type="button" onClick={() => onMapModeChange("start")}>
          Выбрать на карте
        </button>
      </div>

      <div className="point-card">
        <strong>Финиш</strong>
        <span>{pointLabel(endPoint)}</span>
        <small>{weatherLine(endWeather)}</small>
        <button type="button" onClick={() => onMapModeChange("end")}>
          Выбрать на карте
        </button>
      </div>

      <div className="form-grid">
        <label>
          Время вылета
          <input
            type="datetime-local"
            value={departureTime}
            onChange={(event) => onDepartureTimeChange(event.target.value)}
          />
        </label>
        <label>
          Размер сетки
          <input
            type="number"
            min="5"
            max="30"
            value={gridSize}
            onChange={(event) => onGridSizeChange(Number(event.target.value))}
          />
        </label>
        <label>
          Коридор, км
          <input
            type="number"
            min="1"
            max="100"
            value={corridorWidthKm}
            onChange={(event) => onCorridorWidthChange(Number(event.target.value))}
          />
        </label>
      </div>

      <button
        className="button primary full-width"
        type="button"
        onClick={onPlanRoute}
        disabled={!canPlan}
      >
        {isPlanning ? "Строим маршрут..." : "Построить маршрут"}
      </button>
    </section>
  );
}
