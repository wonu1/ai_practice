import { useState, type FormEvent } from "react";
import { Link, Navigate, useNavigate, useParams } from "react-router-dom";

import { createPost } from "../api/boardApi";
import { ApiError } from "../api/client";
import { useAuth } from "../auth/AuthContext";

function parseTags(value: string) {
  return value
    .split(",")
    .map((tag) => tag.trim())
    .filter(Boolean);
}

function PostEditorPage() {
  const { postId } = useParams();
  const navigate = useNavigate();
  const { isAuthenticated, token } = useAuth();
  const isEditMode = Boolean(postId);
  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const [tagInput, setTagInput] = useState("");
  const [errorMessage, setErrorMessage] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (!token || isEditMode) {
      return;
    }

    setErrorMessage("");
    setIsSubmitting(true);

    try {
      const createdPost = await createPost(
        {
          title,
          content,
          tags: parseTags(tagInput),
        },
        token,
      );
      navigate(`/posts/${createdPost.id}`, { replace: true });
    } catch (error) {
      if (error instanceof ApiError) {
        setErrorMessage(error.message);
      } else {
        setErrorMessage("게시글 작성 중 문제가 발생했습니다.");
      }
    } finally {
      setIsSubmitting(false);
    }
  }

  if (!isAuthenticated) {
    return (
      <Navigate
        to="/login"
        replace
        state={{ from: { pathname: "/posts/new" } }}
      />
    );
  }

  return (
    <section className="panel editor-panel">
      <div className="page-heading">
        <div>
          <p className="eyebrow">Editor</p>
          <h1>{isEditMode ? "게시글 수정" : "게시글 작성"}</h1>
          <p className="section-copy">
            제목, 본문, 태그를 입력해 개발 질문을 게시한다.
          </p>
        </div>
        <Link className="secondary-button" to="/posts">
          목록
        </Link>
      </div>

      {isEditMode ? (
        <p className="empty-state">게시글 수정은 다음 단계에서 연결한다.</p>
      ) : (
        <form className="form-stack" onSubmit={handleSubmit}>
          <label className="field">
            <span>제목</span>
            <input
              maxLength={200}
              onChange={(event) => setTitle(event.target.value)}
              placeholder="예: FastAPI에서 JWT 인증이 자꾸 실패합니다"
              required
              type="text"
              value={title}
            />
          </label>

          <label className="field">
            <span>본문</span>
            <textarea
              onChange={(event) => setContent(event.target.value)}
              placeholder="상황, 시도한 방법, 에러 메시지를 적어주세요."
              required
              rows={12}
              value={content}
            />
          </label>

          <label className="field">
            <span>태그</span>
            <input
              onChange={(event) => setTagInput(event.target.value)}
              placeholder="react, fastapi, postgres"
              type="text"
              value={tagInput}
            />
          </label>

          {errorMessage && <p className="form-error">{errorMessage}</p>}

          <button className="primary-button" disabled={isSubmitting} type="submit">
            {isSubmitting ? "저장 중" : "게시글 작성"}
          </button>
        </form>
      )}
    </section>
  );
}

export default PostEditorPage;
