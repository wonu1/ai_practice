# API Design v0.1

## 1. 목적

이 문서는 AI 개발 Q&A 게시판의 REST API 초안을 정의한다.
현재 단계에서는 기본 게시판 CRUD를 구현하기 위한 API를 먼저 설계하고, AI 기능 API는 자리를 잡아두는 수준으로 정리한다.

기본 원칙:

```text
자원은 URL로 표현한다.
행동은 HTTP method로 표현한다.
요청과 응답은 JSON을 사용한다.
권한 검사는 백엔드에서 수행한다.
```

## 2. 공통 규칙

### 2.1 Base URL

로컬 개발 기준:

```text
http://localhost:8000
```

API prefix:

```text
/api
```

예:

```text
GET /api/posts
```

### 2.2 인증 방식

초기 설계는 JWT access token을 사용한다.

인증이 필요한 요청은 아래 헤더를 포함한다.

```http
Authorization: Bearer <access_token>
```

### 2.3 공통 에러 응답

```json
{
  "detail": "에러 메시지"
}
```

### 2.4 상태 코드

| 상태 코드 | 의미 | 사용 예 |
|---|---|---|
| 200 | 성공 | 조회, 수정 성공 |
| 201 | 생성 성공 | 회원가입, 게시글 작성, 댓글 작성 |
| 204 | 성공, 응답 본문 없음 | 삭제 성공 |
| 400 | 잘못된 요청 | 입력값 누락, 형식 오류 |
| 401 | 인증 필요 | 로그인하지 않은 요청 |
| 403 | 권한 없음 | 다른 사용자의 글 수정/삭제 |
| 404 | 리소스 없음 | 존재하지 않는 게시글/댓글 |
| 409 | 충돌 | 이미 존재하는 이메일/닉네임 |
| 500 | 서버 오류 | 예상하지 못한 서버 오류 |

## 3. 인증 API

### 3.1 회원가입

```text
POST /api/auth/signup
```

요청:

```json
{
  "email": "user@example.com",
  "password": "password1234",
  "nickname": "wonu"
}
```

응답:

```json
{
  "id": 1,
  "email": "user@example.com",
  "nickname": "wonu",
  "created_at": "2026-06-07T13:00:00Z"
}
```

실패:

| 상태 코드 | 이유 |
|---|---|
| 400 | email, password, nickname 형식 오류 |
| 409 | 이미 존재하는 email 또는 nickname |

### 3.2 로그인

```text
POST /api/auth/login
```

요청:

```json
{
  "email": "user@example.com",
  "password": "password1234"
}
```

응답:

```json
{
  "access_token": "jwt-token",
  "token_type": "bearer"
}
```

실패:

| 상태 코드 | 이유 |
|---|---|
| 400 | 입력값 누락 |
| 401 | 이메일 또는 비밀번호 불일치 |

### 3.3 내 정보 조회

```text
GET /api/auth/me
```

인증:

```text
필요
```

응답:

```json
{
  "id": 1,
  "email": "user@example.com",
  "nickname": "wonu",
  "created_at": "2026-06-07T13:00:00Z"
}
```

실패:

| 상태 코드 | 이유 |
|---|---|
| 401 | 인증 토큰 없음 또는 유효하지 않음 |

## 4. 게시글 API

### 4.1 게시글 목록 조회

```text
GET /api/posts
```

Query parameters:

| 이름 | 타입 | 필수 | 기본값 | 설명 |
|---|---|---|---|---|
| page | int | no | 1 | 페이지 번호 |
| size | int | no | 10 | 페이지 크기 |
| keyword | string | no | null | 제목/내용 검색어 |
| tag | string | no | null | 태그 필터 |

예:

```text
GET /api/posts?page=1&size=10&keyword=fastapi&tag=rag
```

응답:

```json
{
  "items": [
    {
      "id": 1,
      "title": "FastAPI CORS 에러 질문",
      "author": {
        "id": 1,
        "nickname": "wonu"
      },
      "tags": ["fastapi", "cors"],
      "comment_count": 2,
      "created_at": "2026-06-07T13:00:00Z",
      "updated_at": "2026-06-07T13:00:00Z"
    }
  ],
  "page": 1,
  "size": 10,
  "total": 1
}
```

### 4.2 게시글 상세 조회

```text
GET /api/posts/{post_id}
```

응답:

```json
{
  "id": 1,
  "title": "FastAPI CORS 에러 질문",
  "content": "React에서 FastAPI API를 호출할 때 CORS 에러가 납니다.",
  "author": {
    "id": 1,
    "nickname": "wonu"
  },
  "tags": ["fastapi", "cors"],
  "created_at": "2026-06-07T13:00:00Z",
  "updated_at": "2026-06-07T13:00:00Z"
}
```

실패:

| 상태 코드 | 이유 |
|---|---|
| 404 | 게시글 없음 |

### 4.3 게시글 작성

```text
POST /api/posts
```

인증:

```text
필요
```

요청:

```json
{
  "title": "FastAPI CORS 에러 질문",
  "content": "React에서 FastAPI API를 호출할 때 CORS 에러가 납니다.",
  "tags": ["fastapi", "cors"]
}
```

응답:

```json
{
  "id": 1,
  "title": "FastAPI CORS 에러 질문",
  "content": "React에서 FastAPI API를 호출할 때 CORS 에러가 납니다.",
  "author": {
    "id": 1,
    "nickname": "wonu"
  },
  "tags": ["fastapi", "cors"],
  "created_at": "2026-06-07T13:00:00Z",
  "updated_at": "2026-06-07T13:00:00Z"
}
```

