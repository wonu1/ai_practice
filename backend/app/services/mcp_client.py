import json
import os
import sys
import time
from pathlib import Path
from typing import Any

from mcp.client.session import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client

from backend.app.core.config import get_settings


def _project_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _mcp_server_cwd() -> Path:
    settings = get_settings()
    configured_path = Path(settings.mcp_server_cwd)
    if configured_path.is_absolute():
        return configured_path
    return _project_root() / configured_path


def _mcp_server_command() -> str:
    settings = get_settings()
    return settings.mcp_server_command or sys.executable


def _mcp_server_args() -> list[str]:
    settings = get_settings()
    if settings.mcp_server_command:
        return []
    return [
        "-c",
        "import sys; sys.path.insert(0, 'src'); from ai_board_mcp.server import main; main()",
    ]


def _mcp_server_env(cwd: Path) -> dict[str, str]:
    env = os.environ.copy()
    existing_pythonpath = env.get("PYTHONPATH")
    src_path = str(cwd / "src")
    env["PYTHONPATH"] = (
        f"{src_path}{os.pathsep}{existing_pythonpath}"
        if existing_pythonpath
        else src_path
    )
    return env


def _read_tool_payload(result: Any) -> dict[str, Any]:
    if result.structuredContent:
        return result.structuredContent
    if not result.content:
        return {
            "items": [],
            "status": "mcp_error",
            "message": "MCP tool 응답이 비어 있습니다.",
        }
    return json.loads(result.content[0].text)


async def search_github_issues_via_mcp(
    *,
    query: str,
    repository: str | None,
    limit: int,
) -> dict[str, Any]:
    cwd = _mcp_server_cwd()
    server_params = StdioServerParameters(
        command=_mcp_server_command(),
        args=_mcp_server_args(),
        cwd=cwd,
        env=_mcp_server_env(cwd),
    )

    started_at = time.perf_counter()

    try:
        async with stdio_client(server_params) as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                result = await session.call_tool(
                    "github_search_issues",
                    arguments={
                        "query": query,
                        "repository": repository,
                        "limit": limit,
                    },
                )
                payload = _read_tool_payload(result)
                payload["duration_ms"] = int((time.perf_counter() - started_at) * 1000)
                return payload
    except Exception:
        return {
            "items": [],
            "status": "mcp_error",
            "message": "MCP 서버 호출 중 문제가 발생했습니다.",
            "duration_ms": int((time.perf_counter() - started_at) * 1000),
        }
