# HW08 Judge Trust Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans. Inline execution, one fresh final review.

**Goal:** Complete and submit a reproducible30-case Judge Trust Statement satisfying all mentor checks.
**Architecture:** Keep official loader/parser/calibrator, reuse reviewed capture, freeze inputs and forecasts, audit all raw evidence, publish clean-clone-ready main.
**Tech Stack:** Python stdlib, Docker desktop-linux, OpenRouter, shared PayPilot, GitHub CLI, browser UI.
**Spec:** ../specs/2026-11-06-hw08-judge-trust-design.md

## Global Constraints

- No questions requested; proceed with specified approach and scoped publication approval.
- Exactly30 newly unjudged answers:10 obvious PASS,10 obvious FAIL,10 disputed; all labels/rationales fixed before calls. Same dataset before/after.
- Models/settings as spec; aggregate new usage <=$1 including prior lab0.054354895. Keys only process environment; billing baseline private.
- Original toolkit checks remain unchanged; chain-ready wrapper may make calibration agreement failures nonzero, never convert FAIL/SKIP to PASS.
- Forecasts/reference separate pre-run commits. Preserve negatives. Public main, no .env/secrets/private account totals.

## Review Focus

- Paid HTTP response survives malformed provider JSON and downstream parser/trace failure; test at transport boundary.
- All30 cases including hard/disputed FAIL remain in denominators; detect missing, duplicate and extra votes.
- Required evals/sets alias cannot silently diverge from sets input; compare byte hashes and frozen semantic core.
- Failure exits remain nonzero on offline clean clone, without provider keys or live stand.
- Provider reconciliation distinguishes rounded turn totals, exact span costs and total LLM calls; no false zero/unsupported cost guarantee.

### Task 1: Freeze blind reference and working split

**Files:** evals/sets/l09_labels.jsonl, sets/l09_labels.jsonl, sets/l09_escalation.jsonl, hw08/annotation-policy.md, hw08/manifest.json, hw08/prediction.md, hw08/test_reference.py.
**Interfaces:** source-compatible JSONL, core_hash(cases)->str; exactly30 unique IDs, source PL01..20 preserved, own10.

- [ ] RED: unittest asserts aliases exist/identical;10/10/10 strata; all labels,date,why_disputed/ground_truth_from; no judge criterion depends on trace/database/number.
- [ ] Construct references and five independent working judge views; source/tool cases retained separately. GREEN full suite.
- [ ] Commit labels/policy/manifest separately, then exact baseline prediction. Verify Git times before first paid call.

### Task 2: Reviewed capture and reproducible chain-ready path

**Files:** lab transport/audit helpers/tests reused from lab; judge.py dispatch; hw08/replay.py, hw08/test_gate.py, docker-compose.yml, .gitignore/.gitattributes.
**Interfaces:** complete(system,prompt,model,temp)->raw string; capture before parse; replay(report)->exit0 all agree else1, no paid calls; same loader.

- [ ] Incorporate Important/Critical lab reviewer fixes with offline RED→GREEN, keep parser/majority untouched. Test unknown costs and subsequent response retention.
- [ ] RED: nonzero replay on one failed calibration majority, no judge cases daily, both dataset aliases equal and stock loader accepts30. GREEN full suite.
- [ ] Docker dry-run offline, check model/version/settings; commit technical foundation.

### Task 3: Measure before and after one correction

**Files:** retained reports/evidence, hw08/correction-prediction.md, rubric/v2.md and changelog, independent summary.
**Interfaces:** official calibration reports and full raw responses; independent audit verifies5 votes/ID, same core and settings; Wilson case-level n30.

- [ ] Private starting usage/public prices; baseline30×5 with official calibrator, preserve invalid/error responses. Expected complete150 records or explicit stop with retained evidence.
- [ ] Analyze exact mismatch IDs/common features, confusion matrix and all strata; choose one observed class, commit clarification and forecast separately before after-run.
- [ ] Same30×5 after, no relabeling/result-selective reruns. Optional actual signed working cases only as needed, sequential reset/profile. Record clean failures rather than blaming D27 alone.
- [ ] Independently audit reports/raw votes/model/criterion/prompt hashes; GREEN offline suite; reconcile exact provider delta after settlement; restore stand if changed.

### Task 4: Statement, independent review, clean clone and submission

**Files:** judge-trust-statement.md, detailed calibration appendix, README, reproduction/evidence index, execution audit.
**Interfaces:** six decision lines plus risk table; every claim resolves to retained file; exact required public paths and main.

- [ ] Fill six concise decision rows and detailed seven-section evidence: metrics/intervals, errors, trade-off and owner/date risks. Explicitly small development set, no independent holdout.
- [ ] Run full suite, source/alias/core/hash/chronology/UTF8/link/secret checks and clean-clone offline replay with expected nonzero on mismatches; stage explicit task paths.
- [ ] One fresh final reviewer against complete branch; one Important/Critical RED→GREEN fix pass. Commit, no fabricated chronology or author attestation.
- [ ] Create public Dmitriy004/paypilot-hw08-judge-trust, push main, verify GitHub API visibility/HEAD/required blobs, fill GoIT URL and submit; verify visible submitted state.

## Self-review

All mandatory five stages and six mentor criteria map to Tasks1–4; no optional model comparison needed. Previous lab outputs are separate and not counted as newly blind homework cases. Questions/design gate waived explicitly by user. Separate clone provides isolation; publication authorized, secrets excluded. Native execution minimizes repeated context while final fresh review covers independent correctness.