실패:

| 상태 코드 | 이유 |
|---|---|
| 400 | 제목 또는 내용이 비어 있음 |
| 401 | 로그인 필요 |

### 4.4 게시글 수정

```text
PATCH /api/posts/{post_id}
```

인증:

```text
필요
```

요청:

```json
{
  "title": "수정된 제목",
  "content": "수정된 내용",
  "tags": ["fastapi", "react"]
}
```

응답:

```json
{
  "id": 1,
  "title": "수정된 제목",
  "content": "수정된 내용",
  "author": {
    "id": 1,
    "nickname": "wonu"
  },
  "tags": ["fastapi", "react"],
  "created_at": "2026-06-07T13:00:00Z",
  "updated_at": "2026-06-07T14:00:00Z"
}
```

실패:

| 상태 코드 | 이유 |
|---|---|
| 400 | 입력값 오류 |
| 401 | 로그인 필요 |
| 403 | 작성자가 아님 |
| 404 | 게시글 없음 |

### 4.5 게시글 삭제

```text
DELETE /api/posts/{post_id}
```

인증:

```text
필요
```

응답:

```text
204 No Content
```

실패:

| 상태 코드 | 이유 |
|---|---|
| 401 | 로그인 필요 |
| 403 | 작성자가 아님 |
| 404 | 게시글 없음 |

## 5. 댓글 API

### 5.1 댓글 목록 조회

```text
GET /api/posts/{post_id}/comments
```

응답:

```json
{
  "items": [
    {
      "id": 1,
      "content": "CORS middleware 설정을 확인해보세요.",
      "author": {
        "id": 2,
        "nickname": "helper"
      },
      "created_at": "2026-06-07T13:30:00Z",
      "updated_at": "2026-06-07T13:30:00Z"
    }
  ]
}
```

### 5.2 댓글 작성

```text
POST /api/posts/{post_id}/comments
```

인증:

```text
필요
```

요청:

```json
{
  "content": "CORS middleware 설정을 확인해보세요."
}
```

응답:

```json
{
  "id": 1,
  "content": "CORS middleware 설정을 확인해보세요.",
  "author": {
    "id": 2,
    "nickname": "helper"
  },
  "created_at": "2026-06-07T13:30:00Z",
  "updated_at": "2026-06-07T13:30:00Z"
}
```

실패:

| 상태 코드 | 이유 |
|---|---|
| 400 | 댓글 내용이 비어 있음 |
| 401 | 로그인 필요 |
| 404 | 게시글 없음 |

### 5.3 댓글 삭제

```text
DELETE /api/comments/{comment_id}
```

인증:

```text
필요
```

응답:

```text
204 No Content
```

실패:

| 상태 코드 | 이유 |
|---|---|
| 401 | 로그인 필요 |
| 403 | 댓글 작성자가 아님 |
| 404 | 댓글 없음 |

## 6. 태그 API

### 6.1 태그 목록 조회

```text
GET /api/tags
```

응답:

```json
{
  "items": [
    {
      "id": 1,
      "name": "fastapi"
    },
    {
      "id": 2,
      "name": "react"
    }
  ]
}
```

태그 생성 정책:

```text
초기 버전에서는 게시글 작성/수정 시 전달된 태그 이름이 없으면 자동 생성한다.
```

## 7. AI API 자리

AI 기능은 기본 CRUD 안정화 후 구현한다.
현재는 API 자리만 잡아둔다.

### 7.1 유사 게시글 추천

```text
POST /api/ai/posts/similar
```

요청:

```json
{
  "title": "FastAPI CORS 에러 질문",
  "content": "React에서 API 호출 시 CORS 에러가 납니다."
}
```

응답 초안:

```json
{
  "items": [
    {
      "post_id": 3,
      "title": "FastAPI CORS 설정 문제",
      "summary": "이 글에서는 CORSMiddleware 설정 누락을 해결했습니다.",
      "score": 0.87
    }
  ]
}
```

### 7.2 게시글 요약

```text
POST /api/ai/posts/{post_id}/summary
```

응답 초안:

```json
{
  "post_id": 1,
  "summary": "이 게시글은 React와 FastAPI 사이의 CORS 에러 해결 방법을 질문합니다."
}
```

### 7.3 글 작성 도움 Agent

```text
POST /api/ai/agent/assist-writing
```

요청:

```json
{
  "title": "FastAPI CORS 에러 질문",
  "content": "React에서 API 호출 시 CORS 에러가 납니다.",
  "tags": ["fastapi", "react"]
}
```

응답 초안:

```json
{
  "similar_posts": [],
  "external_references": [],
  "question_feedback": [
    "에러 메시지를 추가하면 답변 정확도가 올라갑니다.",
    "프론트 요청 주소와 백엔드 CORS 설정을 함께 적어주세요."
  ],
  "draft_answer": null
}
```

## 8. MCP 연동 위치

MCP Server는 일반 REST API와 별도로 구현한다.

예상 tool:

```text
github_search_issues
```

예상 흐름:

```text
React
→ POST /api/ai/agent/assist-writing
→ FastAPI Agent
→ MCP Client
→ GitHub MCP Server
→ GitHub API
```

MCP 호출 결과는 Agent 응답의 `external_references`에 포함한다.

## 9. 다음 단계

이 API 설계를 기준으로 다음 구현을 시작한다.

1차 구현 범위:

```text
로그인 없이 게시글 목록, 상세, 작성 API 구현
```

그 다음 구현 범위:

```text
댓글
태그
검색
페이징
회원가입/로그인
권한
```
