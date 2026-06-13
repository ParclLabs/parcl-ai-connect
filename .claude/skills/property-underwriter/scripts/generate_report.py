#!/usr/bin/env python3
"""
Property Underwriting Report Generator
Generates a polished dark-themed HTML dashboard from a JSON data file.

Usage:
    python3 generate_report.py --data report_data.json --output report.html
"""

import argparse
import json
import sys
from datetime import datetime


def build_html(d: dict) -> str:
    s = d["subject"]
    pi = d["price_index"]
    cs = d["comp_sales"]
    cr = d["comp_rentals"]
    m = d["metrics"]

    index_name = pi.get("index_name", f"ZIP {s['zip']}")

    total_appr = (pi["imputed_value"] - s["last_sale_price"]) / s["last_sale_price"] * 100
    appr_class = "pos" if total_appr >= 0 else "neg"
    appr_sign = "+" if total_appr >= 0 else ""

    implied_ppsf = pi["imputed_value"] / max(int(float(s["sqft"])), 1)
    ref_ppsf = s["last_sale_price"] / max(int(float(s["sqft"])), 1)

    # --- Prior sale row ---
    prior_note = ""
    if s.get("prior_sale_price"):
        prior_appr = (s["last_sale_price"] - s["prior_sale_price"]) / s["prior_sale_price"] * 100
        prior_note = f"""<div class="detail-row">
            <span class="detail-label">Prior Sale</span>
            <span class="detail-value">${s['prior_sale_price']:,.0f} on {s['prior_sale_date']} ({prior_appr:+.1f}%)</span>
        </div>"""

    # --- Comp sale rows ---
    sale_rows = ""
    for c in cs.get("top_comps", [])[:15]:
        sale_rows += f"""<tr>
            <td>{c['address']}</td>
            <td>{c.get('city','')}, {c.get('zip','')}</td>
            <td>{c.get('beds','')}/{c.get('baths','')}</td>
            <td>{c.get('sqft','')}</td>
            <td>{c.get('year_built','')}</td>
            <td class="money">${c['price']:,.0f}</td>
            <td class="money">${c.get('ppsf',0):,.2f}</td>
            <td>{c['date']}</td>
        </tr>"""

    # --- Comp rental rows ---
    rental_rows = ""
    for c in cr.get("top_comps", [])[:15]:
        rental_rows += f"""<tr>
            <td>{c['address']}</td>
            <td>{c.get('city','')}, {c.get('zip','')}</td>
            <td>{c.get('beds','')}/{c.get('baths','')}</td>
            <td>{c.get('sqft','')}</td>
            <td class="money">${c['rent']:,.0f}/mo</td>
            <td>{c['date']}</td>
        </tr>"""

    # --- Chart data (handles both dict and list-of-tuples formats) ---
    chart_data = pi.get("monthly_chart_data", pi.get("recent_data", []))
    if chart_data and isinstance(chart_data[0], dict):
        pi_labels = json.dumps([p["date"] for p in chart_data])
        pi_values = json.dumps([p["value"] for p in chart_data])
    elif chart_data and isinstance(chart_data[0], (list, tuple)):
        pi_labels = json.dumps([p[0] for p in chart_data])
        pi_values = json.dumps([p[1] for p in chart_data])
    else:
        pi_labels = json.dumps([])
        pi_values = json.dumps([])
    bucket_labels = json.dumps([b[0] for b in cs.get("price_buckets", [])])
    bucket_values = json.dumps([b[1] for b in cs.get("price_buckets", [])])

    # --- Property type display ---
    ptype = s.get("property_type", "SINGLE_FAMILY").replace("_", " ").title()

    # --- Comp position ---
    comp_position = "above" if implied_ppsf > cs["median_ppsf"] else "below"

    # --- Date for footer ---
    gen_date = datetime.now().strftime("%B %d, %Y")

    # --- Build methodology ---
    methodology = f"""<p><strong>Valuation Methodology:</strong> The imputed current value of <strong>${pi['imputed_value']:,.0f}</strong> is derived by applying the Parcl Labs Sale Price Index ({index_name}) percentage change from the sale date ({pi['pi_sale_date_used']}, ${pi['pi_at_sale_date']:.2f}/sqft) to the most recent observation ({pi['pi_current_date']}, ${pi['pi_current']:.2f}/sqft), representing a <strong>{pi['pct_change']:+.2f}%</strong> change, against the last recorded sale price of ${s['last_sale_price']:,.0f}.</p>"""

    methodology += f"""<br/><p><strong>Comparable Analysis:</strong> {cs['count']} arm's-length single-family sales and {cr['count']} single-family rental listings were captured within a 3-mile radius over the trailing 6 months. The subject's implied $/sqft (${implied_ppsf:,.2f}) is {comp_position} the comp median of ${cs['median_ppsf']:.2f}/sqft.</p>"""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Underwriting Report — {s['address']}, {s['city']}, {s['state']} {s['zip']}</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.min.js"></script>
