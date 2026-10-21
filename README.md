# Kortix, the open-source AI Operating System: a Copilot Studio cost model

This repository prices a stated Copilot Studio workload on Microsoft's published rates. It is open source, reads two JSON files, counts the credits one interaction draws, multiplies by the interactions a month, and prints the pack total beside the pay-as-you-go total. Standard library only.

At a fixed 3,000 interactions a month the same support conversation bills at $30, $510 or $870, and only the agent's design changed. A comparison with an open-source alternative means something once both meters price the same workload.

## Run it

```bash
python3 cost_model.py
```

The three workloads in `workloads.json`:

```text
workload                                                 credits/interaction  credits/month  packs  pack route $    PAYG $
support agent, scripted answers                                          1.0           3000      1           200      30.0
support agent, grounded generative                                      17.0          51000      3           600     510.0
support agent, grounded generative on a reasoning model                 29.0          87000      4           800     870.0

Rates from Microsoft Learn, checked 2026-10-20: https://learn.microsoft.com/en-us/microsoft-copilot-studio/requirements-messages-management
Capacity pack: 25000 credits for $200 a month, no roll-over; pay-as-you-go $0.01 a credit.
```

## What separates the three rows

A classic answer costs 1 credit, a generative answer 2, an agent action 5, tenant graph grounding 10 a message, and an agent flow 13 per 100 actions.

Row one buys a scripted answer for each interaction: 3,000 credits a month. Row two generates the answer, grounds it in the tenant graph and takes one agent action, so 2 + 10 + 5 = 17 credits an interaction and 51,000 a month.

Row three keeps that agent and lets a reasoning model answer with 1,200 premium tokens. Microsoft bills a reasoning-model operation on two meters, the feature rate plus 10 credits per 1,000 premium tokens, and those tokens add 12 credits: 29 an interaction, 87,000 a month.

## Two ways to buy the same credits

A capacity pack is $200 a pack a month for 25,000 credits, and the pay-as-you-go meter is $0.01 a credit ([Microsoft's Copilot Studio licensing guidance](https://www.microsoft.com/licensing/guidance/microsoft-copilot-studio)). The script prints both routes and the pack route rounds up: 51,000 credits needs 3 packs, not 2.04.

Unused pack credits do not roll over to the next month, so a workload drawing 3,000 of its 25,000 pays $200 where the meter charges $30. Packs beat the meter above 20,000 credits a month. Credits are pooled across the tenant and drawn from packs before the meter, so a support agent shares its pack with everything else that runs on it.

## Price your own workload

Copy `workloads.json`, edit the copy, and pass its path:

```bash
python3 cost_model.py my_workload.json
```

A workload is a `name`, a `per_month` count and a `per_interaction` object. The `per_interaction` keys each read a rate from `rates.json`: `classic_answer`, `generative_answer`, `agent_action`, `tenant_graph_grounding`, `agent_flow_actions` (per 100), `content_pages`, and `premium_tokens_per_interaction`. A key you leave out counts as zero.

## Where the rates come from

`rates.json` holds the figures from Microsoft's [billing rates page](https://learn.microsoft.com/en-us/microsoft-copilot-studio/requirements-messages-management), checked 2026-10-20. The [capacity packs page](https://learn.microsoft.com/en-us/microsoft-365/copilot/pay-as-you-go/copilot-capacity-packs) covers the pack mechanics. Microsoft revises rates, so re-read them before relying on a figure and update `checked` when you do.

## What this does not model

- Voice, billed at 10, 35 and 75 credits a minute; the script has no voice key.
- Bring-your-own-model, which Microsoft's rate card excludes and bills separately.
- Interactions by a person on a Microsoft 365 Copilot plan, no charge on the feature rows.
- The annual pre-purchase plan and its tiered discounts.
- Your provider invoices or engineering time. This prices Microsoft's meter.

What a credit buys, and where the pack and meter routes land for two more workloads, is worked through on the campaign site: [what a Copilot Studio credit buys](https://opensourcecopilotalternative.com/copilot-studio-credits) and [Copilot Studio pricing](https://opensourcecopilotalternative.com/copilot-studio-pricing).

## The other meter

[Kortix](https://kortix.com) is the open-source AI Operating System, and its credits buy something different. From the [Kortix pricing](https://kortix.com/pricing) page: "Credits pay for the agent computer: the cloud machine where your agent runs code, browses and edits files. It bills per second while it runs and costs nothing while it is stopped." Model calls go to your own provider key or to the ChatGPT subscription you already pay for. Any model provider with your own keys. Open source. Read it, fork it, audit it. The code is at [Kortix on GitHub](https://github.com/kortix-ai/suna).
