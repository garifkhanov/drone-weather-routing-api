import { apiRequest } from "./client";
import type {
  SavedPoint,
  SavedPointCreate,
  SavedPointUpdate,
} from "../types/savedPoint";

export function getSavedPoints(): Promise<SavedPoint[]> {
  return apiRequest<SavedPoint[]>("/saved-points");
}

export function createSavedPoint(data: SavedPointCreate): Promise<SavedPoint> {
  return apiRequest<SavedPoint>("/saved-points", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export function updateSavedPoint(
  id: number,
  data: SavedPointUpdate,
): Promise<SavedPoint> {
  return apiRequest<SavedPoint>(`/saved-points/${id}`, {
    method: "PATCH",
    body: JSON.stringify(data),
  });
}

export function deleteSavedPoint(id: number): Promise<void> {
  return apiRequest<void>(`/saved-points/${id}`, {
    method: "DELETE",
  });
}
