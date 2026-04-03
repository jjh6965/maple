import { useEffect, useState } from "react";
import {
  BrowserRouter as Router,
  Navigate,
  Route,
  Routes,
} from "react-router-dom";

import { buildApiUrl } from "./config/api";
import Login from "./pages/Login";
import Register from "./pages/Register";
import RealtimeChatPage from "./pages/RealtimeChatPage";

function ProtectedRoute({ isLoggedIn, children }) {
  if (!isLoggedIn) return <Navigate to="/login" replace />;
  return children;
}

function PublicRoute({ isLoggedIn, children }) {
  if (isLoggedIn) return <Navigate to="/" replace />;
  return children;
}

function TopBar({ onLogout }) {
  const userName = localStorage.getItem("userName") || "길드원";

  return (
    <header
      style={{
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
        padding: "12px 16px",
        borderBottom: "1px solid #243447",
        background: "#16212b",
        color: "#ecf2f9",
      }}
    >
      <strong>메이플 길드 실시간 채팅</strong>
      <div style={{ display: "flex", gap: "10px", alignItems: "center" }}>
        <span>{userName}</span>
        <button
          type="button"
          onClick={onLogout}
          style={{
            border: "1px solid #5f768d",
            background: "#203140",
            color: "#ecf2f9",
            borderRadius: 8,
            padding: "6px 10px",
            cursor: "pointer",
          }}
        >
          로그아웃
        </button>
      </div>
    </header>
  );
}

export default function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(
    localStorage.getItem("isLoggedIn") === "true",
  );

  useEffect(() => {
    const sync = () =>
      setIsLoggedIn(localStorage.getItem("isLoggedIn") === "true");
    window.addEventListener("storage", sync);
    window.addEventListener("authStateChanged", sync);
    return () => {
      window.removeEventListener("storage", sync);
      window.removeEventListener("authStateChanged", sync);
    };
  }, []);

  const handleLogout = async () => {
    const userDbId = localStorage.getItem("userDbId");
    const sessionToken = localStorage.getItem("session_token");

    try {
      if (userDbId) {
        const formData = new FormData();
        formData.append("user_id", userDbId);
        if (sessionToken) {
          formData.append("session_token", sessionToken);
        }

        await fetch(buildApiUrl("/auth/logout"), {
          method: "POST",
          body: formData,
        });
      }
    } catch (_) {
      // 서버 로그아웃 실패와 무관하게 클라이언트 세션은 정리한다.
    } finally {
      localStorage.removeItem("isLoggedIn");
      localStorage.removeItem("userName");
      localStorage.removeItem("userId");
      localStorage.removeItem("userDbId");
      localStorage.removeItem("session_token");
      localStorage.removeItem("userRole");
      window.dispatchEvent(new Event("authStateChanged"));
      setIsLoggedIn(false);
    }
  };

  return (
    <Router>
      {isLoggedIn && <TopBar onLogout={handleLogout} />}
      <Routes>
        <Route
          path="/login"
          element={
            <PublicRoute isLoggedIn={isLoggedIn}>
              <Login setIsLoggedIn={setIsLoggedIn} />
            </PublicRoute>
          }
        />
        <Route
          path="/register"
          element={
            <PublicRoute isLoggedIn={isLoggedIn}>
              <Register setIsLoggedIn={setIsLoggedIn} />
            </PublicRoute>
          }
        />
        <Route
          path="/"
          element={
            <ProtectedRoute isLoggedIn={isLoggedIn}>
              <RealtimeChatPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="*"
          element={<Navigate to={isLoggedIn ? "/" : "/login"} replace />}
        />
      </Routes>
    </Router>
  );
}
