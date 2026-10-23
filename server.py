"""Family Budget MCP server: an Alexa+ style voice-assistant backend.

Transport: Streamable HTTP (endpoint: http://localhost:8000/mcp)
"""
import json
from datetime import date, datetime, timedelta
from pathlib import Path

from mcp.server.fastmcp import FastMCP

DB = Path(__file__).with_name("data.json")
mcp = FastMCP("family-budget", host="0.0.0.0", port=8000)


def load() -> dict:
    if DB.exists():
        return json.loads(DB.read_text())
    return {"expenses": [], "bills": []}


def save(data: dict) -> None:
    DB.write_text(json.dumps(data, indent=2))


@mcp.tool()
def add_expense(amount: float, category: str, note: str = "") -> str:
    """Record a household expense. Category examples: groceries, transport, school, health."""
    data = load()
    data["expenses"].append(
        {"amount": amount, "category": category.lower(), "note": note,
         "date": date.today().isoformat()}
    )
    save(data)
    return f"Added {amount:.2f} under {category}."


@mcp.tool()
def spending_summary(days: int = 7) -> str:
    """Summarise spending by category for the last N days (default 7)."""
    data = load()
    since = date.today() - timedelta(days=days)
    totals: dict[str, float] = {}
    for e in data["expenses"]:
        if date.fromisoformat(e["date"]) >= since:
            totals[e["category"]] = totals.get(e["category"], 0) + e["amount"]
    if not totals:
        return f"No expenses recorded in the last {days} days."
    lines = [f"{c}: {t:.2f}" for c, t in sorted(totals.items(), key=lambda x: -x[1])]
    return f"Last {days} days, total {sum(totals.values()):.2f}. " + "; ".join(lines)


@mcp.tool()
def add_bill(name: str, amount: float, due_date: str) -> str:
    """Add an upcoming bill. due_date must be YYYY-MM-DD."""
    datetime.strptime(due_date, "%Y-%m-%d")  # validate
    data = load()
    data["bills"].append({"name": name, "amount": amount, "due_date": due_date, "paid": False})
    save(data)
    return f"Saved bill {name} of {amount:.2f}, due {due_date}."


@mcp.tool()
def upcoming_bills(days: int = 14) -> str:
    """List unpaid bills due within the next N days."""
    data = load()
    limit = date.today() + timedelta(days=days)
    due = [b for b in data["bills"]
           if not b["paid"] and date.fromisoformat(b["due_date"]) <= limit]
    if not due:
        return f"No bills due in the next {days} days."
    due.sort(key=lambda b: b["due_date"])
    return "; ".join(f"{b['name']} {b['amount']:.2f} due {b['due_date']}" for b in due)


@mcp.tool()
def mark_bill_paid(name: str) -> str:
    """Mark the first unpaid bill matching this name as paid."""
    data = load()
    for b in data["bills"]:
        if not b["paid"] and name.lower() in b["name"].lower():
            b["paid"] = True
            save(data)
            return f"Marked {b['name']} as paid."
    return f"No unpaid bill found matching {name}."


@mcp.tool()
def savings_tip(days: int = 30) -> str:
    """Find the biggest spending category recently and suggest where to cut."""
    data = load()
    since = date.today() - timedelta(days=days)
    totals: dict[str, float] = {}
    for e in data["expenses"]:
        if date.fromisoformat(e["date"]) >= since:
            totals[e["category"]] = totals.get(e["category"], 0) + e["amount"]
    if not totals:
        return "Not enough data yet. Add a few expenses first."
    top, amt = max(totals.items(), key=lambda x: x[1])
    return (f"Your biggest category is {top} at {amt:.2f} over {days} days. "
            f"Cutting it by 15% would save about {amt * 0.15:.2f}.")


@mcp.tool()
def weekly_family_checkin() -> str:
    """One-shot weekly plan: spending, bills due soon, and a savings tip, returned as JSON card data."""
    data = load()
    today = date.today()
    totals: dict[str, float] = {}
    for e in data["expenses"]:
        if date.fromisoformat(e["date"]) >= today - timedelta(days=7):
            totals[e["category"]] = totals.get(e["category"], 0) + e["amount"]
    due = sorted(
        [b for b in data["bills"] if not b["paid"]
         and date.fromisoformat(b["due_date"]) <= today + timedelta(days=14)],
        key=lambda b: b["due_date"])
    bills_total = sum(b["amount"] for b in due)
    top = max(totals.items(), key=lambda x: x[1]) if totals else None
    tip = (f"Biggest spend is {top[0]} ({top[1]:.2f}). Trim 15% to save {top[1]*0.15:.2f}."
           if top else "Add some expenses to get a tip.")
    return json.dumps({
        "card": "weekly_checkin",
        "spent_7d": round(sum(totals.values()), 2),
        "by_category": totals,
        "bills_due": due,
        "bills_total": round(bills_total, 2),
        "tip": tip,
    })


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