<style>
  :root {{
    --navy: #0f1a2e;
    --dark: #1a2740;
    --accent: #3b82f6;
    --accent2: #06b6d4;
    --green: #10b981;
    --amber: #f59e0b;
    --red: #ef4444;
    --surface: #1e2d45;
    --surface2: #243351;
    --border: #2d3f5e;
    --text: #e2e8f0;
    --muted: #94a3b8;
    --white: #ffffff;
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    background: var(--navy);
    color: var(--text);
    line-height: 1.5;
    padding: 0;
  }}
  .header {{
    background: linear-gradient(135deg, var(--dark) 0%, #0c1322 100%);
    border-bottom: 1px solid var(--border);
    padding: 28px 40px;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }}
  .header-left h1 {{ font-size: 22px; font-weight: 700; color: var(--white); letter-spacing: -0.3px; }}
  .header-left .subtitle {{ color: var(--muted); font-size: 13px; margin-top: 2px; }}
  .header-right {{ text-align: right; font-size: 12px; color: var(--muted); }}
  .badge {{
    display: inline-block; padding: 3px 10px; border-radius: 20px;
    font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px;
  }}
  .badge-sf {{ background: rgba(59,130,246,0.15); color: var(--accent); border: 1px solid rgba(59,130,246,0.3); }}
  .badge-warn {{ background: rgba(245,158,11,0.15); color: var(--amber); border: 1px solid rgba(245,158,11,0.3); }}
  .badge-green {{ background: rgba(16,185,129,0.15); color: var(--green); border: 1px solid rgba(16,185,129,0.3); }}
  .container {{ max-width: 1280px; margin: 0 auto; padding: 24px 40px 60px; }}
  .kpi-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 24px; }}
  .kpi-card {{
    background: var(--surface); border: 1px solid var(--border); border-radius: 10px;
    padding: 20px; position: relative; overflow: hidden;
  }}
  .kpi-card::before {{ content: ''; position: absolute; top: 0; left: 0; right: 0; height: 3px; }}
  .kpi-card.blue::before {{ background: var(--accent); }}
  .kpi-card.cyan::before {{ background: var(--accent2); }}
  .kpi-card.green::before {{ background: var(--green); }}
  .kpi-card.amber::before {{ background: var(--amber); }}
  .kpi-label {{ font-size: 11px; text-transform: uppercase; letter-spacing: 0.8px; color: var(--muted); margin-bottom: 6px; font-weight: 600; }}
  .kpi-value {{ font-size: 26px; font-weight: 700; color: var(--white); }}
  .kpi-sub {{ font-size: 12px; color: var(--muted); margin-top: 4px; }}
  .kpi-change {{ font-weight: 600; }}
  .kpi-change.pos {{ color: var(--green); }}
  .kpi-change.neg {{ color: var(--red); }}
  .section {{ margin-bottom: 24px; }}
  .section-title {{
    font-size: 14px; font-weight: 700; text-transform: uppercase; letter-spacing: 1px;
    color: var(--muted); margin-bottom: 14px; padding-bottom: 8px; border-bottom: 1px solid var(--border);
  }}
  .grid-2 {{ display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }}
  .card {{ background: var(--surface); border: 1px solid var(--border); border-radius: 10px; padding: 22px; }}
  .card-title {{ font-size: 13px; font-weight: 700; color: var(--accent); text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 14px; }}
  .detail-row {{
    display: flex; justify-content: space-between; padding: 7px 0;
    border-bottom: 1px solid rgba(45,63,94,0.5); font-size: 13px;
  }}
  .detail-row:last-child {{ border-bottom: none; }}
  .detail-label {{ color: var(--muted); }}
  .detail-value {{ font-weight: 600; color: var(--white); text-align: right; }}
  .table-wrap {{ overflow-x: auto; }}
  table {{ width: 100%; border-collapse: collapse; font-size: 12px; }}
  th {{
    text-align: left; padding: 10px 12px; background: var(--surface2); color: var(--muted);
    font-weight: 600; text-transform: uppercase; font-size: 10px; letter-spacing: 0.7px;
    border-bottom: 2px solid var(--border); white-space: nowrap;
  }}
  td {{ padding: 9px 12px; border-bottom: 1px solid rgba(45,63,94,0.4); white-space: nowrap; }}
  tr:hover td {{ background: rgba(59,130,246,0.04); }}
  .money {{ text-align: right; font-variant-numeric: tabular-nums; font-weight: 500; }}
  .chart-container {{ position: relative; height: 220px; }}
  .methodology {{
    background: var(--surface); border: 1px solid var(--border); border-radius: 10px;
    padding: 20px; font-size: 12px; color: var(--muted); line-height: 1.7;
  }}
  .methodology strong {{ color: var(--text); }}
  .footer {{
    text-align: center; padding: 24px; color: var(--muted); font-size: 11px;
    border-top: 1px solid var(--border); margin-top: 32px;
  }}
