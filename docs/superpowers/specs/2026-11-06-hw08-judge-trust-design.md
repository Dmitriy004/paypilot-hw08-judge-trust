# HW08 — Judge Trust Statement

## Intent and constraints

Complete all five stages and mentor chain-ready checks at GoIT lesson54593649/homework, then publish a separate public GitHub repository on main and submit its URL. User explicitly authorized execution, commits, publication and final submission without further questions. Do not add authorship claims or claim independent expert annotation.

Use official kit f5c235aa10a505f9d6f9e422ffd66917578c537b, shared stand74f1995ca8e8e64e4526e374535c2c4e71a2bde1. Preserve prior labs/homework and shared .env. Keep the previously approved $1 aggregate provider cap; prior lab cost0.054354895USD. Existing OpenRouter access, agent anthropic/claude-haiku-5.5. Initial Gemini pilot was interrupted three times by upstream429 (including priority); final full baseline/after use openrouter:openai/gpt-4.1-mini on the fixed openai endpoint, temperature0.7, output400, non-reasoning. All pilots and charges retained; same30 labels, no disputed pilot outcomes inspected. Main cap$0.85 leaves room for pilots/prior lab. Never publish keys, account totals or local IDE files.

## Approach

Reuse tested stdlib transport/capture from the lab after its final review; preserve the official parser, SYSTEM and majority rule. Avoid reusing the12 already-judged lab answers as a fresh blind reference: take20 unjudged pool cases and10 original clear cases, exactly10 obvious PASS/10 obvious FAIL/10 disputed. Freeze all labels and rationales before the first homework judge call. Commit an exact-ID forecast separately. Alternatives rejected: relabeling old lab answers after seeing votes would contaminate the reference; optional multi-model experiments add cost without meeting any missing mandatory requirement.

Canonical required dataset evals/sets/l09_labels.jsonl; byte-identical sets/l09_labels.jsonl serves the unchanged official loader/calibrator. Working sets/l09_escalation.jsonl has the daily/runs1 tool threshold plus control and at least five release/runs5 judge cases. Keep numerical/tool truth out of prose rubric; explicitly signed fixtures avoid the known unauthenticated kit incompatibility.

Run official tools/calibrate_run.py,30 cases×5 baseline; analyze systematic errors, version one targeted correction, commit its exact-ID forecast, repeat the same30×5. Preserve all attempts. Report agreement and stability separately, both Wilson95%, strata, confusion matrices, common-feature errors, exact quotes and evidence paths. Six decision lines at top of concise judge-trust-statement.md, detailed appendices elsewhere, L03-style owned/date-bound risks. No invented second annotator/holdout/production readiness.

Chain-ready: official loader loads both aliases; runner failure returns nonzero; judges never daily; model/rubric metadata matches reports. Prove offline replay, exit failure, Docker dry-run, clean-clone execution, secret scan, public main blobs and final LMS submitted state. Stop only for a concrete unresolved access/security/budget blocker; no generic approval loops.
