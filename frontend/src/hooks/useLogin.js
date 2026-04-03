import { useState } from "react";
import { useNavigate } from "react-router-dom";

import { buildApiUrl } from "../config/api";

export const useLogin = (setIsLoggedIn) => {
  const navigate = useNavigate();

  const [userId, setUserId] = useState("");
  const [userPw, setUserPw] = useState("");
  const [error, setError] = useState("");

  const handleLogin = async (e) => {
    e.preventDefault();
    setError("");

    try {
      const formData = new FormData();
      formData.append("user_id", userId);
      formData.append("user_pw", userPw);

      const response = await fetch(buildApiUrl("/auth/login"), {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        setError(errorData.detail || "로그인 실패");
        return;
      }

      const data = await response.json();
      localStorage.setItem("userName", data.user_name || data.user_id || "");
      localStorage.setItem("userId", data.user_id || "");
      localStorage.setItem("userDbId", String(data.user_db_id || ""));
      localStorage.setItem("session_token", data.session_token || "");
      localStorage.setItem("isLoggedIn", "true");

      if (setIsLoggedIn) setIsLoggedIn(true);
      window.dispatchEvent(new Event("authStateChanged"));
      navigate("/");
    } catch (_) {
      setError("서버 연결 실패");
    }
  };

  return {
    userId,
    setUserId,
    userPw,
    setUserPw,
    error,
    handleLogin,
  };
};