</style>
</head>
<body>

<div class="header">
  <div class="header-left">
    <h1>{s['address']}, {s['city']}, {s['state']} {s['zip']}</h1>
    <div class="subtitle">{s.get('county','')} &bull; {s.get('metro','')} &bull; <span class="badge badge-sf">{ptype}</span></div>
  </div>
  <div class="header-right">
    <div style="font-size:14px;color:var(--white);font-weight:700;">Lender Underwriting Report</div>
    <div>{gen_date} &bull; Parcl Labs Data</div>
  </div>
</div>

<div class="container">

  <div class="kpi-grid">
    <div class="kpi-card blue">
      <div class="kpi-label">Imputed Current Value</div>
      <div class="kpi-value">${pi['imputed_value']:,.0f}</div>
      <div class="kpi-sub"><span class="kpi-change {appr_class}">{appr_sign}{total_appr:.1f}%</span> since last sale</div>
    </div>
    <div class="kpi-card cyan">
      <div class="kpi-label">Last Sale Price</div>
      <div class="kpi-value">${s['last_sale_price']:,.0f}</div>
      <div class="kpi-sub">{s['last_sale_date']}</div>
    </div>
    <div class="kpi-card green">
      <div class="kpi-label">Est. Market Rent</div>
      <div class="kpi-value">${cr['median_rent']:,.0f}<span style="font-size:14px;color:var(--muted)">/mo</span></div>
      <div class="kpi-sub">Gross Yield: {m['gross_yield']:.2f}%</div>
    </div>
    <div class="kpi-card amber">
      <div class="kpi-label">Price Index ($/sqft)</div>
      <div class="kpi-value">${pi['pi_current']:.2f}</div>
      <div class="kpi-sub">{index_name}</div>
    </div>
  </div>

  <div class="section">
    <div class="section-title">Subject Property &amp; Valuation</div>
    <div class="grid-2">
      <div class="card">
        <div class="card-title">Property Details</div>
        <div class="detail-row"><span class="detail-label">Address</span><span class="detail-value">{s['address']}, {s['city']}, {s['state']} {s['zip']}</span></div>
        <div class="detail-row"><span class="detail-label">Type</span><span class="detail-value">{ptype}</span></div>
        <div class="detail-row"><span class="detail-label">Bedrooms / Bathrooms</span><span class="detail-value">{s['beds']} BD / {s['baths']} BA</span></div>
        <div class="detail-row"><span class="detail-label">Living Area</span><span class="detail-value">{int(float(s['sqft'])):,} sqft</span></div>
        <div class="detail-row"><span class="detail-label">Year Built</span><span class="detail-value">{s['year_built']}</span></div>
        <div class="detail-row"><span class="detail-label">Coordinates</span><span class="detail-value">{s['lat']}, {s['lon']}</span></div>
      </div>
      <div class="card">
        <div class="card-title">Valuation Analysis</div>
        <div class="detail-row"><span class="detail-label">Last Sale</span><span class="detail-value">${s['last_sale_price']:,.0f} ({s['last_sale_date']})</span></div>
        {prior_note}
        <div class="detail-row"><span class="detail-label">Price Index at Baseline</span><span class="detail-value">${pi['pi_at_sale_date']:.2f}/sqft ({pi['pi_sale_date_used']})</span></div>
        <div class="detail-row"><span class="detail-label">Price Index Current</span><span class="detail-value">${pi['pi_current']:.2f}/sqft ({pi['pi_current_date']})</span></div>
        <div class="detail-row"><span class="detail-label">Index Change</span><span class="detail-value" style="color:var({'--green' if pi['pct_change'] >= 0 else '--red'})">{pi['pct_change']:+.2f}%</span></div>
        <div class="detail-row"><span class="detail-label">Imputed Current Value</span><span class="detail-value" style="color:var(--accent);font-size:16px;font-weight:700">${pi['imputed_value']:,.0f}</span></div>
        <div class="detail-row"><span class="detail-label">Implied $/sqft (Subject)</span><span class="detail-value">${implied_ppsf:,.2f}</span></div>
        <div class="detail-row"><span class="detail-label">Comp Median $/sqft</span><span class="detail-value">${cs['median_ppsf']:.2f}</span></div>
        <div class="detail-row"><span class="detail-label">Est. Monthly Rent</span><span class="detail-value">${cr['median_rent']:,.0f}</span></div>
        <div class="detail-row"><span class="detail-label">Gross Rental Yield</span><span class="detail-value">{m['gross_yield']:.2f}%</span></div>
        <div class="detail-row"><span class="detail-label">Rent-to-Value Ratio</span><span class="detail-value">{m['monthly_rent_to_value']:.3f}%</span></div>
      </div>
    </div>
  </div>

  <div class="section">
    <div class="section-title">Market Trends — {index_name}</div>
    <div class="grid-2">
      <div class="card">
        <div class="card-title">Sale Price Index ($/sqft)</div>
        <div class="chart-container"><canvas id="piChart"></canvas></div>
      </div>
      <div class="card">
        <div class="card-title">Comp Sale Price Distribution (6-Mo, 3-Mi Radius)</div>
        <div class="chart-container"><canvas id="distChart"></canvas></div>
      </div>
    </div>
  </div>

  <div class="section">
    <div class="section-title">Comparable Sales — {ptype}, 3-Mile Radius, Last 6 Months ({cs['count']} transactions)</div>
    <div class="card" style="padding:0;overflow:hidden;">
      <div style="padding:16px 20px;display:flex;gap:28px;border-bottom:1px solid var(--border);font-size:12px;">
        <span><span class="detail-label">Median:</span> <strong>${cs['median_price']:,.0f}</strong></span>
        <span><span class="detail-label">Mean:</span> <strong>${cs['mean_price']:,.0f}</strong></span>
        <span><span class="detail-label">Range:</span> <strong>${cs['min_price']:,.0f} &ndash; ${cs['max_price']:,.0f}</strong></span>
        <span><span class="detail-label">Median $/sqft:</span> <strong>${cs['median_ppsf']:.2f}</strong></span>
      </div>
      <div class="table-wrap">
        <table>
          <thead><tr><th>Address</th><th>Location</th><th>Bd/Ba</th><th>Sqft</th><th>Year</th><th style="text-align:right">Price</th><th style="text-align:right">$/Sqft</th><th>Date</th></tr></thead>
          <tbody>{sale_rows}</tbody>
        </table>
      </div>
    </div>
  </div>

  <div class="section">
    <div class="section-title">Comparable Rentals — {ptype}, 3-Mile Radius, Last 6 Months ({cr['count']} listings)</div>
    <div class="card" style="padding:0;overflow:hidden;">
      <div style="padding:16px 20px;display:flex;gap:28px;border-bottom:1px solid var(--border);font-size:12px;">
        <span><span class="detail-label">Median Rent:</span> <strong>${cr['median_rent']:,.0f}/mo</strong></span>
        <span><span class="detail-label">Mean Rent:</span> <strong>${cr['mean_rent']:,.0f}/mo</strong></span>
        <span><span class="detail-label">Range:</span> <strong>${cr['min_rent']:,.0f} &ndash; ${cr['max_rent']:,.0f}</strong></span>
      </div>
      <div class="table-wrap">
        <table>
          <thead><tr><th>Address</th><th>Location</th><th>Bd/Ba</th><th>Sqft</th><th style="text-align:right">Rent</th><th>Date</th></tr></thead>
          <tbody>{rental_rows}</tbody>
        </table>
      </div>
    </div>
  </div>

  <div class="section">
    <div class="section-title">Methodology &amp; Risk Notes</div>
    <div class="methodology">
      {methodology}
    </div>
  </div>

  <div class="footer">
    Parcl Labs Underwriting Report &bull; {gen_date} &bull; For risk management and underwriting purposes only
  </div>
