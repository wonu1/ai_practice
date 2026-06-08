# Architecture v0.1

## 1. 목적

이 문서는 AI 개발 Q&A 게시판의 전체 구조를 설명한다.
구현 중에 지금 작업하는 코드가 프론트엔드, 백엔드, 데이터베이스, AI 기능, MCP Server 중 어디에 속하는지 확인하기 위한 기준 문서다.

## 2. 전체 구조

초기 프로젝트는 아래 구조로 시작한다.

```text
사용자
  ↓
React Frontend
  ↓ REST API
FastAPI Backend
  ↓
PostgreSQL
```

AI 기능이 추가된 뒤의 목표 구조는 아래와 같다.

```text
사용자
  ↓
React Frontend
  ↓ REST API
FastAPI Backend
  ├─ PostgreSQL
  ├─ RAG 기능
  │   ├─ Embedding Model
  │   └─ Vector DB
  ├─ Agent
  │   ├─ RAG 검색 도구 사용
  │   └─ MCP 도구 사용
  └─ MCP Client
      ↓ MCP Protocol
      MCP Server
        ↓
        외부 서비스 API
```

## 3. 각 영역의 역할

### 3.1 React Frontend

사용자와 직접 만나는 화면이다.

담당 역할:

- 로그인/회원가입 화면
- 게시글 목록 화면
- 게시글 상세 화면
- 게시글 작성/수정 화면
- 댓글 UI
- 태그/검색/페이징 UI
- AI 작성 도움 결과 표시

하지 않는 일:

- DB에 직접 접근하지 않는다.
- 비밀번호 검증을 직접 책임지지 않는다.
- 글 수정/삭제 권한을 최종 판단하지 않는다.
- 외부 API Key를 보관하지 않는다.

### 3.2 FastAPI Backend

프론트엔드와 데이터베이스, AI 기능 사이를 연결하는 서버다.

담당 역할:

- REST API 제공
- 요청 데이터 검증
- 인증/권한 검사
- 게시글, 댓글, 태그 CRUD 처리
- PostgreSQL 조회/저장
- RAG 기능 호출
- Agent 실행
- MCP Client를 통해 MCP Server 호출

하지 않는 일:

- 사용자 화면을 직접 그리지 않는다.
- 장기적으로는 외부 서비스 API를 직접 무분별하게 호출하지 않고, MCP Server를 통해 도구화한다.

### 3.3 PostgreSQL

영속 데이터를 저장하는 관계형 데이터베이스다.

담당 데이터:

- 사용자
- 게시글
- 댓글
- 태그
- 게시글-태그 관계
- 이후 AI 로그, MCP 호출 로그, 임베딩 메타데이터

초기에는 기본 게시판 데이터만 저장한다.
AI용 벡터 저장 방식은 기본 CRUD 이후 다시 결정한다.

### 3.4 RAG

게시판 내부 데이터를 LLM 답변에 연결하는 기능이다.

예상 역할:

- 게시글 내용을 임베딩으로 변환
- 유사 게시글 검색
- 중복 질문 감지
- 유사 글 요약
- 질문 작성 중 참고할 기존 글 추천

초기 기능:

```text
사용자가 글을 작성할 때 유사 게시글을 추천한다.
```

### 3.5 MCP Server

외부 서비스를 AI Agent가 사용할 수 있는 도구로 제공하는 별도 서버다.

예상 역할:

- GitHub API 같은 외부 서비스를 MCP tool로 감싼다.
- `tools/list`로 사용 가능한 도구를 알려준다.
- `tools/call`로 도구 실행 요청을 처리한다.
- API Key와 외부 API 실패를 서버 쪽에서 관리한다.

초기 후보 tool:

```text
github_search_issues
```

### 3.6 Agent

사용자 요청을 보고 어떤 도구를 사용할지 판단하는 AI 실행 흐름이다.

예상 역할:

- 질문 내용 분석
- RAG 검색이 필요한지 판단
- MCP 외부 검색이 필요한지 판단
- 유사 게시글과 외부 자료를 바탕으로 질문 개선 제안
- 답변 초안 생성
- 무한 루프 방지
- 예외 처리

초기 기능:

```text
글 작성 도움 Agent
```

## 4. 기본 게시판 요청 흐름

### 4.1 게시글 목록 조회

```text
사용자
→ React에서 글 목록 페이지 접속
→ React가 GET /api/posts 요청
→ FastAPI가 요청 수신
→ FastAPI가 PostgreSQL에서 게시글 목록 조회
→ FastAPI가 JSON 응답 반환
→ React가 목록 화면 렌더링
```

### 4.2 게시글 작성

```text
사용자
→ React에서 제목/내용/태그 입력
→ React가 POST /api/posts 요청
→ FastAPI가 로그인 여부 확인
→ FastAPI가 입력값 검증
→ FastAPI가 PostgreSQL에 게시글 저장
→ FastAPI가 생성된 게시글 JSON 반환
→ React가 상세 화면 또는 목록 화면으로 이동
```

## 5. AI 기능 요청 흐름

### 5.1 RAG 유사 게시글 추천

```text
사용자
→ React에서 글 작성 중 AI 추천 요청
→ React가 POST /api/ai/posts/similar 요청
→ FastAPI가 제목/내용을 임베딩
→ Vector DB에서 유사 게시글 검색
→ FastAPI가 유사 게시글과 요약 반환
→ React가 추천 목록 표시
```

### 5.2 MCP 외부 정보 조회

```text
사용자
→ React에서 AI 작성 도움 요청
→ FastAPI Agent 실행
→ Agent가 외부 정보가 필요하다고 판단
→ FastAPI의 MCP Client가 MCP Server에 tools/call 요청
→ MCP Server가 GitHub API 호출
→ MCP Server가 결과 반환
→ Agent가 결과를 정리
→ FastAPI가 React에 응답
```

### 5.3 Agent 작성 도움

```text
사용자
→ React에서 제목/내용 입력
→ React가 POST /api/ai/agent/assist-writing 요청
→ FastAPI Agent가 질문 분석
→ Agent가 RAG 검색 실행
→ Agent가 필요하면 MCP tool 실행
→ Agent가 질문 개선 제안과 답변 초안 생성
→ React가 결과 표시
```

## 6. 구현 우선순위

현재는 AI 기능을 바로 구현하지 않는다.
먼저 기본 게시판이 안정적으로 동작해야 한다.

우선순위:

```text
1. FastAPI 서버 실행 확인
2. PostgreSQL 연결
3. 게시글 CRUD
4. React 화면 연결
5. 로그인/권한
6. 댓글/태그/검색/페이징
7. RAG
8. MCP
9. Agent
```

## 7. 현재 아키텍처 결정

현재 확정:

```text
Frontend: React
Backend: FastAPI
Database: PostgreSQL
API style: REST API
AI detail stack: 기본 CRUD 이후 결정
```

현재 보류:

```text
Vector DB
Embedding Model
RAG Framework
Agent Framework 세부 구현
MCP 외부 서비스 최종 선택
배포 플랫폼
```

## 8. 다음 단계

다음 설계 문서:

```text
SCREEN_FLOW.md
```

목적:

- 어떤 화면이 필요한지 정리한다.
- 사용자가 어떤 순서로 화면을 이동하는지 정리한다.
- React 구현 전에 화면 단위를 명확히 한다.
