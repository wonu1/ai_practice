# Database Design v0.1

## 1. 목적

이 문서는 AI 개발 Q&A 게시판의 기본 데이터 구조를 정의한다.
현재 단계에서는 AI 기능보다 기본 게시판 CRUD를 안정적으로 구현하는 데 필요한 테이블을 먼저 설계한다.

현재 범위:

```text
users
posts
comments
tags
post_tags
```

AI 기능용 테이블은 기본 게시판 기능 안정화 뒤 단계적으로 확장한다.
현재는 RAG 기반 유사 게시글 검색을 위해 `post_embeddings` 테이블을 추가했다.

## 2. 기본 관계

```text
users 1:N posts
users 1:N comments
posts 1:N comments
posts N:M tags
```

의미:

- 한 사용자는 여러 게시글을 작성할 수 있다.
- 한 사용자는 여러 댓글을 작성할 수 있다.
- 한 게시글에는 여러 댓글이 달릴 수 있다.
- 한 게시글은 여러 태그를 가질 수 있고, 한 태그는 여러 게시글에 붙을 수 있다.

## 3. 테이블 설계

### 3.1 users

사용자 계정 정보를 저장한다.

| 컬럼 | 타입 | 제약 | 설명 |
|---|---|---|---|
| id | bigint | PK | 사용자 고유 ID |
| email | varchar(255) | unique, not null | 로그인용 이메일 |
| password_hash | varchar(255) | not null | 해싱된 비밀번호 |
| nickname | varchar(50) | unique, not null | 게시판 표시 이름 |
| created_at | timestamp | not null | 생성 시각 |
| updated_at | timestamp | not null | 수정 시각 |

설계 이유:

- 비밀번호 원문은 저장하지 않고, 반드시 해싱된 값만 저장한다.
- email은 로그인 식별자이므로 unique가 필요하다.
- nickname은 게시글과 댓글에 표시되므로 별도 컬럼으로 둔다.

### 3.2 posts

게시글 정보를 저장한다.

| 컬럼 | 타입 | 제약 | 설명 |
|---|---|---|---|
| id | bigint | PK | 게시글 고유 ID |
| user_id | bigint | FK, not null | 작성자 ID |
| title | varchar(200) | not null | 게시글 제목 |
| content | text | not null | 게시글 본문 |
| created_at | timestamp | not null | 생성 시각 |
| updated_at | timestamp | not null | 수정 시각 |

설계 이유:

- user_id로 작성자와 게시글을 연결한다.
- title은 검색과 목록 표시에서 중요하므로 별도 컬럼으로 둔다.
- content는 길이가 길 수 있으므로 text 타입을 사용한다.

### 3.3 comments

댓글 정보를 저장한다.

| 컬럼 | 타입 | 제약 | 설명 |
|---|---|---|---|
| id | bigint | PK | 댓글 고유 ID |
| post_id | bigint | FK, not null | 댓글이 달린 게시글 ID |
| user_id | bigint | FK, not null | 댓글 작성자 ID |
| content | text | not null | 댓글 내용 |
| created_at | timestamp | not null | 생성 시각 |
| updated_at | timestamp | not null | 수정 시각 |

설계 이유:

- post_id로 어떤 게시글의 댓글인지 연결한다.
- user_id로 댓글 작성자를 연결한다.
- 댓글 수정 기능을 나중에 추가할 수 있도록 updated_at을 둔다.

### 3.4 tags

태그 정보를 저장한다.

| 컬럼 | 타입 | 제약 | 설명 |
|---|---|---|---|
| id | bigint | PK | 태그 고유 ID |
| name | varchar(50) | unique, not null | 태그 이름 |
| created_at | timestamp | not null | 생성 시각 |

설계 이유:

- 같은 이름의 태그가 중복 생성되지 않도록 name에 unique를 둔다.
- 예: react, fastapi, postgres, rag, mcp, agent

### 3.5 post_tags

게시글과 태그의 다대다 관계를 저장한다.

| 컬럼 | 타입 | 제약 | 설명 |
|---|---|---|---|
| post_id | bigint | PK, FK | 게시글 ID |
| tag_id | bigint | PK, FK | 태그 ID |

