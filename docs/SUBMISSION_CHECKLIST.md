# Submission checklist

| Brief requirement | Included evidence | Status |
|---|---|---|
| Complete modular Python source | app.py and ops_assistant/ | Included |
| README with all requested sections | README.md | Included |
| Sample data | data/seed.json | Included |
| At least three tools | Store.search, Store.lookup, Store.create | Implemented |
| LangGraph state, nodes, edges and routing | ops_assistant/agent.py | Implemented |
| LLM/function calling | LLMRouter and strict schemas | Implemented and verified with OpenRouter |
| Memory and multi-step workflow | Missing details, draft, confirmation | Tested locally and with live OpenRouter |
| Safety/error handling | Validation, scoped lookup, deduplication, failure tests | Tested |
| Streamlit chat/history/reset | app.py and UI test | Tested |
| Requirements and environment example | requirements*.txt, .env.example | Included |
| Architecture diagram | README Mermaid and docs/architecture.mmd | Included |
| Demonstration | docs/DEMO_GUIDE.md and scripts/demo.py | Live evaluation must still be delivered |
| GitHub repository | https://github.com/rasingod/ai-operations-assistant | Published in Rajat's account |
| PowerPoint | AI_Operations_Assistant.pptx in submission outputs | Included with final package |

## Before submitting

Submission name: **Rajat Singodia**. Add a student ID only if your institution requires it. Keep your key in the local `.env` and use LLM mode for the GenAI assessment. Use the repository URL above in your submission. Perform the live demonstration or record it using the supplied script. Do not submit an API key or the mutable runtime database.

## Working with the published repository

```bash
git clone https://github.com/rasingod/ai-operations-assistant.git
cd ai-operations-assistant
```

The following instructions also support creating a separate copy in a different repository.

## Publishing a separate copy

From the project root, with Git installed and your own identity configured:

```bash
git init -b main
git add .
git commit -m "Initial AI Operations Assistant submission"
```

Create an empty repository in your GitHub account, then use its actual URL:

```bash
git remote add origin YOUR_REPOSITORY_URL
git push -u origin main
```

The placeholder above is an instruction, not a published repository address. Inspect staged files before pushing. The supplied `.gitignore` excludes secrets and runtime data.
