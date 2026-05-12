"""
MK Agency Sweep
Run this via Claude Code: just say "sweep" and Claude will call the Gmail/Calendar
MCPs, compile urgent flags, update dashboard.html, and fire alerts here.

This script is for standalone alert sending — Claude calls send_alert() during sweeps.
"""

import urllib.request
import urllib.parse
import json

BOT_TOKEN = "8603727414:AAFlx0BLcd5Awx4fy5EdinpsXkoDcqce-2Q"
CHAT_ID = "770097364"
DASHBOARD_URL = "https://mitchelljkwan-collab.github.io/dashboard/dashboard.html"


def send_alert(message: str) -> bool:
    """Send a message to the MK Agency Alerts Telegram bot."""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = urllib.parse.urlencode({
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "HTML",
        "disable_web_page_preview": "true",
    }).encode()
    try:
        req = urllib.request.Request(url, data=data, method="POST")
        with urllib.request.urlopen(req, timeout=10) as resp:
            result = json.loads(resp.read())
            return result.get("ok", False)
    except Exception as e:
        print(f"Telegram send failed: {e}")
        return False


def send_sweep_summary(flags: list[str]) -> bool:
    """
    Send a formatted sweep digest. Pass a list of flag strings.
    Example:
        flags = [
            "🔥 Keshia watched the Extreme Beauty preview — follow up NOW",
            "⚠️ skinexpertsco.com.au domain renewal failed",
        ]
    """
    if not flags:
        return send_alert("✅ Sweep done — nothing urgent.")

    lines = ["<b>MK Agency Sweep</b>", ""] + [f"• {f}" for f in flags]
    lines += ["", f'<a href="{DASHBOARD_URL}">Open dashboard →</a>']
    return send_alert("\n".join(lines))


if __name__ == "__main__":
    # Quick test
    send_sweep_summary([
        "🔥 Test flag — bot is wired up correctly",
    ])
    print("Done.")
