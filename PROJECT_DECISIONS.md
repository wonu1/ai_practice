# 프로젝트 결정 기록

## 1. 확정된 프로젝트 방향

프로젝트 주제:

```text
AI 개발 Q&A 게시판
```

핵심 설명:

```text
사용자가 개발 질문을 작성하면,
기본 게시판 기능을 통해 질문과 답변을 관리하고,
나중에 RAG로 유사 게시글을 추천하며,
MCP로 외부 개발 정보를 조회하고,
Agent가 질문 개선과 답변 초안을 돕는 게시판을 만든다.
```

## 2. 확정 기술 스택

| 영역 | 선택 | 이유 |
|---|---|---|
| 프론트엔드 | React | 과제 요구사항을 만족하고, 프론트/백 역할 분리를 학습하기 좋다. |
| 백엔드 | FastAPI | API 구조가 선명하고, Python AI 생태계와 연결하기 쉽다. |
| 데이터베이스 | PostgreSQL | 과제 요구사항을 만족하고, 이후 pgvector 같은 확장도 고려할 수 있다. |
| 기본 API 방식 | REST API | 게시판 CRUD와 잘 맞고, 프론트/백 통신 구조를 이해하기 좋다. |
| 인증 방식 | JWT 기반 인증 | React와 API 서버 구조에서 흔히 쓰이고, 인증/권한 흐름을 학습하기 좋다. |

## 3. AI 기술 스택 결정 상태

기본 CRUD 게시판이 수동 테스트까지 통과했으므로 AI 기술 선택 단계로 넘어간다.
다만 AI 관련 세부 기술은 한 번에 모두 확정하지 않고, 영역별로 비교한 뒤 선택한다.

현재 확정하는 것은 LLM Provider, RAG 1차 기능, Vector DB, RAG Framework, 관찰 도구, 교체 가능 설계 원칙이다.

### 3.1 LLM Provider 1차 결정

| 항목 | 결정 | 이유 |
|---|---|---|
| LLM Provider | OpenAI | 현재 사용할 수 있는 OpenAI 크레딧이 있고, FastAPI/Python 환경에서 연동 자료와 SDK가 충분하다. |
| 사용 목적 | RAG 요약, 질문 개선, 답변 초안, Agent 응답 생성 | 게시판의 AI 기능이 언어 이해/생성 중심이기 때문이다. |
| 설계 원칙 | 교체 가능하게 구현 | 나중에 Claude, Gemini, 로컬 모델 등으로 바꿀 수 있도록 백엔드 내부에 얇은 AI 서비스 계층을 둔다. |

모델명은 코드 전체에 직접 흩뿌리지 않고 환경변수나 설정 파일에서 관리한다.
이렇게 하면 비용, 성능, 과제 요구에 따라 모델을 교체하기 쉽다.

예상 설정:

```text
AI_PROVIDER=openai
AI_CHAT_MODEL=추후 선택
AI_EMBEDDING_MODEL=text-embedding-3-small
```

### 3.2 RAG 1차 기능 결정

| 항목 | 결정 | 이유 |
|---|---|---|
| RAG 사용 위치 | 게시글 작성 화면 | 사용자가 새 질문을 작성할 때 기존 유사 질문을 찾는 흐름이 가장 자연스럽다. |
| RAG 1차 기능 | 유사 게시글 추천 및 요약 | 중복 질문을 줄이고, 과거 게시글 기반으로 질문 품질을 높일 수 있다. |
| 실행 방식 | 사용자가 "유사 글 찾기" 버튼 클릭 | 자동 실행보다 비용과 호출 타이밍을 통제하기 쉽고, 디버깅과 발표 설명이 명확하다. |
| 검색 대상 | 게시글 제목 + 본문 + 태그 | 게시글의 핵심 의미를 충분히 담으면서 댓글까지 포함하는 복잡도는 피한다. |
| 1차 제외 | 댓글 기반 검색, 실시간 자동 추천, 별도 Q&A 챗봇, 트렌드 리포트 | 기본 RAG 흐름을 먼저 안정화한 뒤 확장한다. |

RAG 처리 흐름:

```text
게시글 작성 화면
→ 제목/본문/태그 입력
→ 유사 글 찾기 클릭
→ 입력 텍스트 embedding 생성
→ 저장된 게시글 embedding에서 top 3~5개 검색
→ LLM이 유사 이유와 요약 생성
→ 프론트에 추천 카드 표시
```

### 3.3 Embedding과 Vector DB 결정

