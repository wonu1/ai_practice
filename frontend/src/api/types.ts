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

export type ApiErrorBody = {
  detail?: string;
};
