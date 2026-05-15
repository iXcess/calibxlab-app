#!/usr/bin/env python3
"""Live API smoke tests against deployed Apps Script (production sheet)."""
from __future__ import annotations

import base64
import io
import json
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import date, datetime

GAS_URL = (
    "https://script.google.com/macros/s/"
    "AKfycby4kRi8q-94685lVVNWA9my0_UW-cE8HxiVgmLop9GygdXqxZuOyQ3TuZrpJjFXnzyi/exec"
)

# Minimal valid JPEG (red dot) — enough for Drive upload tests
_TEST_JPEG_B64 = (
    "/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkSEw8UHRof"
    "Hh0aHBwgJC4nICIsIxwcKDcpLDAxNDQ0Hyc5PTgyPC4zNDL/2wBDAQkJCQwLDBgNDRgyIRwh"
    "MjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjL/wAARCAAB"
    "AAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAn/xAAUEAEAAAAAAAAAAAAAAAAA"
    "AAAA/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMB"
    "AAIRAxEAPwCwAA8A/9k="
)


def _png_b64(w: int = 240, h: int = 120) -> str:
    from PIL import Image, ImageDraw

    im = Image.new("RGB", (w, h), (255, 255, 255))
    draw = ImageDraw.Draw(im)
    draw.rectangle([8, 8, w - 8, h - 8], outline=(26, 60, 94), width=2)
    draw.text((20, 40), "E2E receipt", fill=(14, 107, 68))
    buf = io.BytesIO()
    im.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode("ascii")


def gas_get(query: str):
    url = GAS_URL + "?" + query
    req = urllib.request.Request(url, method="GET")
    with urllib.request.urlopen(req, timeout=120) as resp:
        data = json.loads(resp.read().decode())
    if not data.get("ok", False):
        raise RuntimeError(data.get("error") or "Request failed")
    if "result" not in data:
        return None
    return data["result"]


def gas_post(action: str, payload: dict) -> dict:
    body = json.dumps({"action": action, "payload": payload}).encode("utf-8")
    req = urllib.request.Request(
        GAS_URL,
        data=body,
        method="POST",
        headers={"Content-Type": "text/plain;charset=utf-8"},
    )
    with urllib.request.urlopen(req, timeout=180) as resp:
        data = json.loads(resp.read().decode())
    if not data.get("ok", False):
        raise RuntimeError(data.get("error") or "Request failed")
    if "result" not in data:
        return None
    return data["result"]


def main() -> int:
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    failures: list[str] = []
    print("Calixlab live E2E —", stamp)

    try:
        trainers = gas_get("action=listTrainers")
        print("OK listTrainers:", len(trainers), "trainers")
        trainer = trainers[0] if trainers else "Test Trainer"
    except Exception as e:
        failures.append(f"listTrainers: {e}")
        trainer = "Test Trainer"

    client_name = None
    client_row = None
    try:
        hits = gas_get("action=lookupClient&q=E2E") or []
        if not hits:
            hits = gas_get("action=lookupClient&q=te") or []
        if hits:
            client_name = hits[0].get("fullName")
            client_row = hits[0].get("rowIndex")
            print("OK lookupClient:", client_name, "row", client_row)
        else:
            print("WARN lookupClient: no clients matched; session test may skip sheet row")
    except Exception as e:
        failures.append(f"lookupClient: {e}")

    # 1) Session log
    if client_name:
        try:
            sess = gas_post(
                "recordSessionLog",
                {
                    "sessionDate": date.today().isoformat(),
                    "trainer": trainer,
                    "client": client_name,
                    "sessionType": "PT",
                    "leadSource": "Calixlab",
                    "leadMultiplier": "0.60",
                    "sessionNumber": 1,
                    "clientConfirmed": True,
                    "clientSheetRow": client_row,
                    "packageInfo": "E2E package",
                    "signatureBase64": _TEST_JPEG_B64,
                    "signatureMimeType": "image/jpeg",
                    "signatureFileName": f"e2e-session-{stamp}.jpg",
                },
            )
            sig = sess.get("signatureFile") or ""
            print("OK recordSessionLog: row", sess.get("rowIndex"), "signatureFile=", sig or "(empty)")
            if not sess.get("rowIndex"):
                failures.append("recordSessionLog: missing rowIndex")
            if not sig:
                failures.append("recordSessionLog: signature not saved to Drive")
        except Exception as e:
            failures.append(f"recordSessionLog: {e}")
    else:
        failures.append("recordSessionLog: skipped (no client in sheet)")

    # 2) Onboarding with receipt + waiver signature
    onboard_name = f"E2E Agent {stamp}"
    receipt_b64 = _png_b64()
    onboard_row = None
    try:
        onboard = gas_post(
            "onboardClient",
            {
                "fullName": onboard_name,
                "phone": "0123456789",
                "email": f"e2e.{stamp}@example.com",
                "ic": "900101-01-0001",
                "emergencyContact": "E2E Contact",
                "emergencyPhone": "0198765432",
                "trainerName": trainer,
                "startDate": date.today().isoformat(),
                "fitnessLevel": "Beginner",
                "fitnessGoals": "Strength",
                "medicalConditions": "None",
                "packageType": "PT Package",
                "sessions": "8",
                "ratePerSession": "150",
                "totalPackageValue": "1200",
                "leadType": "Calixlab Lead",
                "paymentMode": "FPX",
                "instalmentPlan": "No",
                "totalInstalments": "",
                "instalmentAmount": "",
                "firstPaymentDate": "",
                "amountPaid": "600.00",
                "additionalPayments": "[]",
                "discoverySource": "E2E test",
                "notes": f"Automated test {stamp}",
                "receiptBase64": receipt_b64,
                "receiptFileName": f"e2e-receipt-{stamp}.png",
                "receiptMimeType": "image/png",
                "signatureBase64": _TEST_JPEG_B64,
                "signatureMimeType": "image/jpeg",
                "waiverDate": date.today().strftime("%d %B %Y"),
            },
        )
        onboard_row = onboard.get("rowIndex")
        print(
            "OK onboardClient:",
            onboard_name,
            "row",
            onboard_row,
            "folder",
            bool(onboard.get("folderUrl")),
        )
        if not onboard_row:
            failures.append("onboardClient: missing rowIndex")
    except Exception as e:
        failures.append(f"onboardClient: {e}")

    # 3) Invoice generation
    if onboard_row:
        try:
            inv = gas_post(
                "generateInvoice",
                {
                    "type": "onboarding",
                    "sheetRowIndex": onboard_row,
                    "saveToDrive": True,
                },
            )
            pdf_len = len(inv.get("pdfBase64") or "")
            print(
                "OK generateInvoice:",
                inv.get("invoiceNumber"),
                "pdf bytes",
                pdf_len,
                "drive",
                bool(inv.get("driveUrl")),
            )
            if pdf_len < 500:
                failures.append("generateInvoice: pdfBase64 too small")
            if not inv.get("invoiceNumber"):
                failures.append("generateInvoice: missing invoiceNumber")
        except Exception as e:
            failures.append(f"generateInvoice: {e}")
    else:
        failures.append("generateInvoice: skipped (onboarding failed)")

    print("---")
    if failures:
        print("FAILED:")
        for f in failures:
            print(" -", f)
        return 1
    print("All live E2E checks passed.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except urllib.error.HTTPError as e:
        print("HTTP error:", e.code, e.read().decode()[:500], file=sys.stderr)
        raise SystemExit(2)
