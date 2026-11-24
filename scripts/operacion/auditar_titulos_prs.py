#!/usr/bin/env python3
"""Auditoría de títulos de pull requests de NETLAB360, sin mutaciones."""
from __future__ import annotations
import argparse
import json
import re
import subprocess
import sys

REPO = "recm0708/netlab360"
PATTERN = re.compile(r"^\[(S0[1-9]|S10|GESTIÓN)\] .{12,}$")
BAD_STATUS = re.compile(r"\s*[—–-]\s*(cerrad[oa]|pendiente|concluid[oa]|completad[oa])\s*$",re.I)


def check(prs: list[dict]) -> dict:
    if not isinstance(prs, list) or len(prs) < 129:
        raise ValueError("pr_inventory_short_or_invalid")
    numbers=set()
    bad=[]
    for pr in prs:
        number=pr["number"]
        if number in numbers:
            raise ValueError("duplicate_pr_number")
        numbers.add(number)
        title=pr.get("title","")
        if not PATTERN.fullmatch(title) or BAD_STATUS.search(title):
            bad.append((number,title))
    if bad:
        raise ValueError("non_normalized_prs: "+repr(bad[:10]))
    return {
        "total": len(prs),
        "open": sum(pr.get("state")=="open" for pr in prs),
        "merged": sum(pr.get("merged_at") is not None for pr in prs),
        "normalized": len(prs),
    }


def fetch() -> list[dict]:
    p=subprocess.run(
        ["gh","api","--paginate","--slurp",
         f"repos/{REPO}/pulls?state=all&per_page=100"],
        text=True,capture_output=True,timeout=120,check=False,
    )
    if p.returncode:
        raise RuntimeError("github_fetch_failed: "+p.stderr[-400:])
    data=json.loads(p.stdout)
    if not isinstance(data,list):
        raise ValueError("github_response_not_array")
    if data and isinstance(data[0],list):
        return [x for page in data for x in page]
    return data


def main() -> None:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check",action="store_true",required=True)
    parser.parse_args()
    result=check(fetch())
    print("========== NETLAB360 AUDITORIA DE PR ==========")
    print("PRS_TOTALES="+str(result["total"]))
    print("PRS_ABIERTOS="+str(result["open"]))
    print("PRS_FUSIONADOS="+str(result["merged"]))
    print("TITULOS_CON_FORMATO="+str(result["normalized"]))
    print("PRS_TITULOS_ES=OK")


if __name__ == "__main__":
    try: main()
    except (ValueError,KeyError,RuntimeError,OSError,
            subprocess.TimeoutExpired,json.JSONDecodeError) as exc:
        print("PRS_AUDITORIA_ERROR="+str(exc),file=sys.stderr)
        sys.exit(1)
