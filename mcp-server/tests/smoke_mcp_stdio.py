import argparse
import json
import sys

import anyio
from mcp.client.session import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client


def _read_tool_payload(result) -> dict:
    if result.structuredContent:
        return result.structuredContent
    return json.loads(result.content[0].text)


async def run_smoke_test(include_live_call: bool) -> None:
    server_params = StdioServerParameters(
        command=sys.executable,
        args=["-c", "from ai_board_mcp.server import main; main()"],
    )

    async with stdio_client(server_params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            init = await session.initialize()
            tools = await session.list_tools()
            tool_names = {tool.name for tool in tools.tools}
            assert "github_search_issues" in tool_names

            invalid_result = await session.call_tool(
                "github_search_issues",
                arguments={"query": "", "repository": None, "limit": 5},
            )
            invalid_payload = _read_tool_payload(invalid_result)
            assert invalid_payload["status"] == "invalid_input"

            print(f"initialize ok: {init.serverInfo.name}")
            print("tools/list ok: github_search_issues")
            print("invalid input ok")

            if not include_live_call:
                return

            live_result = await session.call_tool(
                "github_search_issues",
                arguments={
                    "query": "jwt auth",
                    "repository": "fastapi/fastapi",
                    "limit": 2,
                },
            )
            live_payload = _read_tool_payload(live_result)
            assert live_payload["status"] in {"ok", "no_results", "rate_limited"}
            print(f"live GitHub call ok: {live_payload['status']}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Smoke-test the MCP stdio server.")
    parser.add_argument(
        "--live",
        action="store_true",
        help="Also call the real GitHub Search API.",
    )
    args = parser.parse_args()

    anyio.run(run_smoke_test, args.live)


if __name__ == "__main__":
    main()
