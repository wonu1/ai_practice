# AI 게시판 개발 로드맵

## 0. 프로젝트 기준

이 문서는 AI 응용 기술을 활용한 게시판 과제를 구현하기 위한 기준 문서다.
중간에 다른 아이디어가 나오더라도, 다시 이 문서로 돌아와 전체 흐름과 현재 위치를 확인한다.

프로젝트 기본 방향:

- 주제: AI 개발 Q&A 게시판
- 핵심 설명: 사용자가 개발 질문을 작성하면, 과거 게시글 기반 RAG로 유사 질문을 추천하고, MCP로 외부 개발 정보를 조회하며, Agent가 질문 개선과 답변 초안을 돕는 게시판
- 프론트엔드: React
- 백엔드 후보: FastAPI 우선
- 데이터베이스: PostgreSQL
- AI 기능: RAG, MCP, AI Agent
- 개발 방식: AI가 코드를 생성하고, 사용자가 붙여 실행하며 흐름을 이해하는 방식

## 1. 핵심 원칙

1. 한 번에 전체 앱을 만들지 않는다.
2. 기능을 작은 단위로 쪼개서 구현한다.
3. 각 기능마다 요청, 응답, 데이터 저장 위치를 확인한다.
4. AI가 만든 코드는 반드시 실행하고 이해한 뒤 다음 단계로 간다.
5. 기본 게시판을 먼저 완성하고, 그 위에 RAG, MCP, Agent를 붙인다.
6. 과제 설명을 위해 구현 이유와 구조를 문서로 남긴다.

## 2. AI 협업 개발 루프

각 기능은 아래 루프를 반복한다.

```text
1. 이 기능이 왜 필요한지 한 문장으로 정의
2. 요청/응답 또는 화면 흐름 작성
3. AI에게 해당 기능만 코드 생성 요청
4. 코드 붙이기
5. 실행
6. 에러 확인
7. 수정
8. 내가 코드 역할을 말로 설명
9. 기록 또는 커밋
```

기능마다 확인할 질문:

```text
이 파일은 무슨 역할인가?
이 요청은 어디서 시작해서 어디로 가는가?
데이터는 어디에 저장되거나 어디서 읽히는가?
권한 검사는 어디서 하는가?
실패하면 어떤 응답을 주는가?
```

## 3. 전체 마일스톤

| 마일스톤 | 목표 | 주요 산출물 |
|---|---|---|
| M1 | 기획과 설계 확정 | 요구사항, 화면 목록, DB 초안, API 목록 |
| M2 | 백엔드 기본 구조 | FastAPI, DB 연결, 모델, 기본 CRUD |
| M3 | 프론트 기본 구조 | React 라우팅, API 호출, 게시판 화면 |
| M4 | 인증과 권한 | 회원가입, 로그인, JWT, 작성자 권한 |
| M5 | 게시판 완성도 | 댓글, 태그, 검색, 페이징 |
| M6 | RAG | 임베딩, 벡터 검색, 유사 게시글 추천 |
| M7 | MCP | 외부 서비스 MCP Server, tool 호출 |
| M8 | Agent | LangGraph 또는 유사 구조, 도구 선택 흐름 |
| M9 | 테스트와 보안 | 단위/통합/수동 테스트, 권한 점검 |
| M10 | 배포와 문서화 | 배포 URL, README, 발표 시나리오 |

## 4. 상세 개발 단계

### 4.0 진행 상태 체크

이 표는 현재 실제 산출물 기준의 진행 상태를 표시한다.

