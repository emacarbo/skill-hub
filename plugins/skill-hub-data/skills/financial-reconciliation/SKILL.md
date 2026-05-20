---
name: financial-reconciliation
description: "Multi-source financial data reconciliation: equity cap tables, trial balances, SBC waterfalls, and cross-system identity harmonization. Use when building reconciliation pipelines, variance analysis, or break investigation workflows across systems like Shareworks, NetSuite, Salesforce, RevPro, or IBF."
metadata:
  domain: finance-data
  triggers: reconciliation, cap table, trial balance, SBC, stock-based compensation, equity reconciliation, variance analysis, break investigation, NetSuite, Shareworks, RevPro, IBF
  role: finance-data-engineer
  scope: implementation
---

## Role

You are a finance data engineer specializing in multi-source reconciliation pipelines. You build reliable, auditable comparison frameworks that surface breaks clearly, track them to root cause, and produce exception reports suitable for audit review.

## When to Use

- Reconciling equity data between Shareworks and a legacy cap table system
- Building trial balance comparisons (period-over-period or system-to-system)
- Implementing SBC (Stock-Based Compensation) waterfall analysis
- Consolidating account or name mappings across NetSuite, IBF, or RevPro
- Investigating breaks: unexplained variance between two authoritative sources
- Building identity harmonization logic (employee IDs, legal name matching)

## Core Workflow

### 1. Establish Source Truth Before Comparing

Before writing any reconciliation logic:
1. Identify the **authoritative source** per data element (e.g., Shareworks is authoritative for grant counts; NetSuite is authoritative for booked expense)
2. Confirm the **as-of date** for each system (settlement date vs. book date vs. record date)
3. Validate that both sources have complete data for the reconciliation period before running comparisons

### 2. Multi-Source Reconciliation Patterns

**Full outer join pattern** — the standard for system-to-system comparison:

```sql
select
    coalesce(a.key, b.key)        as record_key,
    a.amount                       as source_a_amount,
    b.amount                       as source_b_amount,
    a.amount - b.amount            as variance,
    case
        when a.key is null then 'missing_in_source_a'
        when b.key is null then 'missing_in_source_b'
        when abs(a.amount - b.amount) > {{ tolerance }} then 'amount_break'
        else 'matched'
    end                            as reconciliation_status
from source_a a
full outer join source_b b using (key)
```

**Tolerance-based matching vs. exact matching**:
- Use exact matching for integer quantities (share counts, unit counts)
- Use tolerance matching for monetary amounts (rounding, FX conversion)
- Document tolerance thresholds explicitly (e.g., $0.01 for USD amounts, 0.001% for percentages)
- Never silently absorb differences larger than tolerance — surface them as warnings

### 3. Equity Cap Table Reconciliation

Key equity movements to reconcile:
- **Granted**: new grants issued in the period
- **Cancelled / Forfeited**: grants returned to the pool
- **Exercised / Released**: grants converted to shares
- **Repurchased**: shares bought back

Roll-forward check (the golden rule of cap table rec):
```
Opening balance + Granted - Cancelled - Exercised - Repurchased = Closing balance
```

Surface any unexplained residual as a break. Attach grant IDs to every row for traceability.

### 4. Trial Balance Comparison

**Period-over-period comparison**:
```sql
select
    account_code,
    account_name,
    current_period_balance,
    prior_period_balance,
    current_period_balance - prior_period_balance as movement,
    case
        when prior_period_balance = 0 then null
        else (current_period_balance - prior_period_balance) / abs(prior_period_balance)
    end as pct_change
from trial_balance
where abs(current_period_balance - prior_period_balance) > {{ materiality_threshold }}
order by abs(movement) desc
```

**System-to-system (e.g., NetSuite vs IBF)**:
- Align chart of accounts via a mapping table before comparing — never compare raw account codes across systems
- Flag accounts with no mapping as unresolved breaks, not zeros

### 5. SBC Accounting Flows

SBC waterfall components:
1. **Grant date fair value**: calculated at grant, amortized over vesting period
2. **Vesting expense**: recognized ratably (straight-line for cliff, graded for ratable)
3. **Forfeiture adjustment**: reversal of expense for unvested cancelled grants
4. **Excess tax benefit / shortfall**: difference between book and tax deduction at exercise

Reconciliation checkpoints:
- Unamortized pool = sum of (fair value × remaining vesting fraction) across all active grants
- Period expense = prior unamortized pool - current unamortized pool + new grants + adjustments
- Accumulated OCI / APIC = cumulative exercises and releases at fair value

### 6. Identity Harmonization

When records don't share a clean key:
1. Prefer a **golden record ID** (e.g., Workday employee_id) as the join key
2. Fall back to deterministic matching: legal name + hire date + last 4 SSN
3. Use fuzzy matching (Levenshtein, Jaro-Winkler) only for name normalization, never as the primary join
4. Persist all resolved mappings in a `employee_crosswalk` reference table — never re-resolve inline

### 7. Break Investigation Workflow

When a break is surfaced:
1. **Categorize**: timing difference, mapping gap, system error, or genuine discrepancy
2. **Quantify**: total break count and total break amount; sort descending by amount
3. **Drill down**: link each break record to the upstream source row + load timestamp
4. **Age breaks**: flag any break older than 30 days as escalation risk
5. **Document**: attach a break reason code and owner before closing

### 8. Reconciliation Reporting

Every reconciliation output should include:
- **Summary table**: total records, matched, breaks by type, total break amount
- **Exception detail**: one row per break with record key, both source values, variance, and break type
- **Trend line**: break count and amount over the last N periods
- **Sign-off column**: approved_by and approved_at for audit trail

### 9. Key Rules

- Never suppress a break — surface it with a reason code, not a null
- Always test reconciliation logic with known synthetic breaks before deploying to production
- Materiality thresholds must be documented and approved by Finance, not chosen by engineering
- Run reconciliations idempotently: re-running the same period must produce the same result
- Retain reconciliation run history (run_id, run_at, period) for audit lookback
