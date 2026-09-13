# Validation record

Execution date: 13 September 2026. Environment: Windows, isolated Python 3.12 environment. Dependency versions appear in requirements-lock.txt.

## Automated results

Command: `python -m pytest -q`

**36 passed in 44.59 seconds.**

The suite exercises actual LangGraph execution, seeded SQLite queries, missing-description memory, draft confirmation, cancellation, reset, employee scope, simultaneous duplicate requests, malformed model functions, provider/tool errors and Streamlit chat/reset. The concurrency case submits 12 identical requests across 6 workers and asserts one insertion and one shared ticket ID.

OpenRouter-specific checks cover the fixed SDK endpoint, secret-safe settings representation, required configuration, model slug validation, HTTP 400/401/402/403/404/429/503 responses, connection failure, and a single corrective retry for invalid tool output. Both successful correction and the two-attempt failure bound are tested.

## Live OpenRouter acceptance

Command: `python scripts/live_check.py`

**5 of 5 checks passed**, using the user's configured `openrouter/free` selection and a temporary SQLite database. The run completed at 06:30 UTC on 13 September 2026. Checks: knowledge retrieval, employee-scoped lookup, missing information, draft preparation and confirmed ticket creation. See `live-check.json` for the actual fictional responses and node traces. Confirmation executes the retained draft without another model call.

During integration, the free router rejected the optional parallel-tool parameter, which was removed. The application still enforces exactly one tool call. A prior run returned malformed model output on draft preparation. The bounded corrective retry addresses that failure; persistent invalid output fails safely. Free-provider routing and availability can change, so this run is a functional acceptance sample, not an accuracy benchmark.

The offline demonstration also completed successfully. `demo-transcript.txt` records knowledge retrieval, lookup, information collection, confirmation and duplicate reuse. Generated IDs vary.

## Evidence boundaries

- No enterprise SSO, penetration test, production load test or internet deployment certification.
- Local tests do not establish the outcome of GitHub Actions runs.
- No recorded or delivered assessment demonstration. Use DEMO_GUIDE.md to deliver the live option required by the brief.
- API credentials remain in the ignored local `.env`; published files and the ZIP exclude that file and runtime databases.
