import { useEffect, useState, type FormEvent } from "react";
import { Link, Navigate, useNavigate, useParams } from "react-router-dom";

import {
  createPost,
  findSimilarPosts,
  getPost,
  updatePost,
} from "../api/boardApi";
import { ApiError } from "../api/client";
import type { SimilarPostItem } from "../api/types";
import { useAuth } from "../auth/AuthContext";

function parseTags(value: string) {
  return value
    .split(",")
    .map((tag) => tag.trim())
    .filter(Boolean);
}

function formatSimilarity(value: number) {
  return `${Math.round(value * 100)}%`;
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
  const [similarErrorMessage, setSimilarErrorMessage] = useState("");
  const [similarStatusMessage, setSimilarStatusMessage] = useState("");
  const [similarSummary, setSimilarSummary] = useState<string | null>(null);
  const [similarPosts, setSimilarPosts] = useState<SimilarPostItem[]>([]);
  const [isLoading, setIsLoading] = useState(isEditMode);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isFindingSimilar, setIsFindingSimilar] = useState(false);
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

  async function handleFindSimilarPosts() {
    if (!token || !title.trim() || !content.trim()) {
      return;
    }

    setSimilarErrorMessage("");
    setSimilarStatusMessage("");
    setSimilarSummary(null);
    setSimilarPosts([]);
    setIsFindingSimilar(true);

    try {
      const response = await findSimilarPosts(
        {
          title,
          content,
          tags: parseTags(tagInput),
          limit: 5,
          exclude_post_id: isEditMode ? numericPostId : undefined,
        },
        token,
      );
      setSimilarSummary(response.summary);
      setSimilarPosts(response.items);
      setSimilarStatusMessage(response.message ?? "");
    } catch (error) {
      if (error instanceof ApiError) {
        setSimilarErrorMessage(error.message);
      } else {
        setSimilarErrorMessage("유사 게시글을 찾는 중 문제가 발생했습니다.");
      }
    } finally {
      setIsFindingSimilar(false);
    }
  }

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
              ? "기존 질문의 제목, 본문, 태그를 수정합니다."
              : "질문을 저장하기 전에 비슷한 과거 글을 먼저 찾아볼 수 있습니다."}
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

          <section className="rag-panel">
            <div className="section-title-row">
              <div>
                <h2>유사 글 추천</h2>
                <p>현재 입력한 내용과 비슷한 과거 게시글을 찾아봅니다.</p>
              </div>
              <button
                className="secondary-button"
                disabled={
                  isFindingSimilar || !title.trim() || !content.trim()
                }
                onClick={handleFindSimilarPosts}
                type="button"
              >
                {isFindingSimilar ? "찾는 중" : "유사 글 찾기"}
              </button>
            </div>

            {similarErrorMessage && (
              <p className="form-error">{similarErrorMessage}</p>
            )}

            {similarStatusMessage && (
              <p className="rag-message">{similarStatusMessage}</p>
            )}

            {similarSummary && (
              <p className="rag-summary">{similarSummary}</p>
            )}

            {similarPosts.length > 0 ? (
              <div className="similar-post-list">
                {similarPosts.map((post) => (
                  <Link
                    className="similar-post-card"
                    key={post.post_id}
                    target="_blank"
                    to={`/posts/${post.post_id}`}
                  >
                    <div>
                      <strong>{post.title}</strong>
                      <p>{post.content_preview}</p>
                    </div>
                    <div className="similar-post-meta">
                      <span>{formatSimilarity(post.similarity)}</span>
                      <div className="tag-list detail-tags">
                        {post.tag_names.map((tag) => (
                          <span className="tag-chip" key={tag}>
                            {tag}
                          </span>
                        ))}
                      </div>
                    </div>
                  </Link>
                ))}
              </div>
            ) : (
              !isFindingSimilar && (
                <p className="empty-state">아직 추천 결과가 없습니다.</p>
              )
            )}
          </section>

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
