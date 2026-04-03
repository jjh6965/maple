import { useState } from "react";
import { useNavigate } from "react-router-dom";

import { buildApiUrl } from "../config/api";

export const useRegister = () => {
  const navigate = useNavigate();

  const [formData, setFormData] = useState({
    user_id: "",
    user_pw: "",
    user_pw_confirm: "",
    user_name: "",
    user_email: "",
  });
  const [error, setError] = useState("");
  const [idMessage, setIdMessage] = useState({ text: "", type: "" });

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
    if (e.target.name === "user_id") setIdMessage({ text: "", type: "" });
  };

  const handleCheckId = async () => {
    if (!formData.user_id) return;
    try {
      const response = await fetch(
        buildApiUrl(`/auth/check-id?user_id=${formData.user_id}`),
      );
      const data = await response.json();
      setIdMessage({
        text: data.message,
        type: data.available ? "success" : "error",
      });
    } catch (_) {
      setError("서버와 연결할 수 없습니다.");
    }
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    setError("");

    if (formData.user_pw !== formData.user_pw_confirm) {
      setError("비밀번호가 일치하지 않습니다.");
      return;
    }

    if (idMessage.type !== "success") {
      setError("아이디 중복 확인이 필요합니다.");
      return;
    }

    const payload = new FormData();
    payload.append("user_id", formData.user_id);
    payload.append("user_pw", formData.user_pw);
    payload.append("user_name", formData.user_name);
    payload.append("user_email", formData.user_email);

    try {
      const response = await fetch(buildApiUrl("/auth/register"), {
        method: "POST",
        body: payload,
      });
      if (!response.ok) {
        const data = await response.json().catch(() => ({}));
        setError(data.detail || "회원가입에 실패했습니다.");
        return;
      }

      navigate("/login");
    } catch (_) {
      setError("서버와 연결할 수 없습니다.");
    }
  };

  return {
    formData,
    error,
    idMessage,
    handleChange,
    handleCheckId,
    handleRegister,
  };
};
