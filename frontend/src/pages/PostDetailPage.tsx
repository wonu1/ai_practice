import { useEffect, useState, type FormEvent } from "react";
import { Link, Navigate, useNavigate, useParams } from "react-router-dom";

import {
  createComment,
  deleteComment,
  deletePost,
  getComments,
  getPost,
} from "../api/boardApi";
import { ApiError } from "../api/client";
import type { Comment, Post } from "../api/types";
import { useAuth } from "../auth/AuthContext";

function formatDate(value: string) {
  return new Intl.DateTimeFormat("ko-KR", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));
}

function PostDetailPage() {
  const { postId } = useParams();
  const navigate = useNavigate();
  const { token, user } = useAuth();
  const [post, setPost] = useState<Post | null>(null);
  const [comments, setComments] = useState<Comment[]>([]);
  const [errorMessage, setErrorMessage] = useState("");
  const [commentContent, setCommentContent] = useState("");
  const [commentErrorMessage, setCommentErrorMessage] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const [isDeleting, setIsDeleting] = useState(false);
  const [isCommentSubmitting, setIsCommentSubmitting] = useState(false);

  const numericPostId = Number(postId);
  const isInvalidPostId = !postId || Number.isNaN(numericPostId);
  const canManagePost = Boolean(user && post && user.id === post.author.id);

  useEffect(() => {
    if (isInvalidPostId) {
      return;
    }

    async function loadPostDetail() {
      setIsLoading(true);
      setErrorMessage("");

      try {
        const [postResponse, commentResponse] = await Promise.all([
          getPost(numericPostId),
          getComments(numericPostId),
        ]);
        setPost(postResponse);
        setComments(commentResponse.items);
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

    void loadPostDetail();
  }, [isInvalidPostId, numericPostId]);

  async function handleDelete() {
    if (!post || !token) {
      return;
    }

    const shouldDelete = window.confirm("게시글을 삭제할까요?");

    if (!shouldDelete) {
      return;
    }

    setIsDeleting(true);
    setErrorMessage("");

    try {
      await deletePost(post.id, token);
      navigate("/posts", { replace: true });
    } catch (error) {
      if (error instanceof ApiError) {
        setErrorMessage(error.message);
      } else {
        setErrorMessage("게시글 삭제 중 문제가 발생했습니다.");
      }
    } finally {
      setIsDeleting(false);
    }
  }

  async function handleCreateComment(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (!token || !post || !commentContent.trim()) {
      return;
    }

    setIsCommentSubmitting(true);
    setCommentErrorMessage("");

    try {
      const createdComment = await createComment(
        post.id,
        commentContent.trim(),
        token,
      );
      setComments((currentComments) => [...currentComments, createdComment]);
      setCommentContent("");
    } catch (error) {
      if (error instanceof ApiError) {
        setCommentErrorMessage(error.message);
      } else {
        setCommentErrorMessage("댓글 작성 중 문제가 발생했습니다.");
      }
    } finally {
      setIsCommentSubmitting(false);
    }
  }

  async function handleDeleteComment(commentId: number) {
    if (!token) {
      return;
    }

    const shouldDelete = window.confirm("댓글을 삭제할까요?");

    if (!shouldDelete) {
      return;
    }

    setCommentErrorMessage("");

    try {
      await deleteComment(commentId, token);
      setComments((currentComments) =>
        currentComments.filter((comment) => comment.id !== commentId),
      );
    } catch (error) {
      if (error instanceof ApiError) {
        setCommentErrorMessage(error.message);
      } else {
        setCommentErrorMessage("댓글 삭제 중 문제가 발생했습니다.");
      }
    }
  }

  if (isInvalidPostId) {
    return <Navigate to="/posts" replace />;
  }

  return (
    <section className="panel detail-panel">
      {isLoading ? (
        <p className="empty-state">게시글을 불러오는 중입니다.</p>
      ) : post ? (
        <>
          <div className="page-heading">
            <div>
              <p className="eyebrow">Post #{post.id}</p>
              <h1>{post.title}</h1>
              <p className="section-copy">
                {post.author.nickname} · {formatDate(post.created_at)}
              </p>
            </div>

            {canManagePost && (
              <div className="action-group">
                <Link className="secondary-button" to={`/posts/${post.id}/edit`}>
                  수정
                </Link>
                <button
                  className="danger-button"
                  disabled={isDeleting}
                  onClick={handleDelete}
                  type="button"
                >
                  {isDeleting ? "삭제 중" : "삭제"}
                </button>
              </div>
            )}
          </div>

          {errorMessage && <p className="form-error">{errorMessage}</p>}

          <div className="tag-list detail-tags" aria-label="게시글 태그">
            {post.tags.map((tag) => (
              <span className="tag-chip" key={tag}>
                {tag}
              </span>
            ))}
          </div>

          <article className="post-content">{post.content}</article>

          <section className="comments-section">
            <div className="section-title-row">
              <h2>댓글</h2>
              <span>{comments.length}개</span>
            </div>

            {user ? (
              <form className="comment-form" onSubmit={handleCreateComment}>
                <label className="field">
                  <span>댓글 작성</span>
                  <textarea
                    onChange={(event) => setCommentContent(event.target.value)}
                    placeholder="답변이나 추가 의견을 남겨주세요."
                    required
                    rows={4}
                    value={commentContent}
                  />
                </label>
                {commentErrorMessage && (
                  <p className="form-error">{commentErrorMessage}</p>
                )}
                <button
                  className="secondary-button"
                  disabled={isCommentSubmitting}
                  type="submit"
                >
                  {isCommentSubmitting ? "등록 중" : "댓글 등록"}
                </button>
              </form>
            ) : (
              <p className="empty-state">
                댓글을 작성하려면 <Link to="/login">로그인</Link>이 필요합니다.
              </p>
            )}

            {comments.length > 0 ? (
              <div className="comment-list">
                {comments.map((comment) => (
                  <article className="comment-item" key={comment.id}>
                    <div className="comment-body">
                      <p>{comment.content}</p>
                      <span>
                        {comment.author.nickname} ·{" "}
                        {formatDate(comment.created_at)}
                      </span>
                    </div>
                    {user?.id === comment.author.id && (
                      <button
                        className="text-button danger-text"
                        onClick={() => void handleDeleteComment(comment.id)}
                        type="button"
                      >
                        삭제
                      </button>
                    )}
                  </article>
                ))}
              </div>
            ) : (
              <p className="empty-state">아직 댓글이 없습니다.</p>
            )}
          </section>
        </>
      ) : (
        <p className="empty-state">
          게시글을 찾지 못했습니다. <Link to="/posts">목록으로 이동</Link>
        </p>
      )}
    </section>
  );
}

export default PostDetailPage;
