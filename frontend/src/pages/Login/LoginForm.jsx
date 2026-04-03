import React from "react";
import { Link } from "react-router-dom";

const LoginForm = ({
  userId,
  setUserId,
  userPw,
  setUserPw,
  error,
  handleLogin,
}) => {
  return (
    <div className="login-form-wrapper">
      <form onSubmit={handleLogin}>
        <div className="form-group input-with-icon">
          <span className="input-icon">🆔</span>
          <input
            type="text"
            value={userId}
            onChange={(e) => setUserId(e.target.value)}
            placeholder="아이디"
            required
          />
        </div>
        <div className="form-group input-with-icon">
          <span className="input-icon">🔒</span>
          <input
            type="password"
            value={userPw}
            onChange={(e) => setUserPw(e.target.value)}
            placeholder="비밀번호"
            required
          />
        </div>
        {error && <p className="error-msg">{error}</p>}
        <button type="submit" className="login-submit-btn">
          로그인
        </button>
      </form>

      <div className="footer-links">
        <p>
          계정이 없으신가요? <Link to="/register">회원가입</Link>
        </p>
      </div>
    </div>
  );
};

export default LoginForm;
