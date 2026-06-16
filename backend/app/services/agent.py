import json
import os
from typing import Any, TypedDict

from langchain_openai import ChatOpenAI
from sqlalchemy.orm import Session

from backend.app.core.config import get_settings
from backend.app.services.embeddings import search_similar_posts
from backend.app.services.mcp_client import search_github_issues_via_mcp
from backend.app.services.rag import summarize_similar_posts


MAX_TOOL_CALLS = 2
MAX_TOOL_RESULTS = 5


class AgentInput(TypedDict):
    title: str
    content: str
    tags: list[str]


class AgentAnalysis(TypedDict):
    intent: str
    missing_info: list[str]
    needs_rag: bool
    needs_mcp: bool
    reason: str


class AgentControl(TypedDict):
    step_count: int
    tool_call_count: int
    errors: list[str]


class AgentState(TypedDict, total=False):
    input: AgentInput
    analysis: AgentAnalysis
    rag_results: dict[str, Any]
    mcp_results: dict[str, Any]
    final_answer: dict[str, Any]
    control: AgentControl


def create_initial_agent_state(
    *,
    title: str,
    content: str,
    tags: list[str],
) -> AgentState:
    return {
        "input": {
            "title": title,
            "content": content,
            "tags": tags,
        },
        "control": {
            "step_count": 0,
            "tool_call_count": 0,
            "errors": [],
        },
    }


def _configure_langsmith() -> None:
    settings = get_settings()

    if settings.langsmith_tracing:
        os.environ["LANGSMITH_TRACING"] = "true"
        os.environ["LANGSMITH_PROJECT"] = settings.langsmith_project
        if settings.langsmith_api_key:
            os.environ["LANGSMITH_API_KEY"] = settings.langsmith_api_key


def _get_chat_client() -> ChatOpenAI | None:
    settings = get_settings()

    if settings.ai_provider != "openai" or not settings.openai_api_key:
        return None

    _configure_langsmith()
    return ChatOpenAI(
        model=settings.ai_chat_model,
        api_key=settings.openai_api_key,
    )


def _bump_step(state: AgentState) -> None:
    control = state.setdefault(
        "control",
        {"step_count": 0, "tool_call_count": 0, "errors": []},
    )
    control["step_count"] += 1


def _bump_tool_call(state: AgentState) -> bool:
    control = state.setdefault(
        "control",
        {"step_count": 0, "tool_call_count": 0, "errors": []},
    )
    if control["tool_call_count"] >= MAX_TOOL_CALLS:
        control["errors"].append("도구 호출 제한에 도달했습니다.")
        return False
    control["tool_call_count"] += 1
    return True


def _append_error(state: AgentState, message: str | None) -> None:
    if not message:
        return
    control = state.setdefault(
        "control",
        {"step_count": 0, "tool_call_count": 0, "errors": []},
    )
    control["errors"].append(message)


def _as_text(value: Any) -> str:
    if isinstance(value, str):
        return value.strip()
    return str(value).strip()


def _parse_json_object(text: str) -> dict[str, Any] | None:
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        return None
    if isinstance(parsed, dict):
        return parsed
    return None


def _fallback_analysis(agent_input: AgentInput) -> AgentAnalysis:
    title = agent_input["title"].strip()
    content = agent_input["content"].strip()
    tags = [tag.lower() for tag in agent_input["tags"]]
    combined = f"{title}\n{content}\n{' '.join(tags)}".lower()
    is_too_short = len(title) + len(content) < 25
    external_keywords = [
        "fastapi",
        "react",
        "spring",
        "jwt",
        "oauth",
        "docker",
        "postgres",
        "github",
        "issue",
        "error",
        "exception",
        "bug",
    ]
    needs_mcp = not is_too_short and any(
        keyword in combined for keyword in external_keywords
    )
    needs_rag = not is_too_short
    missing_info: list[str] = []

    if is_too_short:
        missing_info.extend(["문제 상황", "오류 메시지", "사용 기술"])
    if "error" in combined or "오류" in combined or "에러" in combined:
        missing_info.extend(["전체 오류 메시지", "관련 코드", "실행 환경"])

    return {
        "intent": title or "게시글 작성 도움 요청",
        "missing_info": list(dict.fromkeys(missing_info)),
        "needs_rag": needs_rag,
        "needs_mcp": needs_mcp,
        "reason": "규칙 기반 분석 결과입니다.",
    }


