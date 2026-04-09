# Agent & Broker Analytics

Rank brokers and agents by motivated seller distress signals in luxury markets. Identifies underperforming listing agents and brokerages with distressed inventory, ideal for prospecting listing opportunities.

![Broker Analytics Demo](../../assets/gifs/broker-analytics_small.gif)

## What You Get

A formatted Excel workbook with 5 sheets:

- Executive summary with market-level KPIs and label distribution
- Full property listing sorted by distress signals
- Brokerage rankings with "vs Market Avg" delta scoring
- Agent rankings with the same scoring methodology
- Fire sale and motivated property detail with agent contact info

## Choose Your Path

### Basic (Copy & Paste)

Copy the prompt from [`basic/PROMPT.md`](basic/PROMPT.md) into Claude Code. Targets the Hamptons by default. Change the market name for any luxury market.

### Advanced (Skill)

Run `/broker-analytics [market name]` for a fully automated workbook with:

- Automated market geography resolution across multiple ZIP codes
- Motivated seller score aggregation at brokerage and agent level
- Conditional formatting with above/below market average highlighting
- Bundled Python script for consistent workbook generation

See the [skill definition](../../.claude/skills/broker-analytics/SKILL.md) for full details.

## How It Works

1. Resolve all ZIP codes and parcl_ids for the target luxury market
2. Pull all active for-sale listings with motivated seller scores
3. Filter to properties listed above $2M
4. Aggregate by brokerage and agent, rank by average motivated seller score
5. Agents/brokerages scoring above the market average are flagged as underperformers (listings sitting longer, cutting prices more, signaling more distress)