</div>

<script>
const piCtx = document.getElementById('piChart').getContext('2d');
new Chart(piCtx, {{
  type: 'line',
  data: {{
    labels: {pi_labels},
    datasets: [{{
      label: '$/sqft',
      data: {pi_values},
      borderColor: '#3b82f6',
      backgroundColor: 'rgba(59,130,246,0.08)',
      fill: true, tension: 0.3, pointRadius: 0, borderWidth: 2
    }}]
  }},
  options: {{
    responsive: true, maintainAspectRatio: false,
    plugins: {{
      legend: {{ display: false }},
      tooltip: {{
        backgroundColor: '#1e2d45', titleColor: '#94a3b8', bodyColor: '#e2e8f0',
        borderColor: '#2d3f5e', borderWidth: 1,
        callbacks: {{ label: ctx => '$' + ctx.parsed.y.toFixed(2) + '/sqft' }}
      }}
    }},
    scales: {{
      x: {{ ticks: {{ color: '#64748b', maxTicksLimit: 8, font: {{ size: 10 }} }}, grid: {{ color: 'rgba(45,63,94,0.3)' }} }},
      y: {{ ticks: {{ color: '#64748b', callback: v => '$' + v, font: {{ size: 10 }} }}, grid: {{ color: 'rgba(45,63,94,0.3)' }} }}
    }}
  }}
}});

