# Home Budget Assistant

A voice-first household budget assistant built for the Amazon Developer Hackathon, **Alexa+ track**.
It is a self-hosted **MCP server** (Streamable HTTP, MCP spec 2025-11-25) plus a web simulator
of a voice assistant that calls the server through the official MCP Python client.

Many families track bills and spending in their heads. This lets anyone say
"I spent 200 on groceries" or "what bills are due?" and get an answer, with state saved across sessions.

## MCP tools
`add_expense`, `spending_summary`, `add_bill`, `upcoming_bills`, `mark_bill_paid`,
`savings_tip`, and `weekly_family_checkin` (one call that combines spending, bills due and a savings
tip into a card).

## Run (Python 3.10+)
```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
python server.py                # terminal 1: MCP server at http://localhost:8000/mcp
python app.py                   # terminal 2: simulator at http://localhost:8080
```
Open http://localhost:8080 and try: "I spent 200 on groceries", "add bill electricity 1200 due 2026-11-05",
"what bills are due", "how much did we spend this week", "give me my weekly check-in".
Use the mic button (Chrome) to speak.

## How it works
`app.py` maps a sentence to a tool with a small rule-based matcher (free, no API keys), then calls the
tool via `ClientSession` over Streamable HTTP. `server.py` implements the tools with FastMCP and
stores data in `data.json`. You can also test the server directly with
`npx @modelcontextprotocol/inspector`.

## License
MIT
