export interface SavedPoint {
  id: number;
  user_id: number;
  name: string;
  lat: number;
  lon: number;
  description?: string | null;
  created_at: string;
}

export interface SavedPointCreate {
  name: string;
  lat: number;
  lon: number;
  description?: string | null;
}

export type SavedPointUpdate = Partial<SavedPointCreate>;
