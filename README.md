# Drone Weather Routing API

REST-сервис планирования погодоустойчивых маршрутов БПЛА.

Проект создан как учебный backend-сервис на FastAPI. Он демонстрирует работу с пользователями, JWT-авторизацией, реляционной базой данных, CRUD-операциями, веб-интерфейсом с картой и алгоритмической логикой поиска маршрута с учётом погодного риска.

Сервис не предназначен для реального управления БПЛА, авиационного планирования или принятия решений о настоящих полётах.

Пользователь может:

- зарегистрироваться и войти в систему;
- создать профиль дрона;
- управлять только своими дронами;
- создать запрос на маршрут;
- запустить планирование маршрута;
- получить результат маршрутизации и точки найденного пути;
- работать с приложением через веб-интерфейс на спутниковой карте;
- сохранять часто используемые точки маршрутов.

## Основные возможности

- `GET /health` — проверка работоспособности API.
- `POST /auth/register` — регистрация пользователя.
- `POST /auth/login` — получение access token.
- `POST /drones` — создание профиля дрона.
- `GET /drones` — список своих дронов.
- `GET /drones/{drone_id}` — получение своего дрона.
- `PATCH /drones/{drone_id}` — обновление своего дрона.
- `DELETE /drones/{drone_id}` — удаление своего дрона.
- `POST /route-requests` — создание запроса маршрута.
- `GET /route-requests` — список своих запросов маршрута.
- `GET /route-requests/{route_request_id}` — получение своего запроса маршрута.
- `DELETE /route-requests/{route_request_id}` — удаление своего запроса маршрута.
- `POST /routes/plan` — алгоритмическое планирование маршрута.
- `GET /routes/results/{route_result_id}` — получение результата маршрута.
- `GET /routes/results/{route_result_id}/waypoints` — получение точек маршрута.
- `GET /weather/point` — получение погоды в выбранной точке.
- `POST /saved-points` — создание сохранённой точки.
- `GET /saved-points` — список своих сохранённых точек.
- `GET /saved-points/{saved_point_id}` — получение своей сохранённой точки.
- `PATCH /saved-points/{saved_point_id}` — обновление своей сохранённой точки.
- `DELETE /saved-points/{saved_point_id}` — удаление своей сохранённой точки.

Все endpoints, кроме `/health`, `/auth/register` и `/auth/login`, требуют заголовок:

```text
Authorization: Bearer <access_token>
```

## Технологии

- Python 3.11+;
- FastAPI;
- Uvicorn;
- SQLAlchemy 2.x;
- Pydantic v2;
- SQLite;
- passlib и bcrypt;
- python-jose;
- httpx;
- pytest;
- pylint;
- pydantic-settings;
- python-dotenv;
- React;
- TypeScript;
- Vite;
- Leaflet и react-leaflet.

## Архитектура

Проект разделён на несколько слоёв:

- `app/api/routers` — HTTP endpoints;
- `app/api/deps.py` — FastAPI dependencies;
- `app/core` — настройки и безопасность;
- `app/db` — подключение к БД и создание таблиц;
- `app/models` — SQLAlchemy-модели;
- `app/schemas` — Pydantic-схемы запросов и ответов;
- `app/repositories` — работа с БД;
- `app/services` — бизнес-логика, погодный клиент, сетка, риск и A*.
- `frontend` — веб-интерфейс на React, TypeScript.

## Модель данных

В проекте используются таблицы:

- `users` — пользователи;
- `drones` — профили дронов;
- `route_requests` — запросы маршрутов;
- `weather_points` — погодные точки сетки;
- `route_results` — результаты планирования;
- `route_waypoints` — точки найденного маршрута;
- `saved_points` — часто используемые точки пользователя.

Связи:

- пользователь имеет много дронов;
- пользователь имеет много запросов маршрутов;
- дрон принадлежит пользователю;
- запрос маршрута связан с пользователем и дроном;
- запрос маршрута имеет много погодных точек;
- запрос маршрута имеет один результат;
- результат маршрута имеет много точек маршрута;
- пользователь имеет много сохранённых точек.

## Алгоритм маршрутизации

Endpoint `POST /routes/plan` выполняет следующие действия:

1. Проверяет авторизацию пользователя.
2. Проверяет, что `drone_id` принадлежит текущему пользователю.
3. Создаёт `route_request`.
4. Строит координатную сетку между стартовой и конечной точкой.
5. Получает погодные данные Open-Meteo для точек сетки.
6. Рассчитывает погодный риск каждой точки.
7. Блокирует точки, где погода превышает ограничения дрона.
8. Строит граф по сетке.
9. Запускает A*.
10. Считает обычную и эффективную дистанцию.
11. Проверяет запас хода дрона.
12. Сохраняет результат и точки маршрута в БД.

Формула риска:

```text
wind_ratio = wind_speed_ms / drone.max_wind_speed_ms
gust_ratio = wind_gust_ms / drone.max_gust_ms
precipitation_ratio = precipitation_mm / max(drone.max_precipitation_mm, 0.1)

risk = 0.5 * wind_ratio + 0.3 * gust_ratio + 0.2 * precipitation_ratio
risk = min(max(risk, 0.0), 1.0)
```

