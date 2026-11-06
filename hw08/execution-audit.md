# Execution audit · HW08

## Scope and decisions

-30 previously unjudged answers, not the already scored laboratory cases: avoids retrospectively calling an observed label blind. Cost: a separate experiment.
-Canonical evals/sets plus byte-identical runtime alias: assignment path and unchanged loader both work. Cost: synchronization enforced by tests.
-Questions/design approval waived by explicit user instruction; publication and LMS submission authorized. Cost: defaults selected without another approval round.
-Gemini full phases could not complete after three upstream429s. All67 partial obvious-case votes and probes retained; both primary phases fixed to GPT-4.1 mini before any disputed outcome. Cost: extra pilots and different model-specific trust scope.
-Malformed working judge output is schema FAIL, never repaired or silently retried. Replay retained paid turns after an interruption. Cost: replay elapsed is not live latency, duplicate trace copies must be deduplicated by actual request_id.
-No second accuracy-seeking rubric edit after the one measured correction. Cost: the final gate remains negative and both new false rejects stay visible.

## Verification

Final clean-clone and review results are recorded below after execution. This file does not attest an unperformed check.
