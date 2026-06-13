import { useParams } from "react-router-dom";

function PostEditorPage() {
  const { postId } = useParams();
  const isEditMode = Boolean(postId);

  return (
    <section className="panel">
      <p className="eyebrow">Editor</p>
      <h1>{isEditMode ? "게시글 수정" : "게시글 작성"}</h1>
      <p>제목, 본문, 태그 입력 폼을 배치할 화면이다.</p>
    </section>
  );
}

export default PostEditorPage;
