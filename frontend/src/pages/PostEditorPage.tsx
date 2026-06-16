import { useEffect, useState, type FormEvent } from "react";
import { Link, Navigate, useNavigate, useParams } from "react-router-dom";

import {
  assistWritingWithAgent,
  createPost,
  findSimilarPosts,
  getPost,
  updatePost,
} from "../api/boardApi";
import { ApiError } from "../api/client";
import type {
  AgentAssistWritingResponse,
  SimilarPostItem,
} from "../api/types";
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
  const [agentResult, setAgentResult] =
    useState<AgentAssistWritingResponse | null>(null);
  const [agentErrorMessage, setAgentErrorMessage] = useState("");
  const [agentStatusMessage, setAgentStatusMessage] = useState("");
  const [isLoading, setIsLoading] = useState(isEditMode);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isFindingSimilar, setIsFindingSimilar] = useState(false);
  const [isRunningAgent, setIsRunningAgent] = useState(false);
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

  async function handleAssistWritingWithAgent() {
    if (!token || !title.trim() || !content.trim()) {
      return;
    }

    setAgentErrorMessage("");
    setAgentStatusMessage("");
    setAgentResult(null);
    setIsRunningAgent(true);

    try {
      const response = await assistWritingWithAgent(
        {
          title,
          content,
          tags: parseTags(tagInput),
        },
        token,
      );
      setAgentResult(response);
      setAgentStatusMessage(response.message ?? "Agent가 글쓰기 도움 결과를 만들었습니다.");
    } catch (error) {
      if (error instanceof ApiError) {
        setAgentErrorMessage(error.message);
      } else {
        setAgentErrorMessage("Agent를 실행하는 중 문제가 발생했습니다.");
      }
    } finally {
      setIsRunningAgent(false);
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
              : "질문을 저장하기 전에 비슷한 과거 글과 AI 초안을 확인할 수 있습니다."}
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

            {similarSummary && <p className="rag-summary">{similarSummary}</p>}

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

          <section className="agent-panel">
            <div className="section-title-row">
              <div>
                <h2>AI 글쓰기 Agent</h2>
                <p>
                  내부 유사 글과 외부 GitHub 이슈를 필요에 따라 조회하고,
                  질문 개선 피드백과 초안을 만듭니다.
                </p>
              </div>
              <button
                className="secondary-button"
                disabled={isRunningAgent || !title.trim() || !content.trim()}
                onClick={handleAssistWritingWithAgent}
                type="button"
              >
                {isRunningAgent ? "실행 중" : "AI 도움받기"}
              </button>
            </div>

            {agentErrorMessage && (
              <p className="form-error">{agentErrorMessage}</p>
            )}

            {agentStatusMessage && (
              <p className="agent-message">{agentStatusMessage}</p>
            )}

            {agentResult ? (
              <div className="agent-result">
                <div className="agent-block">
                  <h3>개선 피드백</h3>
                  {agentResult.feedback.length > 0 ? (
                    <ul className="agent-feedback-list">
                      {agentResult.feedback.map((feedback) => (
                        <li key={feedback}>{feedback}</li>
                      ))}
                    </ul>
                  ) : (
                    <p className="empty-state">추가 피드백이 없습니다.</p>
                  )}
                </div>

                <div className="agent-block">
                  <h3>초안</h3>
                  <p className="agent-draft">{agentResult.draft}</p>
                </div>

                {agentResult.similar_posts.length > 0 && (
                  <div className="agent-block">
                    <h3>참고한 내부 글</h3>
                    <div className="similar-post-list">
                      {agentResult.similar_posts.map((post) => (
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
                          </div>
                        </Link>
                      ))}
                    </div>
                  </div>
                )}

                {agentResult.external_refs.length > 0 && (
                  <div className="agent-block">
                    <h3>외부 참고자료</h3>
                    <div className="external-ref-list">
                      {agentResult.external_refs.map((issue) => (
                        <a
                          className="external-ref-card"
                          href={issue.url}
                          key={issue.url}
                          rel="noreferrer"
                          target="_blank"
                        >
                          <strong>{issue.title}</strong>
                          <span>
                            {issue.repository} · {issue.state}
                          </span>
                          <p>{issue.summary}</p>
                        </a>
                      ))}
                    </div>
                  </div>
                )}

                <div className="agent-control">
                  <span>단계 {agentResult.control.step_count}</span>
                  <span>도구 호출 {agentResult.control.tool_call_count}</span>
                  {agentResult.control.stopped && (
                    <span>{agentResult.control.stop_reason}</span>
                  )}
                </div>
              </div>
            ) : (
              !isRunningAgent && (
                <p className="empty-state">아직 Agent 실행 결과가 없습니다.</p>
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
