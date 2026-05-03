import { useCallback, useEffect, useMemo, useState } from "react";
import { clearStoredToken, getStoredToken, ApiError } from "./api/client";
import { getDrones } from "./api/dronesApi";
import { getSavedPoints } from "./api/savedPointsApi";
import { getWeatherPoint } from "./api/weatherApi";
import { planRoute } from "./api/routesApi";
import AuthPanel from "./components/AuthPanel";
import DronePanel from "./components/DronePanel";
import MapView from "./components/MapView";
import RoutePlannerPanel from "./components/RoutePlannerPanel";
import SavedPointsPanel from "./components/SavedPointsPanel";
import RouteResultPanel from "./components/RouteResultPanel";
import WeatherPopup from "./components/WeatherPopup";
import type { Drone } from "./types/drone";
import type { MapMode, MapPoint, RoutePlanResponse } from "./types/route";
import type { SavedPoint, SavedPointCreate, SavedPointUpdate } from "./types/savedPoint";
import type { WeatherPoint } from "./types/weather";
import {
  createSavedPoint,
  deleteSavedPoint,
  updateSavedPoint,
} from "./api/savedPointsApi";

const defaultDepartureTime = new Date(Date.now() + 60 * 60 * 1000)
  .toISOString()
  .slice(0, 16);

function getErrorMessage(error: unknown): string {
  if (error instanceof ApiError) {
    return error.message;
  }
  if (error instanceof Error) {
    return error.message;
  }
  return "Неизвестная ошибка";
}

