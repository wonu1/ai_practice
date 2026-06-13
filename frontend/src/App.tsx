import { Link, Navigate, Route, Routes } from "react-router-dom";

import LoginPage from "./pages/LoginPage";
import PostDetailPage from "./pages/PostDetailPage";
import PostEditorPage from "./pages/PostEditorPage";
import PostsPage from "./pages/PostsPage";
import SignupPage from "./pages/SignupPage";
import { useAuth } from "./auth/AuthContext";
import RequireAuth from "./auth/RequireAuth";

function App() {
  const { isAuthenticated, logout, user } = useAuth();

  return (
    <div className="app-shell">
      <header className="topbar">
        <Link className="brand" to="/posts">
          DevMate Board
        </Link>
        <nav className="nav-links" aria-label="주요 메뉴">
          <Link to="/posts">게시글</Link>
          <Link to="/posts/new">글쓰기</Link>
          {isAuthenticated ? (
            <button className="nav-button" type="button" onClick={logout}>
              {user?.nickname} 로그아웃
            </button>
          ) : (
            <>
              <Link to="/login">로그인</Link>
              <Link to="/signup">회원가입</Link>
            </>
          )}
        </nav>
      </header>

      <main className="page">
        <Routes>
          <Route path="/" element={<Navigate to="/posts" replace />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/signup" element={<SignupPage />} />
          <Route path="/posts" element={<PostsPage />} />
          <Route
            path="/posts/new"
            element={
              <RequireAuth>
                <PostEditorPage />
              </RequireAuth>
            }
          />
          <Route path="/posts/:postId" element={<PostDetailPage />} />
          <Route
            path="/posts/:postId/edit"
            element={
              <RequireAuth>
                <PostEditorPage />
              </RequireAuth>
            }
          />
        </Routes>
      </main>
    </div>
  );
}

export default App;
