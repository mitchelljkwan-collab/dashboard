# MK Agency Dashboard

Static HTML dashboard for Mitchell Kwan. One file: `dashboard.html`.

## Sweep

When told to "sweep", execute this sequence in order — no narration during execution:

1. **Gmail MCP** — fetch unread emails from the last 48 hours only
2. **Calendar MCP** — fetch events for the next 7 days only
3. **Identify flags** matching any of:
   - Client replies (Keshia / Extreme Beauty, Ella or Adriano / Blank Kanvas, PM Aesthetics / foundryclinical.au)
   - Unpaid or overdue invoices mentioned
   - Domain, billing, or subscription alerts
   - Legal updates (Quest Legal, MMJ / Vesna White)
   - Anything time-sensitive requiring same-day action
4. **Edit dashboard.html** — patch only the sections that changed:
   - `<!-- Alerts -->` block: add/remove `.focus-item.red` divs
   - `<!-- Today's Focus -->` block: update `.focus-item` divs
   - `<!-- Client Projects -->` cards: update status, waiting-on, last contact, next action
   - `<!-- This Week -->` calendar: add/remove `.cal-event` entries
   - Header timestamp: update swept date/time in `<p>` under `<h1>`
5. **Telegram** — call `send_alert()` with flag list (skip if nothing urgent)

**Do not rewrite the full file.** Use surgical edits — only touch what changed.

## Output format

After sweeping, output only:
- Bullet list of what changed in the dashboard
- Alert flags sent (or "nothing urgent — no alert sent")

No reasoning, no explanation, no summary of what you read.

## Manual updates

When told to update something specific (e.g. "mark Extreme Beauty invoice as paid"), edit only the relevant card or section. State what line changed. Nothing else.

## HTML structure reference

| Section | Selector | What it contains |
|---|---|---|
| Alerts | `.alert-box` | Red `.focus-item` divs for blocking issues |
| Today's Focus | `.focus-box` | `.focus-item` divs for same-day actions |
| Money | `.cards` (first) | Outstanding invoices + lease exit cards |
| Client Projects | `.cards` (second) | Per-client status cards |
| This Week | `.cal-section` | `.cal-day` blocks with `.cal-event` entries |
| Footer | `.updated` | Last swept timestamp |