export default function App() {
  const [token, setToken] = useState<string | null>(() => getStoredToken());
  const [drones, setDrones] = useState<Drone[]>([]);
  const [selectedDroneId, setSelectedDroneId] = useState<number | null>(null);
  const [savedPoints, setSavedPoints] = useState<SavedPoint[]>([]);
  const [startPoint, setStartPoint] = useState<MapPoint | null>(null);
  const [endPoint, setEndPoint] = useState<MapPoint | null>(null);
  const [draftSavedPoint, setDraftSavedPoint] = useState<MapPoint | null>(null);
  const [mapMode, setMapMode] = useState<MapMode>("weather");
  const [departureTime, setDepartureTime] = useState(defaultDepartureTime);
  const [gridSize, setGridSize] = useState(8);
  const [corridorWidthKm, setCorridorWidthKm] = useState(25);
  const [routeResult, setRouteResult] = useState<RoutePlanResponse | null>(null);
  const [selectedWeather, setSelectedWeather] = useState<WeatherPoint | null>(null);
  const [startWeather, setStartWeather] = useState<WeatherPoint | null>(null);
  const [endWeather, setEndWeather] = useState<WeatherPoint | null>(null);
  const [appError, setAppError] = useState<string | null>(null);
  const [isLoadingWeather, setIsLoadingWeather] = useState(false);
  const [isPlanning, setIsPlanning] = useState(false);
  const isAuthenticated = Boolean(token);

  const selectedDrone = useMemo(
    () => drones.find((drone) => drone.id === selectedDroneId) ?? null,
    [drones, selectedDroneId],
  );

  const loadProtectedData = useCallback(async () => {
    if (!token) {
      return;
    }

    try {
      const [loadedDrones, loadedSavedPoints] = await Promise.all([
        getDrones(),
        getSavedPoints(),
      ]);
      setDrones(loadedDrones);
      setSavedPoints(loadedSavedPoints);
      setSelectedDroneId((currentId) => {
        if (currentId && loadedDrones.some((drone) => drone.id === currentId)) {
          return currentId;
        }
        return loadedDrones[0]?.id ?? null;
      });
      setAppError(null);
    } catch (error) {
      setAppError(getErrorMessage(error));
    }
  }, [token]);

  useEffect(() => {
    loadProtectedData();
  }, [loadProtectedData]);

  useEffect(() => {
    setRouteResult(null);
  }, [selectedDroneId]);

  const loadPointWeather = useCallback(
    async (point: MapPoint, setter: (weather: WeatherPoint | null) => void) => {
      if (!token) {
        return;
      }

      try {
        const weather = await getWeatherPoint(point.lat, point.lon, departureTime);
        setter(weather);
      } catch (error) {
        setter(null);
        setAppError(getErrorMessage(error));
      }
    },
    [departureTime, token],
  );

  useEffect(() => {
    if (startPoint) {
      loadPointWeather(startPoint, setStartWeather);
    } else {
      setStartWeather(null);
    }
  }, [loadPointWeather, startPoint]);

  useEffect(() => {
    if (endPoint) {
      loadPointWeather(endPoint, setEndWeather);
    } else {
      setEndWeather(null);
    }
  }, [endPoint, loadPointWeather]);

  function handleAuthenticated(accessToken: string) {
    setToken(accessToken);
    setAppError(null);
  }

  function handleLogout() {
    clearStoredToken();
    setToken(null);
    setDrones([]);
    setSavedPoints([]);
    setSelectedDroneId(null);
    setStartPoint(null);
    setEndPoint(null);
    setRouteResult(null);
    setSelectedWeather(null);
    setAppError(null);
  }

  function handleMapPoint(mode: MapMode, point: MapPoint) {
    if (mode === "start") {
      setStartPoint(point);
      setRouteResult(null);
    }
    if (mode === "end") {
      setEndPoint(point);
      setRouteResult(null);
    }
    if (mode === "save") {
      setDraftSavedPoint(point);
    }
  }

  async function handleWeatherRequest(point: MapPoint) {
    if (!token) {
      setAppError("Для просмотра погоды нужно войти в систему.");
      return;
    }

    setIsLoadingWeather(true);
    try {
      const weather = await getWeatherPoint(point.lat, point.lon, departureTime);
      setSelectedWeather(weather);
      setAppError(null);
    } catch (error) {
      setAppError(getErrorMessage(error));
    } finally {
      setIsLoadingWeather(false);
    }
  }

  async function handlePlanRoute() {
    if (!selectedDrone || !startPoint || !endPoint) {
      return;
    }

    setIsPlanning(true);
    setRouteResult(null);

    try {
      const result = await planRoute({
        drone_id: selectedDrone.id,
        start_lat: startPoint.lat,
        start_lon: startPoint.lon,
        end_lat: endPoint.lat,
        end_lon: endPoint.lon,
        departure_time: departureTime,
        grid_size: gridSize,
        corridor_width_km: corridorWidthKm,
      });
      setRouteResult(result);
      setAppError(null);
    } catch (error) {
      setAppError(getErrorMessage(error));
    } finally {
      setIsPlanning(false);
    }
  }

  async function handleCreateSavedPoint(data: SavedPointCreate) {
    const savedPoint = await createSavedPoint(data);
    setSavedPoints((items) => [...items, savedPoint]);
    setDraftSavedPoint(null);
  }

  async function handleUpdateSavedPoint(id: number, data: SavedPointUpdate) {
    const updatedPoint = await updateSavedPoint(id, data);
    setSavedPoints((items) =>
      items.map((item) => (item.id === id ? updatedPoint : item)),
    );
  }

  async function handleDeleteSavedPoint(id: number) {
    await deleteSavedPoint(id);
    setSavedPoints((items) => items.filter((item) => item.id !== id));
  }

  function handleUseSavedAsStart(point: MapPoint) {
    setStartPoint(point);
    setRouteResult(null);
  }

  function handleUseSavedAsEnd(point: MapPoint) {
    setEndPoint(point);
    setRouteResult(null);
  }

  return (
    <div className="app-shell">
      <header className="topbar">
        <div>
          <h1>Drone Weather Routing API</h1>
          <p>Учебный интерфейс планирования погодоустойчивого маршрута</p>
        </div>
        <div className="topbar-actions">
          <span className={isAuthenticated ? "status-dot active" : "status-dot"}>
            {isAuthenticated ? "Авторизован" : "Гость"}
          </span>
          {isAuthenticated && (
            <button className="button ghost" type="button" onClick={handleLogout}>
              Выйти
            </button>
          )}
        </div>
      </header>

      {appError && <div className="app-alert">{appError}</div>}

      <main className="workspace">
        <aside className="left-panel">
          <AuthPanel
            isAuthenticated={isAuthenticated}
            onAuthenticated={handleAuthenticated}
            onLogout={handleLogout}
          />

          {isAuthenticated && (
            <>
              <DronePanel
                drones={drones}
                selectedDroneId={selectedDroneId}
                onDronesChange={setDrones}
                onSelectDrone={setSelectedDroneId}
              />
              <RoutePlannerPanel
                selectedDrone={selectedDrone}
                startPoint={startPoint}
                endPoint={endPoint}
                startWeather={startWeather}
                endWeather={endWeather}
                mapMode={mapMode}
                departureTime={departureTime}
                gridSize={gridSize}
                corridorWidthKm={corridorWidthKm}
                isPlanning={isPlanning}
                onMapModeChange={setMapMode}
                onDepartureTimeChange={setDepartureTime}
                onGridSizeChange={setGridSize}
                onCorridorWidthChange={setCorridorWidthKm}
                onPlanRoute={handlePlanRoute}
              />
              <SavedPointsPanel
                savedPoints={savedPoints}
                startPoint={startPoint}
                endPoint={endPoint}
                draftPoint={draftSavedPoint}
                onCreate={handleCreateSavedPoint}
                onUpdate={handleUpdateSavedPoint}
                onDelete={handleDeleteSavedPoint}
                onUseAsStart={handleUseSavedAsStart}
                onUseAsEnd={handleUseSavedAsEnd}
                onPickOnMap={() => setMapMode("save")}
              />
            </>
          )}
        </aside>

        <section className="map-area">
          <MapView
            mapMode={mapMode}
            startPoint={startPoint}
            endPoint={endPoint}
            route={routeResult?.status === "route_found" ? routeResult.route : []}
            savedPoints={savedPoints}
            selectedWeather={selectedWeather}
            isLoadingWeather={isLoadingWeather}
            onPointSelected={handleMapPoint}
            onWeatherRequest={handleWeatherRequest}
          />
        </section>

        <aside className="right-panel">
          <WeatherPopup weather={selectedWeather} isLoading={isLoadingWeather} />
          <RouteResultPanel result={routeResult} />
        </aside>
      </main>
    </div>
  );
}
