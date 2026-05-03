export interface WeatherPoint {
  lat: number;
  lon: number;
  forecast_time: string;
  temperature_c?: number | null;
  relative_humidity_percent?: number | null;
  wind_speed_ms: number;
  wind_gust_ms: number;
  precipitation_mm: number;
  cloud_cover_percent?: number | null;
  weather_code?: number | null;
}