const distCtx = document.getElementById('distChart').getContext('2d');
new Chart(distCtx, {{
  type: 'bar',
  data: {{
    labels: {bucket_labels},
    datasets: [{{
      label: 'Sales',
      data: {bucket_values},
      backgroundColor: 'rgba(6,182,212,0.6)', borderColor: 'rgba(6,182,212,0.9)',
      borderWidth: 1, borderRadius: 3
    }}]
  }},
  options: {{
    responsive: true, maintainAspectRatio: false,
    plugins: {{
      legend: {{ display: false }},
      tooltip: {{ backgroundColor: '#1e2d45', titleColor: '#94a3b8', bodyColor: '#e2e8f0', borderColor: '#2d3f5e', borderWidth: 1 }}
    }},
    scales: {{
      x: {{ ticks: {{ color: '#64748b', maxRotation: 45, font: {{ size: 9 }} }}, grid: {{ display: false }} }},
      y: {{ ticks: {{ color: '#64748b', font: {{ size: 10 }} }}, grid: {{ color: 'rgba(45,63,94,0.3)' }} }}
    }}
  }}
}});
</script>
</body>
</html>"""
    return html


def main():
    parser = argparse.ArgumentParser(description="Generate property underwriting HTML report")
    parser.add_argument("--data", required=True, help="Path to report_data.json")
    parser.add_argument("--output", required=True, help="Path for output HTML file")
    args = parser.parse_args()

    with open(args.data) as f:
        data = json.load(f)

    html = build_html(data)

    with open(args.output, "w") as f:
        f.write(html)

    print(f"Report generated: {args.output} ({len(html):,} bytes)")


if __name__ == "__main__":
    main()
