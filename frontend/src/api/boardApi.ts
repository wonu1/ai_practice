import { apiRequest } from "./client";
import type {
  Comment,
  CommentListResponse,
  Post,
  PostListResponse,
  TagListResponse,
  TokenResponse,
  User,
} from "./types";

export type SignupPayload = {
  email: string;
  nickname: string;
  password: string;
};

export type LoginPayload = {
  email: string;
  password: string;
};

export type PostPayload = {
  title: string;
  content: string;
  tags: string[];
};

export type PostListParams = {
  page?: number;
  size?: number;
  keyword?: string;
  tag?: string;
};

export function signup(payload: SignupPayload) {
  return apiRequest<User>("/auth/signup", {
    method: "POST",
    body: payload,
  });
}

export function login(payload: LoginPayload) {
  return apiRequest<TokenResponse>("/auth/login", {
    method: "POST",
    body: payload,
  });
}

export function getMe(token: string) {
  return apiRequest<User>("/auth/me", { token });
}

export function getPosts(params: PostListParams = {}) {
  return apiRequest<PostListResponse>("/posts", { query: params });
}

export function getPost(postId: number) {
  return apiRequest<Post>(`/posts/${postId}`);
}

export function createPost(payload: PostPayload, token: string) {
  return apiRequest<Post>("/posts", {
    method: "POST",
    body: payload,
    token,
  });
}

export function updatePost(
  postId: number,
  payload: Partial<PostPayload>,
  token: string,
) {
  return apiRequest<Post>(`/posts/${postId}`, {
    method: "PATCH",
    body: payload,
    token,
  });
}

export function deletePost(postId: number, token: string) {
  return apiRequest<void>(`/posts/${postId}`, {
    method: "DELETE",
    token,
  });
}

export function getComments(postId: number) {
  return apiRequest<CommentListResponse>(`/posts/${postId}/comments`);
}

export function createComment(postId: number, content: string, token: string) {
  return apiRequest<Comment>(`/posts/${postId}/comments`, {
    method: "POST",
    body: { content },
    token,
  });
}

export function deleteComment(commentId: number, token: string) {
  return apiRequest<void>(`/comments/${commentId}`, {
    method: "DELETE",
    token,
  });
}

export function getTags() {
  return apiRequest<TagListResponse>("/tags");
}
