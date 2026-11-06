# Rubric history

- rubric.v1: original self-contained criteria, unchanged SYSTEM/parser/majority. Baseline fixed before homework judge calls.
- rubric.v2: append v2.md through JUDGE_RUBRIC_APPEND; clarify identified human actor vs unspecified process words. Observed v1 errors PL-12/14 were PASS5/5 though no human actor was named. No change to answers, labels, criteria, SYSTEM, parser, majority, model, route or decoding settings. PL-16 effort/outcome ambiguity is a different class and deliberately not targeted.

Price: a legitimate internal workflow may use "escalated" as a documented human-queue transition, but the text-only judge now rejects that shorthand unless the answer names the actor. A real tool call still needs a separate span check; do not let the judge infer database state. Independent unseen workflow language has not been validated. Token cost and observed error redistribution must be measured on the unchanged30-case set.
