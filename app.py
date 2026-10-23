"""Home Budget Assistant: voice/chat simulator that talks to the MCP server
over Streamable HTTP using the official MCP Python client."""
import json
import re
from pathlib import Path

import uvicorn
from mcp import ClientSession
from starlette.applications import Starlette
from starlette.responses import HTMLResponse, JSONResponse
from starlette.routing import Route

from mcp.client.streamable_http import streamablehttp_client as http_client

MCP_URL = "http://localhost:8000/mcp"
NUM = r"(?:rs\.?|₹|\$)?\s*(\d+(?:\.\d+)?)"


def pick_tool(text: str):
    """Tiny free intent matcher: maps a sentence to an MCP tool + arguments."""
    t = text.lower().strip()
    m = re.search(r"add bill (.+?) " + NUM + r" due (\d{4}-\d{2}-\d{2})", t)
    if m:
        return "add_bill", {"name": m.group(1), "amount": float(m.group(2)), "due_date": m.group(3)}
    m = re.search(r"(?:mark|paid)\s+(?:the\s+)?(.+?)\s+bill", t)
    if m:
        return "mark_bill_paid", {"name": m.group(1)}
    m = re.search(r"(?:spent|paid|bought)\s+" + NUM + r"\s*(?:on|for)\s+([a-z ]+)", t)
    if m:
        return "add_expense", {"amount": float(m.group(1)), "category": m.group(2).strip()}
    if re.search(r"check-?in|weekly plan|plan my week|family plan", t):
        return "weekly_family_checkin", {}
    if "bill" in t:
        return "upcoming_bills", {}
    if re.search(r"save|saving|tip|cut", t):
        return "savings_tip", {}
    if re.search(r"spend|spent|summary|how much", t):
        d = re.search(r"(\d+)\s*days?", t)
        return "spending_summary", {"days": int(d.group(1)) if d else (30 if "month" in t else 7)}
    return None, None


async def chat(request):
    text = (await request.json()).get("text", "")
    tool, args = pick_tool(text)
    if not tool:
        return JSONResponse({"reply": "Try: 'I spent 200 on groceries', 'what bills are due', "
                                      "'give me my weekly check-in'.", "tool": None})
    try:
        async with http_client(MCP_URL) as streams:
            async with ClientSession(streams[0], streams[1]) as session:
                await session.initialize()
                result = await session.call_tool(tool, args)
                out = result.content[0].text
    except Exception as e:  # server not running etc.
        return JSONResponse({"reply": f"Can't reach the MCP server ({e}). Is server.py running?",
                             "tool": None})
    card = None
    try:
        j = json.loads(out)
        if isinstance(j, dict) and j.get("card"):
            card = j
            out = f"Here is your weekly check-in. {j['tip']}"
    except ValueError:
        pass
    return JSONResponse({"reply": out, "tool": tool, "args": args, "card": card})


async def index(request):
    return HTMLResponse((Path(__file__).with_name("index.html")).read_text())


app = Starlette(routes=[Route("/", index), Route("/chat", chat, methods=["POST"])])

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8080)
