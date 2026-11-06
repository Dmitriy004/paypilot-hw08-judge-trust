# Working-run continuation audit

The first live lesson-09 run completed12 independent agent turns and obtained2 judge outputs. ESC-J02's paid output was malformed JSON; the stock runner aborted before writing its report. All agent responses, traces and raw judge output were already retained. The malformed response is not repaired or replaced and must count as a failed output contract.

The first continuation exposed an additional harness issue: cached live judge calls receive temperature=None at the public function boundary, while the transport had correctly applied TEMP=0.7. Prefix comparison did not normalize the effective temperature and marked those cases as harness mismatches. Its report is retained in reports/diagnostics/l09_escalation-lesson-09-20261106T165706.json; do not count its diagnostic verdicts as model outcomes. The remaining independent agent turns were completed and retained during this attempt.

Offline regression test_live_prefix_uses_effective_environment_temperature reproduced the issue. Normalize the effective temperature before prefix comparison, and raise RuntimeError for a harness mismatch so it cannot be mistaken for malformed judge output. Then replay all saved agent turns and both saved judge outputs, including the malformed one, and call the judge only for the three not-yet-judged cases. No repeated paid agent turn and no selective successful replacement of an invalid verdict.

Resumed runner emits trace copies and short replay latency. Analysis deduplicates identical copies by request_id and rejects conflicting copies. Unique actual responses/spans determine counts and costs. Runner elapsed/latency from replay is not presented as a live latency benchmark. Original timestamps and every failed attempt remain available.
