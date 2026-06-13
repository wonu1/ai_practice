import { useState, type FormEvent } from "react";
import { Link, Navigate, useLocation, useNavigate } from "react-router-dom";

import { login } from "../api/boardApi";
import { ApiError } from "../api/client";
import { useAuth } from "../auth/AuthContext";

function LoginPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const { applyLogin, isAuthenticated } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [errorMessage, setErrorMessage] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const redirectTo = location.state?.from?.pathname ?? "/posts";
  const noticeMessage = location.state?.message;

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setErrorMessage("");
    setIsSubmitting(true);

    try {
      const tokenResponse = await login({ email, password });
      await applyLogin(tokenResponse.access_token);
      navigate(redirectTo, { replace: true });
    } catch (error) {
      if (error instanceof ApiError) {
        setErrorMessage(error.message);
      } else {
        setErrorMessage("로그인 중 문제가 발생했습니다.");
      }
    } finally {
      setIsSubmitting(false);
    }
  }

  if (isAuthenticated) {
    return <Navigate to="/posts" replace />;
  }

  return (
    <section className="panel auth-panel">
      <p className="eyebrow">Auth</p>
      <h1>로그인</h1>
      <p className="section-copy">
        가입한 이메일과 비밀번호로 게시판에 로그인한다.
      </p>

      {noticeMessage && <p className="form-success">{noticeMessage}</p>}

      <form className="form-stack" onSubmit={handleSubmit}>
        <label className="field">
          <span>이메일</span>
          <input
            autoComplete="email"
            name="email"
            onChange={(event) => setEmail(event.target.value)}
            placeholder="you@example.com"
            required
            type="email"
            value={email}
          />
        </label>

        <label className="field">
          <span>비밀번호</span>
          <input
            autoComplete="current-password"
            minLength={8}
            name="password"
            onChange={(event) => setPassword(event.target.value)}
            placeholder="8자 이상"
            required
            type="password"
            value={password}
          />
        </label>

        {errorMessage && <p className="form-error">{errorMessage}</p>}

        <button className="primary-button" disabled={isSubmitting} type="submit">
          {isSubmitting ? "로그인 중" : "로그인"}
        </button>
      </form>

      <p className="form-helper">
        계정이 없다면 <Link to="/signup">회원가입</Link>을 먼저 진행한다.
      </p>
    </section>
  );
}

export default LoginPage;
