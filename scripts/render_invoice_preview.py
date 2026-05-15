#!/usr/bin/env python3
"""Render a sample invoice HTML/PDF locally (same layout as InvoiceTemplate.html)."""
from __future__ import annotations

import base64
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT_HTML = ROOT / "invoice" / "preview-sample.html"
OUT_PDF = ROOT / "invoice" / "preview-sample.pdf"
LOGO = ROOT / "assets" / "calixlab-logo-header.png"
STYLES = (ROOT / "apps-script" / "InvoiceTemplate.html").read_text(encoding="utf-8")
STYLES = STYLES.split("<style>", 1)[1].split("</style>", 1)[0]


def logo_data_uri() -> str:
    return "data:image/png;base64," + base64.b64encode(LOGO.read_bytes()).decode("ascii")


def build_html() -> str:
    m = {
        "companyLegal": "CALIXLAB EMPIRE",
        "companyDisplay": "Cali Lab",
        "companyAddress": [
            "D-G-53A, 10 Boulevard, Jalan Cempaka",
            "Kg. Sg. Kayu Ara, PJU 6A, Petaling Jaya",
            "47400 Selangor, Malaysia",
        ],
        "logoDataUri": logo_data_uri(),
        "billName": "Alexandra Chen",
        "billContact": "Tel: 012-345 6789 · alex.chen@example.com · IC: 901212-14-5678",
        "invoiceNumber": "CL-INV-00199",
        "invoiceDate": "15 May 2026",
        "dueDate": "15 May 2026",
        "terms": "Due on Receipt",
        "balanceDue": "MYR900.00",
        "lineItems": [
            {
                "index": 1,
                "description": "PT Package (12 sessions) · 12 session(s) w/ Sarah",
                "qty": "12.00",
                "rate": "150.00",
                "amount": "1,800.00",
            }
        ],
        "subTotal": "1,800.00",
        "taxNote": "(Tax Inclusive)",
        "total": "MYR1,800.00",
        "paymentMade": "(-) 900.00",
        "notesHtml": (
            "All payments shall be made to:<br><strong>CALIXLAB EMPIRE</strong><br>"
            "HONG LEONG BANK<br>05100348131"
        ),
        "termsList": [
            "Validity of Package: 6 months from first session",
            "Payment before any booking of classes",
        ],
    }
    addr = "".join(f"<p>{line}</p>\n      " for line in m["companyAddress"])
    lines = "".join(
        f"""      <tr>
        <td>{li['index']}</td>
        <td class="desc">{li['description']}</td>
        <td class="r">{li['qty']}</td>
        <td class="r">{li['rate']}</td>
        <td class="r">{li['amount']}</td>
      </tr>\n"""
        for li in m["lineItems"]
    )
    terms = "".join(f"<li>{t}</li>\n        " for t in m["termsList"])
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>{m['invoiceNumber']} — Invoice Preview</title>
<style>
{STYLES}
body {{ max-width: 820px; margin: 0 auto; }}
</style>
</head>
<body>
  <motion class="inv-top">
    <div class="inv-co">
      <h1>{m['companyLegal']}</h1>
      {addr}
    </div>
    <div class="inv-brand">
      <img src="{m['logoDataUri']}" alt="{m['companyDisplay']}"/>
    </div>
  </div>
  <div class="inv-meta-row">
    <div class="inv-bill">
      <h2>Bill To</h2>
      <div class="name">{m['billName']}</div>
      <div class="sub">{m['billContact']}</div>
    </div>
    <div class="inv-badge">
      <div class="lbl">INVOICE</div>
      <div class="num"># {m['invoiceNumber']}</div>
      <div class="inv-balance">
        <div class="bl">Balance Due</div>
        <motion class="bv">{m['balanceDue']}</div>
      </div>
    </div>
  </div>
  <div class="inv-dates" style="margin-bottom:20px;">
    <div><strong>Invoice Date:</strong> {m['invoiceDate']}</div>
    <div><strong>Due Date:</strong> {m['dueDate']}</motion>
    <div><strong>Terms:</strong> {m['terms']}</motion>
  </div>
  <table class="inv-lines">
    <thead>
      <tr>
        <th style="width:36px;">#</th>
        <th>Item &amp; Description</th>
        <th class="r" style="width:56px;">Qty</th>
        <th class="r" style="width:88px;">Rate</th>
        <th class="r" style="width:96px;">Amount</th>
      </tr>
    </thead>
    <tbody>
{lines}
    </tbody>
  </table>
  <table class="inv-totals">
    <tr><td>Sub Total</td><td>{m['subTotal']}</td></tr>
    <tr><td>{m['taxNote']}</td><td></td></tr>
    <tr class="total"><td>Total</td><td>{m['total']}</td></tr>
    <tr class="pay"><td>Payment Made</td><td>{m['paymentMade']}</td></tr>
    <tr class="bal"><td>Balance Due</td><td>{m['balanceDue']}</td></tr>
  </table>
  <div class="inv-foot">
    <div>
      <h3>Notes</h3>
      <p>{m['notesHtml']}</p>
    </div>
    <div>
      <h3>Terms &amp; Conditions</h3>
      <ul>
        {terms}
      </ul>
    </div>
  </div>
  <div class="inv-powered">Cali Lab · Trainer Hub</div>
</body>
</html>"""


def main() -> int:
    html = build_html().replace("<motion ", "<div ").replace("</motion>", "</motion>").replace("</motion>", "</motion>")
    while "<motion " in html or "</motion>" in html:
        html = html.replace("<motion ", "<div ").replace("</motion>", "</div>")
    OUT_HTML.write_text(html, encoding="utf-8")
    print("Wrote", OUT_HTML)
    try:
        subprocess.run(
            [
                "google-chrome",
                "--headless=new",
                "--disable-gpu",
                f"--print-to-pdf={OUT_PDF}",
                OUT_HTML.as_uri(),
            ],
            check=True,
            capture_output=True,
            timeout=45,
        )
        print("Wrote", OUT_PDF)
    except (FileNotFoundError, subprocess.CalledProcessError) as e:
        print("PDF skipped:", e, file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
