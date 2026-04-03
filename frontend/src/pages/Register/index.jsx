// src/pages/Register/index.jsx
import React from "react";
import { Link } from "react-router-dom";
import { useRegister } from "../../hooks/useRegister"; // 커스텀 훅 임포트
import RegisterForm from "./RegisterForm";
import "./style.css";

const Register = () => {
  const {
    formData,
    error,
    idMessage,
    handleChange,
    handleCheckId,
    handleRegister,
  } = useRegister();

  return (
    <div className="register-body">
      <div className="register-container">
        <h2>회원가입</h2>
        <p className="subtitle">길드 실시간 채팅 이용을 위해 가입해주세요.</p>

        <RegisterForm
          formData={formData}
          handleChange={handleChange}
          handleCheckId={handleCheckId}
          idMessage={idMessage}
          handleRegister={handleRegister}
          error={error}
        />

        <div className="footer-links">
          이미 계정이 있으신가요? <Link to="/login">로그인 페이지로</Link>
        </div>
      </div>
    </div>
  );
};

export default Register;
