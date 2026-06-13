import { useEffect, useState, type FormEvent } from "react";
import { Link, Navigate, useNavigate, useParams } from "react-router-dom";

import { createPost, getPost, updatePost } from "../api/boardApi";
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
  const { token, user } = useAuth();
  const isEditMode = Boolean(postId);
  const numericPostId = Number(postId);
  const isInvalidPostId = isEditMode && Number.isNaN(numericPostId);
  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const [tagInput, setTagInput] = useState("");
  const [errorMessage, setErrorMessage] = useState("");
  const [isLoading, setIsLoading] = useState(isEditMode);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [canEdit, setCanEdit] = useState(!isEditMode);

  useEffect(() => {
    if (!isEditMode || isInvalidPostId) {
      return;
    }

    async function loadPostForEdit() {
      setIsLoading(true);
      setErrorMessage("");

      try {
        const post = await getPost(numericPostId);
        setTitle(post.title);
        setContent(post.content);
        setTagInput(post.tags.join(", "));
        setCanEdit(Boolean(user && user.id === post.author.id));
      } catch (error) {
        if (error instanceof ApiError) {
          setErrorMessage(error.message);
        } else {
          setErrorMessage("게시글을 불러오지 못했습니다.");
        }
      } finally {
        setIsLoading(false);
      }
    }

    void loadPostForEdit();
  }, [isEditMode, isInvalidPostId, numericPostId, user]);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (!token) {
      return;
    }

    setErrorMessage("");
    setIsSubmitting(true);

    try {
      const payload = {
        title,
        content,
        tags: parseTags(tagInput),
      };

      if (isEditMode) {
        const updatedPost = await updatePost(numericPostId, payload, token);
        navigate(`/posts/${updatedPost.id}`, { replace: true });
      } else {
        const createdPost = await createPost(payload, token);
        navigate(`/posts/${createdPost.id}`, { replace: true });
      }
    } catch (error) {
      if (error instanceof ApiError) {
        setErrorMessage(error.message);
      } else {
        setErrorMessage("게시글 저장 중 문제가 발생했습니다.");
      }
    } finally {
      setIsSubmitting(false);
    }
  }

  if (isInvalidPostId) {
    return <Navigate to="/posts" replace />;
  }

  return (
    <section className="panel editor-panel">
      <div className="page-heading">
        <div>
          <p className="eyebrow">Editor</p>
          <h1>{isEditMode ? "게시글 수정" : "게시글 작성"}</h1>
          <p className="section-copy">
            {isEditMode
              ? "기존 질문의 제목, 본문, 태그를 수정한다."
              : "제목, 본문, 태그를 입력해 개발 질문을 게시한다."}
          </p>
        </div>
        <Link className="secondary-button" to="/posts">
          목록
        </Link>
      </div>

      {isLoading ? (
        <p className="empty-state">게시글을 불러오는 중입니다.</p>
      ) : isEditMode && !canEdit ? (
        <p className="empty-state">이 게시글을 수정할 권한이 없습니다.</p>
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
            {isSubmitting
              ? "저장 중"
              : isEditMode
                ? "게시글 수정"
                : "게시글 작성"}
          </button>
        </form>
      )}
    </section>
  );
}

export default PostEditorPage;
