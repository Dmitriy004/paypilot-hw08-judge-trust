# Execution audit · HW08

## Scope and decisions

-30 previously unjudged answers, not the already scored laboratory cases: avoids retrospectively calling an observed label blind. Cost: a separate experiment.
-Canonical evals/sets plus byte-identical runtime alias: assignment path and unchanged loader both work. Cost: synchronization enforced by tests.
-Questions/design approval waived by explicit user instruction; publication and LMS submission authorized. Cost: defaults selected without another approval round.
-Gemini full phases could not complete after three upstream429s. All67 partial obvious-case votes and probes retained; both primary phases fixed to GPT-4.1 mini before any disputed outcome. Cost: extra pilots and different model-specific trust scope.
-Malformed working judge output is schema FAIL, never repaired or silently retried. Replay retained paid turns after an interruption. Cost: replay elapsed is not live latency, duplicate trace copies must be deduplicated by actual request_id.
-No second accuracy-seeking rubric edit after the one measured correction. Cost: the final gate remains negative and both new false rejects stay visible.

## Verification

At measured-evidence commit `74cfe94`, a fresh local clone contained no .env and ran27/27 offline tests, raw-evidence analysis, and replay exit1. Both datasets loaded in Docker dry-run; Docker tests27/27 and replay exit1. Native Windows regeneration changed only working-copy newline encoding (no semantic diff).

Fresh whole-branch review independently reproduced the references,150 distinct generations per primary phase,374 distinct accepted judge generations, metrics,29 unique agent turns and exact provider cost. It found two Important validation gaps, no Critical or Minor findings:

1. Incomplete/duplicated/relabelled reports could pass the offline gate. Regression removed actual PL-01/05/16 failures and produced exit0 before the fix; now invalid archives return2. Replay validates canonical/runtime bytes, manifest/core/set hashes, exact ID coverage, labels/disputed flags and five votes. Malformed JSON/report shapes also return2.
2. A copied provider generation could replace a missing vote while preserving count/votes/cost. Regression on actual baseline evidence failed before the fix; now missing/duplicate generation IDs are rejected both within a phase and across all accepted judge records used in accounting. Identical output text from distinct IDs remains valid.

Both fixes were made in one offline RED→GREEN pass without paid calls, relabeling or changing reported votes. Results:30/30 local tests; the complete after-report still returns exit1; raw analysis still reproduces27/30 agreement,29/30 stability for both phases and$0.100849845.

The final clean-clone check also exposed newline normalization of the working JSONL: live byte hash70f163adf8c1 became2cce8501487e on checkout, although parsed cases were identical. An assertion against the retained report failed on that clone. The exact originally measured bytes are now stored with a specific `.gitattributes -text` rule, plus `test_working_set_byte_hash_matches_retained_live_reports`; no case or report was rewritten. Canonical calibration aliases remain LF and retain their frozen hash. The first dry-run check was repeated after removing an early-terminating stdout pipeline; both full-output dry-runs exited0.

## Review scope decisions

-Independent second annotator/holdout remains absent and explicitly disclosed. No generalized production reliability claim; cost if wrong: reference bias remains.
-Full seven-case clean comparison was not measured. Only2 action cases on clean; cost if wrong: no claim about clean judge quality.
-Additional models and paid reruns are optional and excluded. Cost if wrong: model-specific scope, not comparative superiority.
-Provider console was not independently opened for billing verification. API-key delta with no-concurrency assumption is disclosed; cost if wrong: concurrent key usage would contaminate the delta.
-Official quote/parser semantics remain unchanged. Nonverbatim working quote is flagged separately, not silently repaired; cost if wrong: runner PASS is not a validated evidence-contract PASS.
-Publication/submission are completion steps, not evidence already present at reviewed commit74cfe94. Their final status is reported only after verification.

Deferred minors: none from this homework review.
