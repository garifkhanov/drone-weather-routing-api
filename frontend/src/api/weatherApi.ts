import { apiRequest } from "./client";
import type { WeatherPoint } from "../types/weather";

export function getWeatherPoint(
  lat: number,
  lon: number,
  forecastTime?: string,
): Promise<WeatherPoint> {
  const params = new URLSearchParams({
    lat: String(lat),
    lon: String(lon),
  });

  if (forecastTime) {
    params.set("forecast_time", forecastTime);
  }

  return apiRequest<WeatherPoint>(`/weather/point?${params.toString()}`);
}
