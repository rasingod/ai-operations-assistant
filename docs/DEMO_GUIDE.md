# Live demonstration guide

Allow approximately 7 minutes. Start with a fresh database path if repeatable seed-only results are needed. Use only fictional data. Select EMP1024.

| Time | Action | Explain / expected evidence |
|---|---|---|
| 0:00 | Introduce the problem and mode | State whether the planner is LLM or deterministic demo |
| 0:45 | Ask `How do I reset my VPN password?` | KB001, retrieved source text, knowledge_search trace |
| 1:30 | Ask `What is the status of my laptop issue?` | IT-1001, In progress, scoped SQLite lookup |
| 2:15 | Ask `Please raise a ticket` | Missing-description request, no database write |
| 2:45 | Enter `My printer prints blank pages` | Creation intent survives the second turn, draft appears |
| 3:15 | Enter `confirm` | New generated ID and Open status |
| 3:45 | Repeat `My printer prints blank pages. Please raise a ticket.` and `confirm` | Same active ID reused |
| 4:30 | Ask about IT-1003 | No ticket available under EMP1024 |
| 5:00 | Prepare another draft, enter `cancel` | No ticket write |
| 5:30 | Clear conversation and inspect tickets again | History disappears, saved tickets remain |
| 6:00 | Show agent.py and test output | Explain state, conditional edges, validation and transaction |
| 6:45 | State limitations | Demo identity, lexical search, no live-model verification yet |

For the GenAI criterion, configure LLM mode before evaluation and run the same cases. Validate that the model understands paraphrases. Do not claim the deterministic run measures model accuracy. Model credentials belong in the local `.env` only.

If recording instead of presenting live, capture the app window and narration, hide account/key screens, and include the mode label and tool traces. No recording is included in this package. `demo-transcript.txt` is an executed offline transcript for preparation.

## Likely viva questions

**Why LangGraph?** It makes decision, preparation, execution and response transitions explicit and testable.

**Where is the AI?** LLMRouter calls the model with function schemas and contextual input. DemoRouter is a separate rules implementation.

**Where is memory?** Assistant.state is retained in Streamlit session state and passed back into the graph each turn.

**Can the model create any ticket it wants?** It can propose a draft. The application waits for explicit confirmation and independently validates the write.

**How are duplicates prevented?** A normalized-description fingerprint plus an employee-scoped active-ticket unique index within a SQLite transaction.

**Why not let the model rewrite ticket status?** Direct formatting ensures the response preserves database facts exactly.

**Is this enterprise-ready?** It is a tested local implementation with deployment safeguards documented. Real use requires authentication and operational controls beyond the assignment's scope.
