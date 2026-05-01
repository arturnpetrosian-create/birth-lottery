"""Скачать PNG флагов и сохранить base64 в data/flags_b64.json (без внешних запросов в приложении)."""
from __future__ import annotations

import base64
import json
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ISO_JSON = ROOT / "data" / "iso3_alpha2.json"
OUT_JSON = ROOT / "data" / "flags_b64.json"
URLS = (
    "https://flagcdn.com/w20/{a2}.png",
    "https://flagcdn.com/h20/{a2}.png",
)


def fetch_png(a2: str) -> bytes | None:
    for url_template in URLS:
        url = url_template.format(a2=a2)
        for attempt in range(4):
            try:
                req = urllib.request.Request(
                    url,
                    headers={"User-Agent": "birth-lottery-build/1.0"},
                )
                with urllib.request.urlopen(req, timeout=45) as resp:
                    return resp.read()
            except (urllib.error.URLError, OSError):
                time.sleep(1.0 + attempt * 0.5)
    return None


def main() -> int:
    if not ISO_JSON.is_file():
        print(f"Нет {ISO_JSON}", file=sys.stderr)
        return 1
    iso3_to_a2 = json.loads(ISO_JSON.read_text(encoding="utf-8"))
    a2_set = sorted({str(v).lower() for v in iso3_to_a2.values() if v})
    out: dict[str, str] = {}
    failed: list[str] = []
    for i, a2 in enumerate(a2_set):
        raw = fetch_png(a2)
        if raw is None:
            failed.append(a2)
            continue
        out[a2.upper()] = base64.standard_b64encode(raw).decode("ascii")
        if i % 25 == 24:
            time.sleep(0.2)
    if failed:
        print("Не скачались:", ", ".join(failed), file=sys.stderr)
    if not out:
        return 1
    OUT_JSON.write_text(json.dumps(out, separators=(",", ":")), encoding="utf-8")
    print(f"OK {len(out)}/{len(a2_set)} -> {OUT_JSON} (~{OUT_JSON.stat().st_size // 1024} KiB)")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
