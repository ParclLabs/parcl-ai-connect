# Accidental Landlord Lead Generation

Identify homeowners who failed to sell and pivoted to renting. These are the highest-intent property management prospects. Parcl Labs coined this term and the methodology that generated Tier-1 media coverage (WSJ, NYT, CNBC, MSNBC).

![Accidental Landlord Demo](../../assets/gifs/accidental-landlords_small.gif)

## What You Get

A client-ready HTML dashboard with:

- KPI strip (total leads, median price, median rent, median yield)
- Geographic distribution charts (top ZIPs, top cities)
- Searchable, sortable lead table with motivated seller/renter signals
- Full methodology documentation embedded

The Houston MSA reference implementation produced **1,464 qualified leads**.

## Choose Your Path

### Basic (Copy & Paste)

No setup required. Copy the prompt from [`basic/PROMPT.md`](basic/PROMPT.md) into Claude Code with the Parcl Labs MCP connected.

### Advanced (Skill)

Run `/accidental-landlord [market name]` in Claude Code for a fully automated pipeline with:

- 110-day rolling window methodology with same-owner filtering
- Motivated seller/renter enrichment joins
- Outlier detection and quality checks
- Reference output validation against published benchmarks

See the [skill definition](../../.claude/skills/accidental-landlord/SKILL.md) for full details.

## Key Concepts

- **110-Day Rolling Window**: 50-day lookback for sale events + 60-day lookahead for rental events
- **Same-Owner Filter**: Ensures the transition is a genuine pivot, not a new buyer renting
- **Gross Yield**: (monthly rent x 12) / sale price, used for outlier detection and lead ranking

## Target Markets

High-value markets for accidental landlord analysis (from published research):

| Metro | AL Rate (Apr 2025) | YoY Change |
|---|---|---|
| Houston | 6.8% | +41.4% |
| Dallas | 5.1% | +32.3% |
| Phoenix | 4.5% | +11.3% |
| Tampa | 4.2% | +12.7% |
| Atlanta | 3.2% | +5.2% |
| Charlotte | 2.0% | -7.2% |
