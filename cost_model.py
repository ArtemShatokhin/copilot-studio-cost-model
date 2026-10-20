"""Copilot Studio cost model.

Computes what a defined workload costs on Microsoft's Copilot Studio meter,
from Microsoft's published billing rates, and prints the prepaid-pack and
pay-as-you-go totals side by side.

Rates and billing facts: rates.json, read from Microsoft Learn (see its
"source" fields for the two pages and the date they were checked).
Method: credits_per_interaction * interactions_per_month -> credits per month;
then the pack route (ceil(credits / pack size) * pack price) and the
pay-as-you-go route (credits * per-credit price).

Run: python3 cost_model.py [workloads.json]
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def load(name: str):
    with open(HERE / name, encoding="utf-8") as fh:
        return json.load(fh)


def credits_per_interaction(rates: dict, spec: dict) -> float:
    c = rates["copilot_credits"]
    total = 0.0
    total += spec.get("classic_answer", 0) * c["classic_answer"]
    total += spec.get("generative_answer", 0) * c["generative_answer"]
    total += spec.get("agent_action", 0) * c["agent_action"]
    total += spec.get("tenant_graph_grounding", 0) * c["tenant_graph_grounding"]
    total += spec.get("agent_flow_actions", 0) / 100.0 * c["agent_flow_actions_per_100"]
    total += spec.get("content_pages", 0) * c["content_processing_per_page"]
    # A reasoning-model answer bills twice: the feature rate above, plus the
    # premium text/AI-tools rate for the tokens the model reads and writes.
    total += spec.get("premium_tokens_per_interaction", 0) / 1000.0 * c["text_ai_premium_per_1k_tokens"]
    return total


def monthly(workload: dict, rates: dict) -> dict:
    per = credits_per_interaction(rates, workload["per_interaction"])
    credits = per * workload["per_month"]
    billing = rates["billing"]
    pack_price = billing["capacity_pack_usd_per_month"]
    pack_size = billing["capacity_pack_credits"]
    packs = math.ceil(credits / pack_size) if credits else 0
    return {
        "workload": workload["name"],
        "interactions_per_month": workload["per_month"],
        "credits_per_interaction": round(per, 2),
        "credits_per_month": round(credits),
        "pack_route_usd": packs * pack_price,
        "packs": packs,
        "payg_route_usd": round(credits * billing["pay_as_you_go_usd_per_credit"], 2),
    }


def main(argv: list[str]) -> int:
    rates = load("rates.json")
    workloads = load(argv[1] if len(argv) > 1 else "workloads.json")
    rows = [monthly(w, rates) for w in workloads]
    width = max(len(r["workload"]) for r in rows)
    print(f"{'workload':<{width}}  {'credits/interaction':>19}  {'credits/month':>13}  {'packs':>5}  {'pack route $':>12}  {'PAYG $':>8}")
    for r in rows:
        print(f"{r['workload']:<{width}}  {r['credits_per_interaction']:>19}  {r['credits_per_month']:>13}  {r['packs']:>5}  {r['pack_route_usd']:>12}  {r['payg_route_usd']:>8}")
    print()
    print(f"Rates from Microsoft Learn, checked {rates['checked']}: {rates['source']}")
    print(f"Capacity pack: {rates['billing']['capacity_pack_credits']} credits for "
          f"${rates['billing']['capacity_pack_usd_per_month']} a month, no roll-over; "
          f"pay-as-you-go ${rates['billing']['pay_as_you_go_usd_per_credit']} a credit.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
