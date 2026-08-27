"""Google Workspace integration: tools auto-discovered from a local workspace-mcp server.

Usage in the kernel:

    import gworkspace
    for t in await gworkspace.list_tools():
        print(t["name"])
"""

from __future__ import annotations

from rlm import McpIntegration

__all__ = ["GWorkspace", "gworkspace"]


class GWorkspace(McpIntegration):
    server = "gworkspace"
    # Overridden by mcpServers.gworkspace.url in settings.json when present.
    url = "http://127.0.0.1:8000/mcp"
    # The local server ignores Authorization; this var only satisfies the
    # host/kernel "is authed" check so the skill loads without an OAuth flow.
    bearer_token_env = "GWORKSPACE_MCP_TOKEN"


gworkspace = GWorkspace()

_RESERVED = {"run", "__wrapped__", "__call__"}


def __getattr__(name: str):
    if name.startswith("_") or name in _RESERVED:
        raise AttributeError(name)
    return getattr(gworkspace, name)
