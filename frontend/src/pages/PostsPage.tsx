import { useEffect, useState, type FormEvent } from "react";
import { Link, useSearchParams } from "react-router-dom";

import { getPosts, getTags } from "../api/boardApi";
import { ApiError } from "../api/client";
import type { PostListResponse, Tag } from "../api/types";

const PAGE_SIZE = 10;

function formatDate(value: string) {
  return new Intl.DateTimeFormat("ko-KR", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));
}

function PostsPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const [posts, setPosts] = useState<PostListResponse | null>(null);
  const [tags, setTags] = useState<Tag[]>([]);
  const [keywordInput, setKeywordInput] = useState(
    searchParams.get("keyword") ?? "",
  );
  const [errorMessage, setErrorMessage] = useState("");
  const [isLoading, setIsLoading] = useState(true);

  const page = Number(searchParams.get("page") ?? "1");
  const keyword = searchParams.get("keyword") ?? undefined;
  const tag = searchParams.get("tag") ?? undefined;
  const totalPages = posts ? Math.max(1, Math.ceil(posts.total / posts.size)) : 1;

  useEffect(() => {
    const nextKeyword = searchParams.get("keyword") ?? "";
    setKeywordInput(nextKeyword);
  }, [searchParams]);

  useEffect(() => {
    async function loadPosts() {
      setIsLoading(true);
      setErrorMessage("");

      try {
        const [postResponse, tagResponse] = await Promise.all([
          getPosts({ page, size: PAGE_SIZE, keyword, tag }),
          getTags(),
        ]);
        setPosts(postResponse);
        setTags(tagResponse.items);
      } catch (error) {
        if (error instanceof ApiError) {
          setErrorMessage(error.message);
        } else {
          setErrorMessage("게시글 목록을 불러오지 못했습니다.");
        }
      } finally {
        setIsLoading(false);
      }
    }

    void loadPosts();
  }, [keyword, page, tag]);

  function updateFilters(next: {
    page?: number;
    keyword?: string;
    tag?: string;
  }) {
    const params = new URLSearchParams(searchParams);
    const nextPage = next.page ?? 1;

    params.set("page", String(nextPage));

    if (next.keyword !== undefined) {
      if (next.keyword.trim()) {
        params.set("keyword", next.keyword.trim());
      } else {
        params.delete("keyword");
      }
    }

    if (next.tag !== undefined) {
      if (next.tag) {
        params.set("tag", next.tag);
      } else {
        params.delete("tag");
      }
    }

    setSearchParams(params);
  }

  function handleSearch(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    updateFilters({ keyword: keywordInput, page: 1 });
  }

  return (
    <section className="panel posts-panel">
      <div className="page-heading">
        <div>
          <p className="eyebrow">Board</p>
          <h1>게시글 목록</h1>
          <p className="section-copy">
            질문을 찾고, 태그로 좁히고, 필요한 글을 빠르게 확인한다.
          </p>
        </div>
        <Link className="primary-link" to="/posts/new">
          글쓰기
        </Link>
      </div>

      <form className="toolbar" onSubmit={handleSearch}>
        <label className="field compact-field">
          <span>검색</span>
          <input
            onChange={(event) => setKeywordInput(event.target.value)}
            placeholder="제목 또는 내용"
            type="search"
            value={keywordInput}
          />
        </label>

        <label className="field compact-field">
          <span>태그</span>
          <select
            onChange={(event) =>
              updateFilters({ tag: event.target.value, page: 1 })
            }
            value={tag ?? ""}
          >
            <option value="">전체</option>
            {tags.map((item) => (
              <option key={item.id} value={item.name}>
                {item.name}
              </option>
            ))}
          </select>
        </label>

        <button className="secondary-button" type="submit">
          검색
        </button>
      </form>

      {errorMessage && <p className="form-error">{errorMessage}</p>}

      {isLoading ? (
        <p className="empty-state">게시글을 불러오는 중입니다.</p>
      ) : posts && posts.items.length > 0 ? (
        <div className="post-list">
          {posts.items.map((post) => (
            <Link className="post-row" key={post.id} to={`/posts/${post.id}`}>
              <div className="post-main">
                <h2>{post.title}</h2>
                <p>
                  {post.author.nickname} · 댓글 {post.comment_count}개 ·{" "}
                  {formatDate(post.created_at)}
                </p>
              </div>
              <div className="tag-list" aria-label="게시글 태그">
                {post.tags.map((item) => (
                  <span className="tag-chip" key={item}>
                    {item}
                  </span>
                ))}
              </div>
            </Link>
          ))}
        </div>
      ) : (
        <p className="empty-state">아직 조건에 맞는 게시글이 없습니다.</p>
      )}

      <div className="pagination">
        <button
          className="secondary-button"
          disabled={page <= 1 || isLoading}
          onClick={() => updateFilters({ page: page - 1 })}
          type="button"
        >
          이전
        </button>
        <span>
          {page} / {totalPages}
        </span>
        <button
          className="secondary-button"
          disabled={page >= totalPages || isLoading}
          onClick={() => updateFilters({ page: page + 1 })}
          type="button"
        >
          다음
        </button>
      </div>
    </section>
  );
}

export default PostsPage;
