# Devpost submission text (copy and paste; edit anything that is not true for you)

## Track and mini challenge
- Primary track: Alexa+
- Mini challenge: Open Source (new project, MIT license)
- Not entering: AWS Builder

## Project description
Home Budget Assistant is a voice-first household budget helper built as a self-hosted MCP server
(Streamable HTTP, MCP spec 2025-11-25) for the Alexa+ track. Families can say "I spent 200 on
groceries", "add bill electricity 1200 due 2026-11-05" or "what bills are due?" and get an answer.
Data persists across sessions, so the assistant remembers last week's spending and upcoming bills.

The server exposes seven tools: add_expense, spending_summary, add_bill, upcoming_bills,
mark_bill_paid, savings_tip, and weekly_family_checkin. The last one combines spending by
category, bills due in the next 14 days and a personalised savings tip into one card.

Because Alexa+ is not available to me, I built a web simulator of a voice assistant. It has a
microphone button (browser speech recognition), spoken replies, suggestion chips and a rendered
check-in card. It calls the MCP server through the official MCP Python client (ClientSession over
Streamable HTTP), so every reply comes from a real MCP tool call, shown on screen.

Why it matters: many families manage bills and spending in their heads, which leads to missed
payments and unplanned shortfalls. I built this because my own family has faced money stress.
The MCP server could plug into any MCP-capable assistant, and the same tools could later be
extended with bank-statement imports, reminders and multiple languages.

Everything was built during the hackathon window. It is a new project.

## Built with
Python, MCP Python SDK (FastMCP server and ClientSession client), Streamable HTTP, Starlette,
Uvicorn, browser Web Speech API, MCP Inspector for testing.

## Open Source mini challenge fields
- Contribution URL: (your GitHub repo URL)
- Project repository URL: (your GitHub repo URL)
- GitHub username: (your username)
- Description: A new MIT-licensed project: an MCP server and voice-assistant simulator for household
  budgeting. It works by exposing budget tools over Streamable HTTP and calling them from a web
  client. It matters because it gives families a free, self-hostable assistant, and the code is a
  small, readable reference for building a stateful MCP server.

## Product feedback
**Tools used:** MCP Python SDK (mcp 1.30.0) to build the server with FastMCP and the client with
ClientSession; Streamable HTTP transport; MCP Inspector to test tools.

**What worked well:** FastMCP made a tool a single decorated function, and docstrings became tool
descriptions automatically. Streamable HTTP needed one line to run. The client API was easy to use.
Spec version 2025-11-25 was reported by the SDK, which made compliance easy to confirm.

**What needs work:** Running `pip install -U mcp` now installs the 2.x line, which renamed
FastMCP and changed client imports, so most existing tutorials and examples break until you pin
`mcp<2`. The client function was also renamed (streamablehttp_client to streamable_http_client),
and the error from a failed connection was only "unhandled errors in a TaskGroup", which hides the
real cause. A clearer connection error and a migration banner in the quickstart would help.
Docs for the Alexa+ track did not describe how an MCP server connects to the real Alexa+ app,
which is why I used the simulator path.

**Onboarding (zero to hello world):** about 15 minutes for the server once the version issue was
understood. I would estimate much longer for someone new who installs the latest version.

**Would I build with it again?** Yes. The protocol is simple, the SDK is small, and the tools I
wrote could be reused with any MCP-capable assistant.

## Friction log (paste each as a separate entry)

1. **Task:** Install the MCP SDK and run a hello-world server.
   **Steps:** `pip install -U mcp`, then `from mcp.server.fastmcp import FastMCP`.
   **Expected:** The tutorial import works. **Actual:** ModuleNotFoundError saying FastMCP was
   renamed to MCPServer in mcp 2.x.
   **Severity:** High (blocks first run). **Workaround:** `pip install "mcp>=1.23,<2"`.
   **Suggestion:** Show the version pin or the new import prominently in the quickstart.

2. **Task:** Connect a client to my server over Streamable HTTP.
   **Steps:** Called streamablehttp_client from the client module.
   **Expected:** Connection opens. **Actual:** ImportError, the function had been renamed.
   **Severity:** Medium. **Workaround:** Pin mcp 1.x. **Suggestion:** Keep a deprecated alias
   for one release.

3. **Task:** Debug a failed connection (server not running).
   **Steps:** Called the tool with the server stopped.
   **Expected:** A message such as "connection refused to localhost:8000".
   **Actual:** "unhandled errors in a TaskGroup (1 sub-exception)".
   **Severity:** Medium. **Workaround:** Print the sub-exception manually.
   **Suggestion:** Unwrap ExceptionGroup and show the root cause.

4. **Task:** Test the project against the real Alexa+ experience.
   **Steps:** Looked in the resources for how to connect my MCP server to Alexa+.
   **Expected:** A clear path to try it on a device or emulator.
   **Actual:** No public instructions, so I built a simulator.
   **Severity:** Medium. **Workaround:** Simulated experience path.
   **Suggestion:** Provide an Alexa+ test harness or emulator for MCP servers.

## Feature requests (optional)
- Alexa+ MCP test harness or emulator (Important): lets developers test without preview access.
- Ready-made MCP response format for cards and carousels (Nice-to-have).

## Demo video script (under 3 minutes; speak in English; no music; no logos)
0:00-0:20  "Many families track bills and spending in their heads and miss payments. I built Home
           Budget Assistant, an MCP server for the Alexa+ track, so you can just say it."
0:20-1:30  Open http://localhost:8080. Click the mic or chips: "I spent 200 on groceries",
           "I spent 450 on school fees", "add bill electricity 1200 due 2026-11-05",
           "what bills are due". Point at the "MCP tool called" line under each reply.
1:30-2:00  Say "give me my weekly check-in". Show the card. Say "it combines three tools into one plan".
2:00-2:30  Show server.py (the @mcp.tool functions, streamable-http) and the terminal where it runs.
           Show data.json to prove state is saved. Restart server.py and ask "what bills are due"
           again to prove the data persists across sessions.
2:30-3:00  "Everything is open source under MIT. Next steps are bank imports, reminders and
           more languages. Thanks for watching."