Стоимость ребра:

```text
edge_cost = distance_km * (1 + average_weather_risk)
```

Эвристика A*:

```text
haversine_distance_km(current, goal)
```

## Запуск проекта

Создать и активировать виртуальное окружение:

```powershell
python -m venv .venv
.venv\Scripts\activate
```

Установить зависимости:

```powershell
pip install -r requirements.txt
```

Запустить сервер:

```powershell
uvicorn app.main:app --reload
```

Если на Windows возникают ошибки `PermissionError: [WinError 5]` при запуске с `--reload`, можно запустить без reload:

```powershell
python -m uvicorn app.main:app
```

Swagger UI:

```text
http://127.0.0.1:8000/docs
```

Health check:

```text
http://127.0.0.1:8000/health
```

## Веб-интерфейс

Frontend находится в папке `frontend/`. Карта использует спутниковую подложку.

Запуск backend:

```powershell
uvicorn app.main:app --reload
```

Запуск frontend:

```powershell
cd frontend
npm install
npm run dev
```

Также frontend можно запускать из корня проекта:

```powershell
npm install
npm run dev
```

Если PowerShell после установки Node.js ещё не видит команду `npm`, можно запустить helper-скрипт:

```powershell
cd frontend
powershell -ExecutionPolicy Bypass -File .\start-dev.ps1
```

Открыть интерфейс:

```text
http://localhost:5173
```

Если браузер не открыл `localhost`, используйте прямой адрес:

```text
http://127.0.0.1:5173
```

Как пользоваться веб-интерфейсом:

1. Зарегистрироваться или войти через панель авторизации.
2. Создать профиль дрона или выбрать уже существующий.
3. На карте выбрать режим `Старт` и кликнуть по начальной точке.
4. Выбрать режим `Финиш` и кликнуть по конечной точке.
5. В режиме `Погода` кликнуть по карте, чтобы посмотреть погодные параметры точки.
6. При необходимости сохранить старт, финиш или произвольную точку в панели сохранённых точек.
7. Указать время вылета, размер сетки и ширину коридора.
8. Нажать `Построить маршрут`.
9. Посмотреть линию маршрута на карте и summary результата справа.

Frontend использует backend endpoints:

- `POST /auth/register`;
- `POST /auth/login`;
- `GET /drones`;
- `POST /drones`;
- `PATCH /drones/{drone_id}`;
- `DELETE /drones/{drone_id}`;
- `GET /weather/point`;
- `POST /routes/plan`;
- `GET /saved-points`;
- `POST /saved-points`;
- `PATCH /saved-points/{saved_point_id}`;
- `DELETE /saved-points/{saved_point_id}`.

Для локального frontend разрешены CORS origins:

- `http://localhost:5173`;
- `http://127.0.0.1:5173`.

## Примеры запросов

Регистрация:

```json
{
  "email": "student@example.com",
  "password": "secret123"
}
```

Создание дрона:

```json
{
  "name": "Test Drone",
  "max_range_km": 100,
  "max_wind_speed_ms": 10,
  "max_gust_ms": 15,
  "max_precipitation_mm": 0.5,
  "cruise_speed_kmh": 50
}
```

Планирование маршрута:

```json
{
  "drone_id": 1,
  "start_lat": 59.3293,
  "start_lon": 18.0686,
  "end_lat": 59.8586,
  "end_lon": 17.6389,
  "departure_time": "2026-05-03T10:00:00",
  "grid_size": 8,
  "corridor_width_km": 25
}
```

Пример успешного ответа:

```json
{
  "status": "route_found",
  "route_request_id": 1,
  "route_result_id": 1,
  "total_distance_km": 72.4,
  "effective_distance_km": 81.6,
  "risk_score": 0.28,
  "weather_summary": {
    "max_wind_speed_ms": 8.1,
    "max_gust_ms": 12.4,
    "max_precipitation_mm": 0.2
  },
  "route": [
    {
      "lat": 59.3293,
      "lon": 18.0686,
      "weather_risk": 0.1
    }
  ],
  "reason": null,
  "explanation": [
    "Route found using A* search on weather risk grid",
    "The route avoids points with excessive wind or precipitation",
    "Effective distance is within drone range"
  ]
}
```

## Запуск тестов

```powershell
pytest
```

Тесты используют отдельную in-memory SQLite БД и fake weather client. Реальный Open-Meteo в тестах не вызывается.

## Запуск pylint

```powershell
pylint app > pylint.txt
```

Файл `pylint.txt` добавлен в `.gitignore`, поэтому его можно создавать локально без попадания в репозиторий.

## Ограничения модели

- сервис демонстрационный;
- данные Open-Meteo используются только для учебного примера;
- координатная сетка является приближением;
- алгоритм не учитывает реальные авиационные правила, высоты, препятствия, зоны ограничений и телеметрию;
- результат нельзя использовать для настоящего управления БПЛА.

## Автор

Автор: Гарифханов Ильяс Тахирович
