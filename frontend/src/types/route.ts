export interface RoutePlanRequest {
  drone_id: number;
  start_lat: number;
  start_lon: number;
  end_lat: number;
  end_lon: number;
  departure_time: string;
  grid_size: number;
  corridor_width_km: number;
}

export interface RouteWaypoint {
  lat: number;
  lon: number;
  weather_risk: number;
}

export interface WeatherSummary {
  max_wind_speed_ms: number;
  max_gust_ms: number;
  max_precipitation_mm: number;
}

export interface RoutePlanResponse {
  status: string;
  route_request_id: number;
  route_result_id: number;
  total_distance_km?: number | null;
  effective_distance_km?: number | null;
  risk_score?: number | null;
  weather_summary?: WeatherSummary | null;
  route: RouteWaypoint[];
  reason?: string | null;
  explanation: string[];
}

export interface MapPoint {
  lat: number;
  lon: number;
}

export type MapMode = "start" | "end" | "weather" | "save";
