import { useState, type FormEvent } from "react";
import { Link, Navigate, useNavigate } from "react-router-dom";

import { signup } from "../api/boardApi";
import { ApiError } from "../api/client";
import { useAuth } from "../auth/AuthContext";

function SignupPage() {
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();
  const [email, setEmail] = useState("");
  const [nickname, setNickname] = useState("");
  const [password, setPassword] = useState("");
  const [errorMessage, setErrorMessage] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setErrorMessage("");
    setIsSubmitting(true);

    try {
      await signup({ email, nickname, password });
      navigate("/login", {
        replace: true,
        state: { message: "회원가입이 완료되었습니다. 다시 로그인해주세요." },
      });
    } catch (error) {
      if (error instanceof ApiError) {
        setErrorMessage(error.message);
      } else {
        setErrorMessage("회원가입 중 문제가 발생했습니다.");
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
      <h1>회원가입</h1>
      <p className="section-copy">
        이메일, 닉네임, 비밀번호로 게시판 계정을 만든다.
      </p>

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
          <span>닉네임</span>
          <input
            autoComplete="nickname"
            maxLength={50}
            minLength={2}
            name="nickname"
            onChange={(event) => setNickname(event.target.value)}
            placeholder="2자 이상"
            required
            type="text"
            value={nickname}
          />
        </label>

        <label className="field">
          <span>비밀번호</span>
          <input
            autoComplete="new-password"
            maxLength={100}
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
          {isSubmitting ? "가입 중" : "회원가입"}
        </button>
      </form>

      <p className="form-helper">
        이미 계정이 있다면 <Link to="/login">로그인</Link>으로 이동한다.
      </p>
    </section>
  );
}

export default SignupPage;
