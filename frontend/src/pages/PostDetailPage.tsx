import { useParams } from "react-router-dom";

function PostDetailPage() {
  const { postId } = useParams();

  return (
    <section className="panel">
      <p className="eyebrow">Post #{postId}</p>
      <h1>게시글 상세</h1>
      <p>게시글 본문과 댓글을 보여줄 화면이다.</p>
    </section>
  );
}

export default PostDetailPage;