def analyze_node(state: AgentState) -> AgentState:
    _bump_step(state)
    agent_input = state["input"]
    client = _get_chat_client()

    if client is None:
        state["analysis"] = _fallback_analysis(agent_input)
        return state

    prompt = f"""
너는 개발 게시판의 글쓰기 보조 Agent다.
사용자의 게시글 초안을 분석하고, 필요한 도구를 판단해라.

판단 기준:
- needs_rag=true: 내부 유사 게시글이나 중복 질문 확인이 도움 될 때
- needs_mcp=true: 특정 라이브러리, 프레임워크, 오류, GitHub issue 사례가 도움 될 때
- 질문이 너무 짧거나 불명확하면 도구를 쓰기보다 missing_info를 채워라

반드시 JSON 객체만 반환해라.
형식:
{{
  "intent": "질문 의도",
  "missing_info": ["부족한 정보"],
  "needs_rag": true,
  "needs_mcp": false,
  "reason": "판단 이유"
}}

제목: {agent_input["title"]}
태그: {", ".join(agent_input["tags"])}
본문:
{agent_input["content"]}
""".strip()

    try:
        response = client.invoke(prompt)
        parsed = _parse_json_object(_as_text(response.content))
    except Exception:
        parsed = None

    if parsed is None:
        state["analysis"] = _fallback_analysis(agent_input)
        _append_error(state, "LLM 분석 결과를 해석하지 못해 규칙 기반 분석을 사용했습니다.")
        return state

    state["analysis"] = {
        "intent": str(parsed.get("intent") or agent_input["title"]),
        "missing_info": [
            str(item) for item in parsed.get("missing_info", []) if str(item).strip()
        ],
        "needs_rag": bool(parsed.get("needs_rag")),
        "needs_mcp": bool(parsed.get("needs_mcp")),
        "reason": str(parsed.get("reason") or ""),
    }
    return state


def retrieve_internal_node(state: AgentState, db: Session) -> AgentState:
    _bump_step(state)
    analysis = state.get("analysis")
    if not analysis or not analysis.get("needs_rag"):
        state["rag_results"] = {
            "status": "skipped",
            "message": "내부 유사 글 검색이 필요하지 않다고 판단했습니다.",
            "similar_posts": [],
            "summary": None,
        }
        return state

    if not _bump_tool_call(state):
        state["rag_results"] = {
            "status": "skipped",
            "message": "도구 호출 제한으로 내부 검색을 생략했습니다.",
            "similar_posts": [],
            "summary": None,
        }
        return state

    agent_input = state["input"]
    search_result = search_similar_posts(
        db,
        title=agent_input["title"],
        content=agent_input["content"],
        tags=agent_input["tags"],
        limit=MAX_TOOL_RESULTS,
    )
    summary = summarize_similar_posts(
        title=agent_input["title"],
        content=agent_input["content"],
        tags=agent_input["tags"],
        similar_posts=search_result.items,
    )
    state["rag_results"] = {
        "status": search_result.status,
        "message": search_result.message,
        "similar_posts": [
            {
                "post_id": item.post_id,
                "title": item.title,
                "content_preview": item.content[:200],
                "tag_names": item.tag_names,
                "similarity": item.similarity,
            }
            for item in search_result.items
        ],
        "summary": summary,
    }
    if search_result.status not in {"ok", "no_results"}:
        _append_error(state, search_result.message)
    return state


def _build_github_query(state: AgentState) -> str:
    agent_input = state["input"]
    analysis = state.get("analysis", {})
    query_parts = [
        str(analysis.get("intent") or ""),
        agent_input["title"],
        " ".join(agent_input["tags"]),
    ]
    query = " ".join(part.strip() for part in query_parts if part.strip())
    return query[:200] or agent_input["title"][:200]


