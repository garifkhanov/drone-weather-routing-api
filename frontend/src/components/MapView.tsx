import { useEffect, useMemo, useState } from "react";
import L, { type LatLngBoundsExpression, type LeafletMouseEvent } from "leaflet";
import {
  MapContainer,
  Marker,
  Polyline,
  Popup,
  TileLayer,
  useMap,
  useMapEvents,
} from "react-leaflet";
import type { MapMode, MapPoint, RouteWaypoint } from "../types/route";
import type { SavedPoint } from "../types/savedPoint";
import type { WeatherPoint } from "../types/weather";

interface MapViewProps {
  mapMode: MapMode;
  startPoint: MapPoint | null;
  endPoint: MapPoint | null;
  route: RouteWaypoint[];
  savedPoints: SavedPoint[];
  selectedWeather: WeatherPoint | null;
  isLoadingWeather: boolean;
  onPointSelected: (mode: MapMode, point: MapPoint) => void;
  onWeatherRequest: (point: MapPoint) => void;
}

interface MapClickHandlerProps {
  mapMode: MapMode;
  onPointSelected: (mode: MapMode, point: MapPoint) => void;
  onWeatherRequest: (point: MapPoint) => void;
  onHoverPoint: (point: MapPoint) => void;
}

function markerIcon(label: string, className: string): L.DivIcon {
  return L.divIcon({
    className: `map-marker ${className}`,
    html: label,
    iconSize: [30, 30],
    iconAnchor: [15, 15],
  });
}

function MapClickHandler({
  mapMode,
  onPointSelected,
  onWeatherRequest,
  onHoverPoint,
}: MapClickHandlerProps) {
  useMapEvents({
    click(event: LeafletMouseEvent) {
      const point = {
        lat: event.latlng.lat,
        lon: event.latlng.lng,
      };

      if (mapMode === "weather") {
        onWeatherRequest(point);
        return;
      }

      onPointSelected(mapMode, point);
    },
    mousemove(event: LeafletMouseEvent) {
      onHoverPoint({
        lat: event.latlng.lat,
        lon: event.latlng.lng,
      });
    },
  });

  return null;
}

function FitRoute({ route }: { route: RouteWaypoint[] }) {
  const map = useMap();

  useEffect(() => {
    if (route.length > 1) {
      const bounds: LatLngBoundsExpression = route.map((point) => [
        point.lat,
        point.lon,
      ]);
      map.fitBounds(bounds, { padding: [40, 40] });
    }
  }, [map, route]);

  return null;
}

function weatherPopupText(weather: WeatherPoint): string {
  return [
    `Ветер: ${weather.wind_speed_ms} м/с`,
    `Порывы: ${weather.wind_gust_ms} м/с`,
    `Осадки: ${weather.precipitation_mm} мм`,
    weather.temperature_c !== null && weather.temperature_c !== undefined
      ? `Температура: ${weather.temperature_c} °C`
      : null,
  ]
    .filter(Boolean)
    .join(", ");
}

export default function MapView({
  mapMode,
  startPoint,
  endPoint,
  route,
  savedPoints,
  selectedWeather,
  isLoadingWeather,
  onPointSelected,
  onWeatherRequest,
}: MapViewProps) {
  const [hoverPoint, setHoverPoint] = useState<MapPoint | null>(null);
  const icons = useMemo(
    () => ({
      start: markerIcon("S", "start-marker"),
      end: markerIcon("F", "end-marker"),
      saved: markerIcon("P", "saved-marker"),
    }),
    [],
  );
  const routePositions = useMemo(
    () => route.map((point) => [point.lat, point.lon] as [number, number]),
    [route],
  );

  return (
    <div className="map-wrap">
      <MapContainer
        center={[59.3293, 18.0686]}
        zoom={6}
        minZoom={2}
        maxZoom={18}
        scrollWheelZoom
        attributionControl={false}
        className="map"
      >
        <TileLayer
          maxZoom={18}
          url="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
        />

        <MapClickHandler
          mapMode={mapMode}
          onPointSelected={onPointSelected}
          onWeatherRequest={onWeatherRequest}
          onHoverPoint={setHoverPoint}
        />
        <FitRoute route={route} />

        {startPoint && (
          <Marker position={[startPoint.lat, startPoint.lon]} icon={icons.start}>
            <Popup>Старт: {startPoint.lat.toFixed(5)}, {startPoint.lon.toFixed(5)}</Popup>
          </Marker>
        )}

        {endPoint && (
          <Marker position={[endPoint.lat, endPoint.lon]} icon={icons.end}>
            <Popup>Финиш: {endPoint.lat.toFixed(5)}, {endPoint.lon.toFixed(5)}</Popup>
          </Marker>
        )}

        {savedPoints.map((point) => (
          <Marker
            key={point.id}
            position={[point.lat, point.lon]}
            icon={icons.saved}
          >
            <Popup>
              <strong>{point.name}</strong>
              <br />
              {point.lat.toFixed(5)}, {point.lon.toFixed(5)}
            </Popup>
          </Marker>
        ))}

        {routePositions.length > 1 && (
          <Polyline
            positions={routePositions}
            pathOptions={{ color: "#0f7a67", weight: 5, opacity: 0.85 }}
          />
        )}

        {selectedWeather && (
          <Popup position={[selectedWeather.lat, selectedWeather.lon]}>
            <strong>Погода</strong>
            <br />
            {weatherPopupText(selectedWeather)}
          </Popup>
        )}
      </MapContainer>

      <div className="map-status">
        <span>Режим: {mapMode === "start" ? "старт" : mapMode === "end" ? "финиш" : mapMode === "save" ? "сохранение" : "погода"}</span>
        {hoverPoint && (
          <span>{hoverPoint.lat.toFixed(5)}, {hoverPoint.lon.toFixed(5)}</span>
        )}
        {isLoadingWeather && <span>Загрузка погоды...</span>}
      </div>
    </div>
  );
}
