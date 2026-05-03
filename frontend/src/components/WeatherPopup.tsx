import type { WeatherPoint } from "../types/weather";

interface WeatherPopupProps {
  weather: WeatherPoint | null;
  isLoading?: boolean;
}

function formatValue(value: number | null | undefined, suffix: string): string {
  if (value === null || value === undefined) {
    return "нет данных";
  }
  return `${value}${suffix}`;
}

export default function WeatherPopup({ weather, isLoading = false }: WeatherPopupProps) {
  return (
    <section className="panel compact">
      <div className="panel-header">
        <h2>Погода в точке</h2>
      </div>

      {isLoading && <p className="muted">Загрузка погодных данных...</p>}

      {!isLoading && !weather && (
        <p className="empty-state">Выберите режим “Погода” и кликните по карте.</p>
      )}

      {!isLoading && weather && (
        <dl className="metric-list">
          <div>
            <dt>Координаты</dt>
            <dd>{weather.lat.toFixed(5)}, {weather.lon.toFixed(5)}</dd>
          </div>
          <div>
            <dt>Время прогноза</dt>
            <dd>{new Date(weather.forecast_time).toLocaleString("ru-RU")}</dd>
          </div>
          <div>
            <dt>Температура</dt>
            <dd>{formatValue(weather.temperature_c, " °C")}</dd>
          </div>
          <div>
            <dt>Влажность</dt>
            <dd>{formatValue(weather.relative_humidity_percent, " %")}</dd>
          </div>
          <div>
            <dt>Ветер</dt>
            <dd>{formatValue(weather.wind_speed_ms, " м/с")}</dd>
          </div>
          <div>
            <dt>Порывы</dt>
            <dd>{formatValue(weather.wind_gust_ms, " м/с")}</dd>
          </div>
          <div>
            <dt>Осадки</dt>
            <dd>{formatValue(weather.precipitation_mm, " мм")}</dd>
          </div>
          <div>
            <dt>Облачность</dt>
            <dd>{formatValue(weather.cloud_cover_percent, " %")}</dd>
          </div>
          <div>
            <dt>Weather code</dt>
            <dd>{weather.weather_code ?? "нет данных"}</dd>
          </div>
        </dl>
      )}
    </section>
  );
}
