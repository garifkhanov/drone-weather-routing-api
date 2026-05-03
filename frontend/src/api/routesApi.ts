import { apiRequest } from "./client";
import type { RoutePlanRequest, RoutePlanResponse } from "../types/route";

export function planRoute(data: RoutePlanRequest): Promise<RoutePlanResponse> {
  return apiRequest<RoutePlanResponse>("/routes/plan", {
    method: "POST",
    body: JSON.stringify(data),
  });
}