async def search_external_node(state: AgentState) -> AgentState:
    _bump_step(state)
    analysis = state.get("analysis")
    if not analysis or not analysis.get("needs_mcp"):
        state["mcp_results"] = {
            "status": "skipped",
            "message": "외부 GitHub issue 검색이 필요하지 않다고 판단했습니다.",
            "github_issues": [],
        }
        return state

    if not _bump_tool_call(state):
        state["mcp_results"] = {
            "status": "skipped",
            "message": "도구 호출 제한으로 외부 검색을 생략했습니다.",
            "github_issues": [],
        }
        return state

    result = await search_github_issues_via_mcp(
        query=_build_github_query(state),
        repository=None,
        limit=MAX_TOOL_RESULTS,
    )
    state["mcp_results"] = {
        "status": result.get("status", "mcp_error"),
        "message": result.get("message"),
        "github_issues": result.get("items", []),
    }
    if result.get("status") not in {"ok", "no_results", "rate_limited"}:
        _append_error(state, result.get("message"))
    return state


def _build_used_sources(state: AgentState) -> list[dict[str, Any]]:
    sources: list[dict[str, Any]] = []
    for item in state.get("rag_results", {}).get("similar_posts", []):
        sources.append(
            {
                "type": "internal_post",
                "title": item.get("title"),
                "ref": item.get("post_id"),
            }
        )
    for item in state.get("mcp_results", {}).get("github_issues", []):
        sources.append(
            {
                "type": "github_issue",
                "title": item.get("title"),
                "ref": item.get("url"),
            }
        )
    return sources


def _fallback_final_answer(state: AgentState) -> dict[str, Any]:
    analysis = state.get("analysis", {})
    missing_info = analysis.get("missing_info", [])
    feedback = []

    if missing_info:
        feedback.append(
            "질문에 다음 정보를 보강하면 답변 품질이 좋아집니다: "
            + ", ".join(missing_info)
        )
    else:
        feedback.append("질문 의도는 비교적 명확합니다. 재현 과정과 기대 결과를 함께 쓰면 더 좋습니다.")

    if state.get("rag_results", {}).get("similar_posts"):
        feedback.append("내부 유사 게시글을 먼저 확인해 중복 질문인지 비교해 보세요.")
    if state.get("mcp_results", {}).get("github_issues"):
        feedback.append("GitHub issue 참고 자료를 함께 보면 외부 사례까지 확인할 수 있습니다.")

    return {
        "feedback": feedback,
        "draft": (
            f"{state['input']['title']}에 대한 질문 초안입니다.\n\n"
            "문제 상황, 재현 방법, 기대 결과, 실제 결과를 나누어 작성해 보세요."
        ),
        "used_sources": _build_used_sources(state),
    }


def generate_node(state: AgentState) -> AgentState:
    _bump_step(state)
    client = _get_chat_client()

    if client is None:
        state["final_answer"] = _fallback_final_answer(state)
        return state

    prompt = f"""
너는 개발 게시판의 글쓰기 보조 Agent다.
아래 AgentState를 바탕으로 사용자가 더 좋은 질문을 작성하도록 도와라.

반드시 JSON 객체만 반환해라.
형식:
{{
  "feedback": ["질문 개선 제안"],
  "draft": "사용자가 수정해서 쓸 수 있는 답변 또는 글 초안",
  "used_sources": [
    {{"type": "internal_post 또는 github_issue", "title": "근거 제목", "ref": "id 또는 url"}}
  ]
}}

AgentState:
{json.dumps(state, ensure_ascii=False, default=str)}
""".strip()

    try:
        response = client.invoke(prompt)
        parsed = _parse_json_object(_as_text(response.content))
    except Exception:
        parsed = None

    if parsed is None:
        state["final_answer"] = _fallback_final_answer(state)
        _append_error(state, "LLM 최종 응답을 해석하지 못해 규칙 기반 응답을 사용했습니다.")
        return state

    state["final_answer"] = {
        "feedback": [
            str(item) for item in parsed.get("feedback", []) if str(item).strip()
        ],
        "draft": str(parsed.get("draft") or ""),
        "used_sources": parsed.get("used_sources") or _build_used_sources(state),
    }
    return state
