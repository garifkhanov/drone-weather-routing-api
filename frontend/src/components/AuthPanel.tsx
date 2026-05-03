import { FormEvent, useState } from "react";
import { loginUser, registerUser } from "../api/authApi";
import { ApiError } from "../api/client";

interface AuthPanelProps {
  isAuthenticated: boolean;
  onAuthenticated: (token: string) => void;
  onLogout: () => void;
}

function getErrorMessage(error: unknown): string {
  if (error instanceof ApiError || error instanceof Error) {
    return error.message;
  }
  return "Не удалось выполнить запрос";
}

export default function AuthPanel({
  isAuthenticated,
  onAuthenticated,
  onLogout,
}: AuthPanelProps) {
  const [mode, setMode] = useState<"login" | "register">("login");
  const [email, setEmail] = useState("student@example.com");
  const [password, setPassword] = useState("secret123");
  const [isLoading, setIsLoading] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setIsLoading(true);
    setMessage(null);

    try {
      if (mode === "register") {
        await registerUser({ email, password });
      }
      const tokenResponse = await loginUser({ email, password });
      onAuthenticated(tokenResponse.access_token);
    } catch (error) {
      setMessage(getErrorMessage(error));
    } finally {
      setIsLoading(false);
    }
  }

  if (isAuthenticated) {
    return (
      <section className="panel">
        <div className="panel-header">
          <h2>Авторизация</h2>
        </div>
        <p className="muted">Вы вошли в систему. Защищённые действия доступны.</p>
        <button className="button secondary" type="button" onClick={onLogout}>
          Выйти
        </button>
      </section>
    );
  }

  return (
    <section className="panel">
      <div className="panel-header">
        <h2>Авторизация</h2>
      </div>
      <div className="segmented">
        <button
          className={mode === "login" ? "active" : ""}
          type="button"
          onClick={() => setMode("login")}
        >
          Вход
        </button>
        <button
          className={mode === "register" ? "active" : ""}
          type="button"
          onClick={() => setMode("register")}
        >
          Регистрация
        </button>
      </div>
      <form className="stack" onSubmit={handleSubmit}>
        <label>
          Email
          <input
            type="email"
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            required
          />
        </label>
        <label>
          Пароль
          <input
            type="password"
            value={password}
            minLength={6}
            onChange={(event) => setPassword(event.target.value)}
            required
          />
        </label>
        {message && <p className="error-text">{message}</p>}
        <button className="button primary" type="submit" disabled={isLoading}>
          {isLoading ? "Подождите..." : mode === "login" ? "Войти" : "Создать аккаунт"}
        </button>
      </form>
    </section>
  );
}
