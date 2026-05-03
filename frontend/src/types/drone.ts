export interface Drone {
  id: number;
  owner_id: number;
  name: string;
  max_range_km: number;
  max_wind_speed_ms: number;
  max_gust_ms: number;
  max_precipitation_mm: number;
  cruise_speed_kmh: number;
  created_at: string;
}

export interface DroneCreate {
  name: string;
  max_range_km: number;
  max_wind_speed_ms: number;
  max_gust_ms: number;
  max_precipitation_mm: number;
  cruise_speed_kmh: number;
}

export type DroneUpdate = Partial<DroneCreate>;
