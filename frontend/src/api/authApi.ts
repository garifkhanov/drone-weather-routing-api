import { apiRequest, setStoredToken } from "./client";
import type { AuthCredentials, TokenResponse } from "../types/auth";

export async function registerUser(credentials: AuthCredentials): Promise<void> {
  await apiRequest("/auth/register", {
    method: "POST",
    body: JSON.stringify(credentials),
    authorized: false,
  });
}

export async function loginUser(credentials: AuthCredentials): Promise<TokenResponse> {
  const tokenResponse = await apiRequest<TokenResponse>("/auth/login", {
    method: "POST",
    body: JSON.stringify(credentials),
    authorized: false,
  });

  setStoredToken(tokenResponse.access_token);
  return tokenResponse;
}
