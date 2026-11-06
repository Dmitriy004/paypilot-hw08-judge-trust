# Operational restart before complete baseline

The default OpenRouter route stopped twice with upstream shared-pool HTTP429: first after40 accepted votes, then after10 more. All50 accepted votes and both HTTP errors are retained under hw08/evidence/pilot, with their original phase/timestamps. These partial calls covered only PL-01…10 (obvious cases), not the disputed third. There was no complete calibration report and no selection based on disagreement results.

A neutral non-dataset route check succeeded on google-ai-studio/priority, still google/gemini-2.5-flash. Public endpoint pricing snapshot: input$0.54/M, output$4.50/M,1.8× standard. Sources: https://openrouter.ai/api/v1/models/google/gemini-2.5-flash/endpoints and https://openrouter.ai/docs/guides/routing/provider-selection . Route-check evidence is also archived, including its cost.

To keep the before/after comparison controlled, restart the entire30×5 baseline on this fixed priority endpoint, then use the exact same endpoint/settings for after. Do not mix the50 pilot votes into the primary denominator; include their costs in the total. Labels, answers, criteria, final set and exact-ID forecast remain unchanged. Explicitly disable fallback and require decoding parameters. No model substitution.

Main new-run guard$0.85 leaves room below the previously approved aggregate$1 even after prior lab$0.054354895, pilot charges and operational error reserves. The guard is not a provider-enforced cap for arbitrary large workloads; this experiment uses short fixed prompts and output400. No hidden retries; successful prefix can be replayed only with identical prompt/settings if another transport interruption occurs.

## Final primary configuration after priority also failed

Priority accepted17 dataset votes, then returned the same upstream429. Archive these17 and the third refusal as well. A second neutral probe succeeded for openai/gpt-4.1-mini on endpoint openai. Final full baseline and after use this same different judge model, fixed endpoint, temperature0.7, output400. GPT-4.1 mini has no reasoning step, so the unsupported reasoning parameter is omitted, not silently changed mid-run. Official model reference: https://developers.openai.com/api/docs/models/gpt-4.1-mini ; endpoint support/prices: https://openrouter.ai/api/v1/models/openai/gpt-4.1-mini/endpoints . New exact-ID prediction is prediction-gpt41.md, committed before the first GPT homework case.

All67 partial Gemini dataset votes concerned PL-01…10, still no disputed-third outcomes. These operational pilots are retained and charged in the total, never mixed into the final30-case denominator. Both neutral probes are retained too. This is a controlled restart due availability, not an accuracy-based model selection.
