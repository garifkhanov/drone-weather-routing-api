import type { RoutePlanResponse } from "../types/route";

interface RouteResultPanelProps {
  result: RoutePlanResponse | null;
}

function formatMetric(value: number | null | undefined, suffix = ""): string {
  if (value === null || value === undefined) {
    return "нет данных";
  }
  return `${value.toFixed(2)}${suffix}`;
}

export default function RouteResultPanel({ result }: RouteResultPanelProps) {
  if (!result) {
    return (
      <section className="panel compact">
        <div className="panel-header">
          <h2>Результат маршрута</h2>
        </div>
        <p className="empty-state">Маршрут ещё не построен.</p>
      </section>
    );
  }

  const riskClass =
    (result.risk_score ?? 0) < 0.35
      ? "risk low"
      : (result.risk_score ?? 0) < 0.7
        ? "risk medium"
        : "risk high";

  return (
    <section className="panel compact">
      <div className="panel-header">
        <h2>Результат маршрута</h2>
        <span className={riskClass}>{result.status}</span>
      </div>

      {result.reason && <p className="error-text">{result.reason}</p>}

      <dl className="metric-list">
        <div>
          <dt>Общая длина</dt>
          <dd>{formatMetric(result.total_distance_km, " км")}</dd>
        </div>
        <div>
          <dt>Эффективная длина</dt>
          <dd>{formatMetric(result.effective_distance_km, " км")}</dd>
        </div>
        <div>
          <dt>Risk score</dt>
          <dd>{formatMetric(result.risk_score)}</dd>
        </div>
        {result.weather_summary && (
          <>
            <div>
              <dt>Макс. ветер</dt>
              <dd>{result.weather_summary.max_wind_speed_ms.toFixed(2)} м/с</dd>
            </div>
            <div>
              <dt>Макс. порывы</dt>
              <dd>{result.weather_summary.max_gust_ms.toFixed(2)} м/с</dd>
            </div>
            <div>
              <dt>Макс. осадки</dt>
              <dd>{result.weather_summary.max_precipitation_mm.toFixed(2)} мм</dd>
            </div>
          </>
        )}
      </dl>

      {result.explanation.length > 0 && (
        <ul className="plain-list">
          {result.explanation.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
      )}
    </section>
  );
}