| 항목 | 결정 | 이유 |
|---|---|---|
| Embedding Model | OpenAI `text-embedding-3-small` | OpenAI를 이미 사용하기로 했고, 비용 효율이 좋아 게시글 유사도 검색 1차 구현에 적합하다. |
| Embedding Dimension | 1536 | `text-embedding-3-small`의 기본 벡터 차원에 맞춰 pgvector 컬럼을 설계한다. |
| Vector DB | PostgreSQL + pgvector | 이미 PostgreSQL을 사용하므로 원본 게시글과 embedding을 같은 DB에서 관리할 수 있다. |
| 저장 전략 | 초기 backfill + 이후 증분 embedding | 기존 게시글은 한 번에 채우고, 새 글/수정 글은 해당 글만 embedding한다. |
| 검색 방식 | cosine distance 기반 top-k 검색 | 의미적으로 가까운 게시글을 상위 몇 개만 가져와 RAG 컨텍스트로 사용한다. |

Embedding은 검색 시점마다 전체 DB를 다시 계산하지 않는다.
게시글 embedding은 미리 저장하고, 검색할 때는 사용자의 현재 입력만 embedding한다.

### 3.4 RAG Framework와 관찰 도구 결정

| 항목 | 결정 | 이유 |
|---|---|---|
| RAG Framework | LangChain 사용 | OpenAI, embedding, retriever, prompt, LLM 호출을 연결하기 쉽고 RAG 예제와 자료가 많다. |
| 사용 범위 | 필요한 부분만 사용 | RAG 흐름 전체를 숨기지 않고, post_embeddings 테이블과 API 흐름은 직접 설계한다. |
| Observability | LangSmith 사용 | RAG/Agent의 중간 과정, 프롬프트, 검색 결과, 모델 응답을 추적하고 디버깅하기 좋다. |
| Agent Framework | LangGraph를 나중에 검토 | Agent 단계에서 상태, 분기, 도구 선택, 무한 루프 방지를 명시적으로 다루기 좋다. |

LangChain은 RAG 구현을 돕는 프레임워크이고, LangSmith는 실행 과정을 관찰하는 도구다.
LangSmith는 LangChain 전용은 아니지만, 이 프로젝트에서는 LangChain/LangGraph와 함께 쓰는 흐름이 가장 자연스럽다.

### 3.5 아직 비교 후 결정할 영역

| AI 영역 | 현재 결정 | 세부 기술 후보 |
|---|---|---|
| RAG | 글 작성 중 유사 게시글 추천 및 요약 | 이후 댓글 검색, Q&A 봇, 트렌드 리포트로 확장 가능 |
| Vector DB | PostgreSQL + pgvector | 규모가 커지면 Qdrant, Pinecone 등 전문 Vector DB 재검토 |
| Embedding Model | OpenAI `text-embedding-3-small` | 성능 부족 시 `text-embedding-3-large`, bge, e5, voyage 등 재검토 |
| MCP | 외부 개발 정보 조회 기능으로 사용 | GitHub API 연동 MCP Server 우선 고려 |
| Agent | 질문 개선/답변 초안 도우미로 사용 | LangGraph 우선 검토, 단순 Agent 흐름 후 확장 가능 |
| LLM | OpenAI 우선 사용 | 세부 chat 모델명은 비용/성능을 비교해 추후 선택 |

## 4. 현재 개발 순서 결정

현재는 아래 순서로 진행한다.

```text
1. 기본 기획 확정
2. DB 설계
3. REST API 설계
4. FastAPI 백엔드 기본 CRUD 구현
5. React 프론트 기본 화면 구현
6. 회원가입/로그인/권한 구현
7. 댓글/태그/검색/페이징 구현
8. 기본 게시판 안정화
9. RAG 세부 기술 선택 및 구현
10. MCP Server 구현
11. Agent 구현
12. 테스트
13. 배포
14. 문서화
```

## 5. 현재 1차 목표

가장 먼저 달성할 목표:

```text
React + FastAPI + PostgreSQL로
로그인 없이 게시글 목록, 상세, 작성 기능을 구현한다.
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

## 6. 다른 프레임워크로 다시 구현하는 것에 대한 판단

이 프로젝트를 완성한 뒤 다른 프레임워크로 다시 만들어보는 것은 의미가 있다.

예:

```text
1차 구현:
React + FastAPI + PostgreSQL

2차 재구현:
React + Spring Boot + PostgreSQL + 별도 Python AI Server
```

의미 있는 이유:

- 같은 요구사항을 다른 프레임워크가 어떻게 표현하는지 비교할 수 있다.
- FastAPI와 Spring Boot의 역할, 구조, 장단점이 더 선명해진다.
- API 설계, DB 설계, 인증, 권한 같은 핵심 개념은 유지되고 구현 방식만 바뀐다는 것을 배울 수 있다.
- 나중에 기업형 백엔드 구조를 학습할 때 좋은 비교 자료가 된다.

주의할 점:

- 처음부터 여러 프레임워크를 동시에 하지 않는다.
- 먼저 하나의 스택으로 끝까지 완성한다.
- 두 번째 구현은 완성 후 리팩토링/재구현 학습으로 진행한다.

정리:

```text
지금은 FastAPI로 완성한다.
완성 후 Spring Boot 등 다른 스택으로 다시 구현하는 것은 매우 좋은 학습 프로젝트가 될 수 있다.
```
