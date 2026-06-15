from mcp.server.fastmcp import FastMCP

from ai_board_mcp.config import get_settings


def create_server() -> FastMCP:
    settings = get_settings()
    return FastMCP(settings.mcp_server_name)


def main() -> None:
    server = create_server()
    server.run(transport="stdio")


if __name__ == "__main__":
    main()