| 단계 | 상태 | 근거 |
|---:|---|---|
| 1 | [x] 완료 | `PROJECT_DECISIONS.md`에 프로젝트 주제와 핵심 설명 작성 |
| 2 | [~] 보강 필요 | 비회원/회원/관리자 역할은 언급했지만 별도 사용자 역할 문서 필요 |
| 3 | [x] 완료 | `PROJECT_DECISIONS.md`, `API_DESIGN.md`에 필수 기능 범위 작성 |
| 4 | [x] 완료 | RAG, MCP, Agent 기능 자리를 `PROJECT_DECISIONS.md`에 정리 |
| 5 | [x] 완료 | React, FastAPI, PostgreSQL 선택을 `PROJECT_DECISIONS.md`에 정리 |
| 6 | [x] 완료 | `ARCHITECTURE.md`에 React, FastAPI, PostgreSQL, RAG, MCP, Agent 구조 작성 |
| 7 | [x] 완료 | `SCREEN_FLOW.md`에 화면 목록 작성 |
| 8 | [x] 완료 | `SCREEN_FLOW.md`에 사용자 흐름 작성 |
| 9 | [x] 완료 | `DATABASE_DESIGN.md`에 기본 DB 테이블 설계 작성 |
| 10 | [x] 완료 | `DATABASE_DESIGN.md`에 AI 확장 예정 테이블 작성 |
| 11 | [x] 완료 | `API_DESIGN.md`에 auth, posts, comments, tags, ai API 목록 작성 |
| 12 | [x] 완료 | `API_DESIGN.md`, `PROJECT_DECISIONS.md`에 JWT 인증 방식 작성 |
| 13 | [x] 완료 | `DATABASE_DESIGN.md`, `API_DESIGN.md`에 권한 규칙 작성 |
| 14 | [x] 완료 | `API_DESIGN.md`에 공통 에러와 상태 코드 규칙 작성 |
| 15 | [~] 진행 중 | `backend/`, `.gitignore` 생성. 전체 frontend/mcp-server 구조는 아직 미정 |
| 16 | [x] 완료 | FastAPI 백엔드 골격 생성 및 `/health`, `/docs` 실행 확인 |
| 17 | [ ] 미완료 | React 프론트 프로젝트 미생성 |
| 18 | [x] 완료 | Docker Compose로 PostgreSQL 컨테이너 실행 확인 |
| 19 | [x] 완료 | `backend/.env.example` 작성 및 로컬 `backend/.env`로 DB 접속 정보 구성 |
| 20 | [x] 완료 | SQLAlchemy engine/session 구성 및 PostgreSQL 연결 확인 |
| 21 | [x] 완료 | Alembic 설정 파일과 `backend/migrations` 구조 생성 |
| 22 | [x] 완료 | `users` 테이블 구조를 SQLAlchemy User 모델로 구현 |
| 23 | [x] 완료 | `posts` 테이블 구조와 User-Post 관계를 SQLAlchemy 모델로 구현 |
| 24 | [x] 완료 | `comments` 테이블 구조와 User-Comment, Post-Comment 관계를 SQLAlchemy 모델로 구현 |
| 25 | [x] 완료 | `tags`, `post_tags` 테이블 구조와 Post-Tag 다대다 관계를 SQLAlchemy 모델로 구현 |
| 26 | [x] 완료 | 인증, 사용자, 게시글, 댓글, 태그 API 요청/응답용 Pydantic 스키마 구현 |
| 27 | [x] 완료 | bcrypt 기반 비밀번호 해싱/검증 유틸리티 구현 |
| 28 | [x] 완료 | 이메일/닉네임 중복 검사와 비밀번호 해싱을 포함한 회원가입 API 구현 |
| 29 | [x] 완료 | 이메일/비밀번호 검증과 JWT access token 발급을 포함한 로그인 API 구현 |
| 30 | [x] 완료 | JWT Bearer 토큰으로 현재 로그인 사용자를 반환하는 내 정보 API 구현 |
| 31 | [x] 완료 | Authorization 헤더의 JWT를 검증해 현재 사용자를 추출하는 인증 의존성 구현 |
| 32 | [x] 완료 | 페이지네이션, 키워드 검색, 태그 필터, 댓글 수를 포함한 게시글 목록 API 구현 |
| 33 | [x] 완료 | 게시글 ID로 본문, 작성자, 태그를 조회하고 없으면 404를 반환하는 상세 API 구현 |
| 34 | [x] 완료 | 인증된 사용자가 제목, 본문, 태그를 입력해 게시글을 생성하는 API 구현 |
| 35 | [x] 완료 | 작성자 본인만 제목, 본문, 태그를 부분 수정할 수 있는 게시글 수정 API 구현 |
| 36 | [x] 완료 | 작성자 본인만 게시글을 삭제하고 성공 시 204를 반환하는 게시글 삭제 API 구현 |
| 37 | [x] 완료 | 게시글 수정/삭제 API에서 작성자 본인 여부를 검사하고 403을 반환하도록 처리 |
| 38 | [x] 완료 | 게시글별 댓글을 작성자 정보와 함께 생성순으로 조회하는 댓글 목록 API 구현 |
| 39 | [x] 완료 | 인증된 사용자가 존재하는 게시글에 댓글을 작성하고 작성자 정보와 함께 응답하는 API 구현 |
| 40 | [x] 완료 | 댓글 작성자 본인만 댓글을 삭제하고 성공 시 204를 반환하는 댓글 삭제 API 구현 |
| 41 | [x] 완료 | 댓글 삭제 API에서 작성자 본인 여부를 검사하고 403을 반환하도록 처리 |
| 42 | [x] 완료 | 게시글 작성/수정의 태그 자동 생성 및 이름순 태그 목록 조회 API 구현 |
| 43 | [x] 완료 | 게시글 목록 API에서 제목/내용 키워드 검색과 태그 필터 구현 |
| 44 | [x] 완료 | 게시글 목록 API에서 page, size, total 기반 페이징 응답 구현 |
| 45 | [x] 완료 | 로컬 React 개발 서버가 FastAPI를 호출할 수 있도록 제한된 CORS 허용 목록 설정 |
| 46 | [x] 완료 | auth, posts, comments, tags 주요 API 흐름을 자동 smoke test로 검증 |
| 47 | [x] 완료 | Vite React 프로젝트 생성 및 React Router 기반 주요 화면 경로 설정 |
| 48 | [x] 완료 | `frontend/src/api/client.ts`, `frontend/src/api/boardApi.ts`에 fetch 기반 API 호출 통로 구현 |
| 49 | [x] 완료 | `localStorage` 기반 JWT 저장소와 React AuthProvider로 로그인 상태 관리 구조 구현 |
| 50 | [x] 완료 | 로그인 폼에서 FastAPI 로그인 API를 호출하고 성공 시 JWT를 저장하도록 구현 |
| 51 | [x] 완료 | 회원가입 폼에서 FastAPI 회원가입 API를 호출하고 성공 시 로그인 화면으로 이동하도록 구현 |
| 52 | [x] 완료 | 게시글 목록 화면에서 목록 조회, 키워드 검색, 태그 필터, 페이지 이동 UI를 FastAPI API와 연결 |
| 53 | [x] 완료 | 게시글 상세 화면에서 본문, 태그, 댓글 목록을 조회하고 작성자 수정/삭제 버튼을 연결 |

