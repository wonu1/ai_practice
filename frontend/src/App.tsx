import { Link, Navigate, Route, Routes } from "react-router-dom";

import LoginPage from "./pages/LoginPage";
import PostDetailPage from "./pages/PostDetailPage";
import PostEditorPage from "./pages/PostEditorPage";
import PostsPage from "./pages/PostsPage";
import SignupPage from "./pages/SignupPage";

function App() {
  return (
    <div className="app-shell">
      <header className="topbar">
        <Link className="brand" to="/posts">
          DevMate Board
        </Link>
        <nav className="nav-links" aria-label="주요 메뉴">
          <Link to="/posts">게시글</Link>
          <Link to="/posts/new">글쓰기</Link>
          <Link to="/login">로그인</Link>
          <Link to="/signup">회원가입</Link>
        </nav>
      </header>

      <main className="page">
        <Routes>
          <Route path="/" element={<Navigate to="/posts" replace />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/signup" element={<SignupPage />} />
          <Route path="/posts" element={<PostsPage />} />
          <Route path="/posts/new" element={<PostEditorPage />} />
          <Route path="/posts/:postId" element={<PostDetailPage />} />
          <Route path="/posts/:postId/edit" element={<PostEditorPage />} />
        </Routes>
      </main>
    </div>
  );
}

export default App;
