// src/pages/Login/index.jsx
import React from "react";
import { useLogin } from "../../hooks/useLogin";
import LoginForm from "./LoginForm";
import "./style.css";

const Login = ({ setIsLoggedIn }) => {
  const loginLogic = useLogin(setIsLoggedIn);

  return (
    <div className="login-body">
      <div className="login-container">
        <h2 className="main-title">메이플 길드 실시간 채팅</h2>

        <LoginForm
          userId={loginLogic.userId}
          setUserId={loginLogic.setUserId}
          userPw={loginLogic.userPw}
          setUserPw={loginLogic.setUserPw}
          error={loginLogic.error}
          handleLogin={loginLogic.handleLogin}
        />
      </div>
    </div>
  );
};

export default Login;