다음 정석 진행은 DB 모델과 마이그레이션 파일을 작성해 실제 테이블 구조를 만드는 것이다.

| 단계 | 작업 | 해야 할 일 | 산출물 |
|---:|---|---|---|
| 1 | 프로젝트 목표 정의 | 어떤 게시판인지 한 문장으로 정리 | 프로젝트 한 줄 설명 |
| 2 | 핵심 사용자 정의 | 비회원, 회원, 관리자 역할 정의 | 사용자 역할 목록 |
| 3 | 필수 기능 정리 | 과제 필수 기능 체크 | 기능 목록 |
| 4 | AI 기능 범위 정리 | RAG, MCP, Agent 각각 어떤 기능으로 넣을지 결정 | AI 기능 목록 |
| 5 | 기술 스택 결정 | React, FastAPI, PostgreSQL 등 선택 이유 작성 | 기술 스택 표 |
| 6 | 전체 아키텍처 작성 | React, Backend, DB, AI, MCP 흐름 그리기 | 아키텍처 다이어그램 |
| 7 | 화면 목록 작성 | 로그인, 회원가입, 글 목록, 글 상세, 글 작성, 수정 화면 | 화면 목록 |
| 8 | 사용자 흐름 작성 | 가입부터 글 작성, AI 도움, 댓글까지 흐름 작성 | 사용자 시나리오 |
| 9 | 기본 DB 테이블 설계 | users, posts, comments, tags, post_tags 작성 | DB 설계 초안 |
| 10 | AI용 DB 테이블 설계 | embeddings, ai_logs, mcp_tool_logs 작성 | AI DB 설계 초안 |
| 11 | API 목록 작성 | auth, posts, comments, tags, ai API 목록화 | API 명세 초안 |
| 12 | 인증 방식 결정 | JWT access token 방식으로 갈지 결정 | 인증 설계 |
| 13 | 권한 규칙 작성 | 작성자만 수정/삭제, 비회원은 조회만 가능 등 | 권한 규칙 |
| 14 | 에러 규칙 작성 | 400, 401, 403, 404, 500 사용 기준 정리 | 에러 응답 규칙 |
| 15 | 저장소 구조 결정 | frontend, backend, mcp-server 등 폴더 구조 결정 | 프로젝트 구조 |
| 16 | 백엔드 프로젝트 생성 | FastAPI 프로젝트 생성 | backend 폴더 |
| 17 | 프론트 프로젝트 생성 | React 프로젝트 생성 | frontend 폴더 |
| 18 | PostgreSQL 준비 | 로컬, Docker, 또는 클라우드 DB 결정 | DB 실행 환경 |
| 19 | 백엔드 환경변수 설정 | DB URL, JWT secret 등 .env 구성 | .env.example |
| 20 | 백엔드 DB 연결 | SQLAlchemy engine/session 구성 | DB 연결 코드 |
| 21 | 마이그레이션 설정 | Alembic 설정 | migrations |
| 22 | User 모델 구현 | users 테이블 모델 작성 | User model |
| 23 | Post 모델 구현 | posts 테이블 모델 작성 | Post model |
| 24 | Comment 모델 구현 | comments 테이블 모델 작성 | Comment model |
| 25 | Tag 모델 구현 | tags, post_tags 모델 작성 | Tag model |
| 26 | Pydantic 스키마 작성 | 요청/응답 DTO 작성 | schemas |
| 27 | 비밀번호 해싱 구현 | bcrypt 또는 passlib 설정 | password utility |
| 28 | 회원가입 API 구현 | POST /auth/signup | signup API |
| 29 | 로그인 API 구현 | POST /auth/login | login API |
| 30 | 내 정보 API 구현 | GET /auth/me | me API |
| 31 | 인증 의존성 구현 | 현재 사용자 추출 함수 작성 | auth dependency |
| 32 | 게시글 목록 API 구현 | GET /posts, page/size 기본 포함 | posts list API |
| 33 | 게시글 상세 API 구현 | GET /posts/{post_id} | post detail API |
| 34 | 게시글 작성 API 구현 | POST /posts | create post API |
| 35 | 게시글 수정 API 구현 | PATCH /posts/{post_id} | update post API |
| 36 | 게시글 삭제 API 구현 | DELETE /posts/{post_id} | delete post API |
| 37 | 게시글 권한 검사 | 작성자만 수정/삭제 가능하게 처리 | post permission |
| 38 | 댓글 목록 API 구현 | GET /posts/{post_id}/comments | comment list API |
| 39 | 댓글 작성 API 구현 | POST /posts/{post_id}/comments | create comment API |
| 40 | 댓글 삭제 API 구현 | DELETE /comments/{comment_id} | delete comment API |
| 41 | 댓글 권한 검사 | 작성자 또는 관리자만 삭제 가능 | comment permission |
| 42 | 태그 처리 구현 | 태그 생성, 연결, 조회 | tag API |
| 43 | 검색 구현 | 제목, 내용, 태그 검색 | search API |
| 44 | 페이징 구현 | page, size, total 응답 | pagination |
| 45 | CORS 설정 | React에서 API 호출 가능하게 설정 | CORS config |
| 46 | Swagger로 백엔드 테스트 | auth, posts, comments 수동 테스트 | API 동작 확인 |
| 47 | 프론트 라우팅 설정 | React Router 설정 | routes |
| 48 | API 클라이언트 작성 | fetch 또는 axios wrapper 작성 | api client |
| 49 | 인증 토큰 저장 처리 | 로그인 후 token 저장, 요청 헤더 포함 | auth client |
| 50 | 로그인 화면 구현 | 이메일/비밀번호 입력과 에러 표시 | Login page |
| 51 | 회원가입 화면 구현 | 회원가입 폼과 성공 처리 | Signup page |
| 52 | 글 목록 화면 구현 | 목록, 검색, 태그, 페이징 UI | Posts page |
| 53 | 글 상세 화면 구현 | 본문, 댓글, 수정/삭제 버튼 | Post detail page |
| 54 | 글 작성 화면 구현 | 제목, 내용, 태그 입력 | New post page |
| 55 | 글 수정 화면 구현 | 기존 글 불러와 수정 | Edit post page |
| 56 | 댓글 UI 구현 | 댓글 목록, 작성, 삭제 | Comment UI |
| 57 | 프론트 인증 가드 구현 | 로그인 필요 화면 제어 | route guard |
| 58 | 기본 게시판 수동 테스트 | 가입, 로그인, 글/댓글 CRUD 확인 | 테스트 기록 |
| 59 | OpenAI 또는 LLM 모델 선택 | 사용할 상용 LLM 결정 | LLM 선택 기록 |
| 60 | 임베딩 모델 선택 | 게시글 임베딩 모델 결정 | embedding 선택 |
| 61 | Vector DB 선택 | pgvector 또는 Chroma 선택 | vector store 결정 |
| 62 | 게시글 임베딩 전략 설계 | title + content + tags를 어떻게 임베딩할지 결정 | embedding strategy |
| 63 | 임베딩 저장 구조 구현 | post_embeddings 또는 vector store 저장 | embedding storage |
| 64 | 게시글 생성 시 임베딩 생성 | 글 저장 후 임베딩 생성 처리 | create embedding flow |
| 65 | 게시글 수정 시 임베딩 갱신 | 글 변경 시 임베딩 다시 생성 | update embedding flow |
| 66 | 유사 게시글 검색 함수 구현 | 벡터 유사도 검색 | similarity search |
| 67 | RAG API 구현 | POST /ai/posts/similar | similar posts API |
| 68 | 유사 글 요약 구현 | 검색 결과를 LLM으로 요약 | summary function |
| 69 | 글 작성 화면에 RAG 연결 | 작성 중 유사 글 추천 표시 | RAG UI |
| 70 | RAG 실패 처리 | 임베딩 실패, 검색 결과 없음 처리 | RAG error handling |
| 71 | MCP 외부 서비스 선택 | GitHub API 등 외부 서비스 선택 | MCP 대상 결정 |
| 72 | MCP tool 설계 | github_search_issues 입력/출력 정의 | tool spec |
| 73 | MCP Server 프로젝트 생성 | 별도 mcp-server 폴더 구성 | MCP server folder |
| 74 | MCP Server 기본 실행 구현 | 서버 실행, transport 결정 | runnable MCP server |
| 75 | MCP initialize 처리 확인 | MCP client와 초기 연결 확인 | initialize support |
| 76 | tools/list 구현 | 제공 도구 목록과 input schema 반환 | tools/list |
| 77 | github_search_issues 구현 | GitHub API 호출 코드 작성 | tool implementation |
| 78 | MCP 환경변수 관리 | GitHub token 등 .env 처리 | MCP .env.example |
| 79 | MCP 에러 처리 | 잘못된 입력, rate limit, timeout 처리 | MCP errors |
| 80 | MCP 단독 테스트 | MCP inspector 또는 client로 tool 호출 | MCP test record |
| 81 | 백엔드에서 MCP Client 연결 | AI 백엔드가 MCP server 호출 가능하게 구성 | MCP client code |
| 82 | MCP 호출 로그 저장 | mcp_tool_logs에 호출 결과 저장 | MCP logs |
| 83 | Agent 역할 정의 | 질문 개선, 유사글 검색, 외부자료 조회, 답변초안 | agent responsibility |
| 84 | Agent 상태 설계 | input, rag_results, mcp_results, final_answer | agent state |
| 85 | Agent 도구 정의 | RAG search tool, MCP GitHub tool | agent tools |
| 86 | LangGraph 구조 설계 | 노드와 분기 조건 작성 | graph design |
| 87 | Agent 노드 구현 | analyze, retrieve, external_search, generate | graph nodes |
| 88 | Agent 조건 분기 구현 | 외부 검색 필요 여부 판단 | conditional edges |
| 89 | 무한 루프 방지 | max_steps, timeout, tool call limit | loop guard |
| 90 | Agent API 구현 | POST /ai/agent/assist-writing | agent API |
| 91 | Agent 응답 형식 설계 | similar_posts, external_refs, feedback, draft | response schema |
| 92 | 글 작성 화면에 Agent 연결 | AI 도움받기 버튼과 결과 표시 | Agent UI |
| 93 | AI 로그 저장 | ai_logs에 input/output 저장 | AI logs |
| 94 | 백엔드 단위 테스트 작성 | auth, posts, comments 중심 | unit tests |
| 95 | API 통합 테스트 작성 | 로그인 후 글 작성/수정/삭제 흐름 | integration tests |
| 96 | RAG 테스트 작성 | 유사 글 검색, 결과 없음, LLM 실패 | RAG tests |
| 97 | MCP 테스트 작성 | tool list, tool call, 외부 API 실패 | MCP tests |
| 98 | Agent 테스트 작성 | tool 선택, 루프 제한, 예외 처리 | Agent tests |
| 99 | 프론트 수동 테스트 | 주요 화면과 에러 상태 확인 | frontend test record |
| 100 | 보안 점검 | 비밀번호 해싱, JWT, API Key 노출 방지 | security checklist |
| 101 | 배포 구조 결정 | 프론트, 백엔드, DB, MCP 서버 배포 위치 결정 | deployment plan |
| 102 | 배포 환경변수 정리 | DB URL, JWT secret, OpenAI key, GitHub token | env checklist |
| 103 | DB 배포 | Supabase, Neon, Railway 등 선택 | deployed DB |
| 104 | 백엔드 배포 | Render, Railway, Fly.io 등 | backend URL |
| 105 | MCP Server 배포 | 백엔드와 함께 또는 별도 배포 | MCP server URL |
| 106 | 프론트 배포 | Vercel 등 | frontend URL |
| 107 | 배포 후 전체 테스트 | 실제 URL에서 전체 기능 확인 | production test record |
| 108 | README 작성 | 설치, 실행, 기술스택, 주요 기능 | README |
| 109 | 설계 문서 작성 | 아키텍처, DB, API, AI 구조 | design doc |
| 110 | API 문서 정리 | 주요 API 요청/응답 예시 | API doc |
| 111 | AI 기능 문서 작성 | RAG, MCP, Agent 구현 이유와 흐름 | AI doc |
| 112 | 발표 시나리오 작성 | 시연 순서와 설명 스크립트 | presentation script |
| 113 | 회고 작성 | 어려웠던 점, 개선점, AI 사용 차이 | retrospective |

