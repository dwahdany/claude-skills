---
name: gworkspace
description: Read and write Google Docs, Drive, Gmail, Calendar, Sheets and Slides through a local workspace-mcp server. Tools are auto-discovered from the server at runtime.
---

# Google Workspace

Talk to Google Workspace through a locally running `workspace-mcp` server
(streamable HTTP on 127.0.0.1:8000) from the IPython kernel.

## Setup (host, one time)

1. `systemctl --user status workspace-mcp` — the server must be running.
2. Google account consent: call the server's auth tool once and open the URL it
   returns in a browser:

   ```python
   import gworkspace
   print(await gworkspace.call_tool("start_google_auth",
                                    {"user_google_email": "you@example.com"}))
   ```

If a call raises `NotEnabled`, `GWORKSPACE_MCP_TOKEN` is not set in this
process's environment — tell the user; do not try to work around it.

## Usage

The tool set is defined by the server, so **discover before you call**:

```python
import gworkspace

for tool in await gworkspace.list_tools():
    print(tool["name"], "-", tool["description"])

doc = await gworkspace.call_tool("get_doc_content",
                                 {"user_google_email": "you@example.com",
                                  "document_id": "<id>"})
```

Notes:
- Every call is `async` — always `await`.
- Results are already-parsed Python; no `json.loads`.
- Most tools require `user_google_email`; the consented account is per email.
- The kernel import name is `gworkspace`.
