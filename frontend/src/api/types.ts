export type UserSummary = {
  id: number;
  nickname: string;
};

export type User = {
  id: number;
  email: string;
  nickname: string;
  created_at: string;
};

export type TokenResponse = {
  access_token: string;
  token_type: "bearer";
};

export type Tag = {
  id: number;
  name: string;
};

export type PostListItem = {
  id: number;
  title: string;
  author: UserSummary;
  tags: string[];
  comment_count: number;
  created_at: string;
  updated_at: string;
};

export type Post = {
  id: number;
  title: string;
  content: string;
  author: UserSummary;
  tags: string[];
  created_at: string;
  updated_at: string;
};

export type PostListResponse = {
  items: PostListItem[];
  page: number;
  size: number;
  total: number;
};

export type Comment = {
  id: number;
  content: string;
  author: UserSummary;
  created_at: string;
  updated_at: string;
};

export type CommentListResponse = {
  items: Comment[];
};

export type TagListResponse = {
  items: Tag[];
};

export type SimilarPostItem = {
  post_id: number;
  title: string;
  content_preview: string;
  tag_names: string[];
  similarity: number;
};

export type SimilarPostsResponse = {
  status: string;
  message: string | null;
  summary: string | null;
  items: SimilarPostItem[];
};

export type GitHubIssueItem = {
  title: string;
  url: string;
  repository: string;
  state: string;
  summary: string;
};

export type AgentUsedSource = {
  type: string;
  title: string | null;
  ref: string | number | null;
};

export type AgentControlInfo = {
  step_count: number;
  tool_call_count: number;
  errors: string[];
  stopped: boolean;
  stop_reason: string | null;
};

export type AgentAssistWritingResponse = {
  status: string;
  message: string | null;
  feedback: string[];
  draft: string;
  similar_posts: SimilarPostItem[];
  external_refs: GitHubIssueItem[];
  used_sources: AgentUsedSource[];
  control: AgentControlInfo;
};

export type ApiErrorBody = {
  detail?: string;
};