설계 이유:

- 게시글 하나에 태그 여러 개가 붙을 수 있다.
- 태그 하나도 여러 게시글에 붙을 수 있다.
- 두 컬럼을 복합 기본키로 사용해 같은 게시글에 같은 태그가 중복 연결되지 않게 한다.

## 4. 삭제 정책 초안

현재는 단순한 정책으로 시작한다.

| 삭제 대상 | 정책 |
|---|---|
| 사용자 삭제 | 초기 버전에서는 지원하지 않는다. |
| 게시글 삭제 | 게시글 삭제 시 댓글과 post_tags도 함께 삭제한다. |
| 댓글 삭제 | 댓글만 삭제한다. |
| 태그 삭제 | 초기 버전에서는 직접 삭제 기능을 제공하지 않는다. |

게시글 삭제 시 관련 데이터:

```text
posts 삭제
→ comments 삭제
→ post_tags 삭제
```

## 5. 검색과 페이징 고려

초기 검색 대상:

```text
posts.title
posts.content
tags.name
```

초기 정렬 기준:

```text
created_at desc
```

초기 페이징 파라미터:

```text
page
size
```

예:

```text
GET /posts?page=1&size=10&keyword=fastapi&tag=rag
```

## 6. AI 기능 확장 테이블

기본 CRUD가 안정화된 뒤 RAG, MCP, Agent 기능을 위해 아래 테이블을 단계적으로 추가한다.

### 6.1 post_embeddings

게시글 임베딩을 저장한다.

| 컬럼 | 타입 | 제약 | 설명 |
|---|---|---|---|
| id | bigint | PK | 임베딩 고유 ID |
| post_id | bigint | FK, unique, not null | 임베딩 대상 게시글 ID |
| embedding_model | varchar(100) | not null | 임베딩 생성에 사용한 모델명 |
| source_text | text | not null | 임베딩에 사용한 원본 조합 텍스트 |
| embedding | vector(1536) | not null | OpenAI `text-embedding-3-small` 결과 벡터 |
| created_at | timestamp | not null | 생성 시각 |
| updated_at | timestamp | not null | 수정 시각 |

사용 목적:

- RAG 기반 유사 게시글 검색
- 중복 질문 감지
- 게시글 추천

설계 이유:

- 게시글 하나당 현재 임베딩 하나를 저장하므로 `post_id`에 unique 제약을 둔다.
- 게시글 삭제 시 임베딩도 함께 삭제되도록 `posts.id`에 `ON DELETE CASCADE`로 연결한다.
- 검색 품질 분석과 모델 교체를 위해 `embedding_model`과 `source_text`를 함께 저장한다.
- `text-embedding-3-small`의 기본 차원에 맞춰 `vector(1536)`을 사용한다.
- cosine distance 검색을 빠르게 하기 위해 HNSW 인덱스를 사용한다.

### 6.2 ai_logs

AI 기능 호출 기록을 저장한다.

```text
id
user_id
action_type
input
output
created_at
```

사용 목적:

- AI 질문 개선 요청 기록
- 요약 요청 기록
- Agent 실행 결과 추적

### 6.3 mcp_tool_logs

MCP tool 호출 기록을 저장한다.

```text
id
user_id
tool_name
arguments
result
status
created_at
```

사용 목적:

- GitHub 검색 tool 호출 추적
- 외부 API 실패 원인 확인
- Agent가 어떤 도구를 사용했는지 설명 가능하게 하기

## 7. 현재 설계에서 보류한 것

아래 기능은 초기 CRUD 이후 다시 검토한다.

```text
관리자 권한
게시글 좋아요
북마크
조회수
첨부파일
대댓글
소프트 삭제
신고/모더레이션
알림
```

보류 이유:

- 초기 범위가 커지는 것을 막기 위해서다.
- 기본 게시판 흐름을 먼저 완성해야 RAG, MCP, Agent를 안정적으로 붙일 수 있다.

## 8. 다음 단계

이 DB 설계를 기준으로 다음 문서를 작성한다.

```text
API_DESIGN.md
```

다음 설계 대상:

```text
인증 API
게시글 API
댓글 API
태그 API
검색/페이징 API
AI API 자리
```
