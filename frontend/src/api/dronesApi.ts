import { apiRequest } from "./client";
import type { Drone, DroneCreate, DroneUpdate } from "../types/drone";

export function getDrones(): Promise<Drone[]> {
  return apiRequest<Drone[]>("/drones");
}

export function createDrone(data: DroneCreate): Promise<Drone> {
  return apiRequest<Drone>("/drones", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export function updateDrone(id: number, data: DroneUpdate): Promise<Drone> {
  return apiRequest<Drone>(`/drones/${id}`, {
    method: "PATCH",
    body: JSON.stringify(data),
  });
}

export function deleteDrone(id: number): Promise<void> {
  return apiRequest<void>(`/drones/${id}`, {
    method: "DELETE",
  });
}