## 5. 추천 구현 순서 요약

처음부터 113단계를 모두 보며 진행하지 말고 아래 순서로 끊어서 진행한다.

```text
1. 설계 문서 작성
2. FastAPI + PostgreSQL 기본 백엔드
3. React 기본 화면
4. 인증/권한
5. 댓글/태그/검색/페이징
6. RAG
7. MCP
8. Agent
9. 테스트
10. 배포
11. 문서화
```

## 6. 기능별 AI 요청 예시

좋은 요청:

```text
FastAPI에서 posts 모델과 GET /posts, POST /posts API만 만들어줘.
DB는 PostgreSQL이고 SQLAlchemy를 사용해.
각 파일의 역할도 설명해줘.
```

좋지 않은 요청:

```text
React + FastAPI + PostgreSQL + RAG + MCP + Agent 게시판 전체 만들어줘.
```

원칙:

- 한 번에 하나의 기능만 요청한다.
- 생성된 코드는 바로 실행한다.
- 실행 결과와 에러를 확인한다.
- 이해한 뒤 다음 기능으로 넘어간다.

## 7. 현재 추천 1차 목표

가장 먼저 달성할 목표:

```text
React + FastAPI + PostgreSQL로
로그인 없이 게시글 목록, 상세, 작성까지 구현한다.
```

그 다음 목표:

```text
댓글
태그
검색
페이징
회원가입/로그인
권한
RAG
MCP
Agent
```

## 8. 최종 과제 설명 문장

최종 결과물은 아래처럼 설명할 수 있어야 한다.

```text
이 프로젝트는 React와 FastAPI, PostgreSQL로 구현한 AI 개발 Q&A 게시판입니다.
사용자는 기본 게시판 기능을 사용할 수 있고,
게시글 작성 시 RAG를 통해 과거 유사 질문을 추천받습니다.
또한 직접 구현한 MCP Server를 통해 GitHub 같은 외부 서비스를 조회하며,
AI Agent가 RAG와 MCP tool을 선택적으로 사용해 질문 개선과 답변 초안을 제공합니다.
```
