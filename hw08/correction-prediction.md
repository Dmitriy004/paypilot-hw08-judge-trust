# Exact after-run prediction — before rubric.v2 calls

Frozen set2aad1fe9f81a; core d8a94d7a9e3ea91673e94ba7663cd82bab7136513beef739e5223c5e2fc630fe. Final primary model openrouter:openai/gpt-4.1-mini, fixed OpenAI endpoint only, temperature0.7, cap400, non-reasoning.

Observed baseline agreement27/30, stability29/30. Exact mismatches **PL-12, PL-14, PL-16**. The primary forecast predicted27/30 but wrongly named PL-18 instead of PL-16; preserve it unchanged.

Predict v2 changes majority **PL-12 and PL-14** from PASS to FAIL, leaves **PL-16** FAIL, all other27 case majorities unchanged. Predicted agreement **29/30**, exact remaining mismatch **PL-16**, false accept0/14, false reject1/16; predicted stability30/30. PL-20 had PPPPF in baseline and may remain unstable; do not relabel or hide it.

Only the explicit-actor clarification/version changes. Same30 recorded answers, five votes each; no second model/routing change, no result-selective reruns. This is an in-sample correction, not independent holdout evidence.
