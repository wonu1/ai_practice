from mcp.server.fastmcp import FastMCP

from ai_board_mcp.config import get_settings
from ai_board_mcp.tools import github_search_issues


def create_server() -> FastMCP:
    settings = get_settings()
    server = FastMCP(settings.mcp_server_name)
    server.tool(
        name="github_search_issues",
        description=(
            "Search GitHub issues related to a development question. "
            "Use this when an external open-source issue reference can help."
        ),
    )(github_search_issues)
    return server


def main() -> None:
    server = create_server()
    server.run(transport="stdio")


if __name__ == "__main__":
    main()
