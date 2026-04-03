---
name: voltaire-status
description: Quick pulse check on your paywall. Triggered by "voltaire status", "how is my paywall", "check my conversion rate".
---

First, check if the Voltaire MCP tools are available by attempting to call `mcp__voltaire__get_stats`.

If the tool call fails, tell the user:
"Run `/mcp` in Claude Code, find **voltaire** in the list, and click **Authenticate**. A browser will open — log in with Google or GitHub. Once done, run `/voltaire:voltaire-status` again."
Then stop.

If the tools are available:

1. Call `mcp__voltaire__get_stats` — check connection status, SDK status, data volume.

2. Call `mcp__voltaire__analyze_paywall` — extract:
   - Current conversion rate vs benchmark
   - Revenue this week vs last week
   - Any anomalies flagged
   - Last fix applied and its impact (if measurable)
   - 7-day trend direction

3. Output a compact status card — no prose, just facts:
   ```
   📊 Voltaire Status — [date]

   Conversion:  X.X% (benchmark: Y.Y%)  [↑↓ vs last week]
   Revenue:     $X this week  [↑↓ $Y vs last week]
   Data points: X events collected
   Last fix:    [one line, date]
   Trend:       ↑ improving / → flat / ↓ declining

   [Any anomaly alerts if present]
   ```

4. If data is thin (SDK not installed or < 7 days of data): say so clearly. Suggest running `/voltaire` to complete setup.

5. If trial expired: "Your 14-day Lumière Intelligence trial has ended. Upgrade at https://app.hivoltaire.com/account to restore agent analysis."

No fixes, no recommendations — read-only. For a full analysis and fix, run `/voltaire`.
