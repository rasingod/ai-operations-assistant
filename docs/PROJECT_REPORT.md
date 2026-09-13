# Project report: Northstar AI Operations Assistant

Submitted by **Rajat Singodia**. Project 3.

## Abstract

This project implements an agentic assistant for a fictional organization's IT support operations. A language model maps natural language to function calls. A LangGraph workflow executes a constrained set of local actions and retains context across turns. The application combines a Streamlit chat interface with a seeded SQLite repository. A separate offline planner makes functional evaluation possible without API credentials.

## Objectives and scope

The project demonstrates tool calling, an agent decision, state, conditional routing and a multi-step workflow. Its required tools are knowledge search, ticket lookup and ticket creation. It intentionally runs on a local machine and uses fictional data. The implemented scope follows the brief's emphasis on a realistic, achievable application.

## Functional design

An employee chooses a demo profile and enters a request. Guidance requests search article titles and tags and display ranked matches. Ticket inquiries retrieve only rows scoped to the chosen employee. Requests to open a ticket collect missing issue details, display a draft, and wait for explicit confirmation. The final write validates the fields, checks for an identical active ticket within a transaction, and returns either the new or existing ID.

## Agent and orchestration

The LLM is a constrained planner rather than a free-running autonomous loop. It sees a system policy, current request and bounded context. Five schemas cover three tool intents plus clarification and no-tool responses. Strict schema output and Pydantic parsing constrain argument shape. The application owns identity and authorization. LangGraph's decision node maps a validated planner decision to preparation, execution or response. The response node presents database facts without generative modification.

The graph completes at most one tool action per turn. The multi-step workflow is conversational: intent, missing information, draft, confirmation, transaction and final response. This is a deliberate design choice to keep tool behavior inspectable during evaluation.

## State model

The typed state includes employee identity, input message, bounded conversation history, route, arguments, latest result, reply, pending intent, draft and trace. The Streamlit session retains this state between graph invocations. Reset clears conversational state and any pending draft. It does not delete tickets. Profile changes create a new assistant instance. Persisted tickets survive a restart, while conversation state does not.

## Data design

The JSON seed contains three fictional employee profiles, six IT articles and three existing tickets. Startup imports it idempotently into SQLite. Employees and articles have stable IDs. Tickets contain an employee foreign key, title, issue description, status, UTC creation time and fingerprint. A partial unique index covers employee plus fingerprint for active tickets. A separate audit table records successful writes by ticket ID and time.

## Validation and failure handling

The assistant rejects unknown model tool names and malformed arguments. Required ticket lengths are validated before preview and again in the repository. Confirmation bypasses the model and uses only the retained draft. SQLite queries use parameters. A write transaction serializes duplicate checks and inserts. Provider timeouts, invalid decisions and tool exceptions return user-facing errors without exposing exception details. Prompts and credentials are not logged.

## User experience

The UI offers chat history, sample prompts, employee selection and reset. Each assistant response includes an expandable tool-result and workflow trace. Demo mode displays a visible warning, preventing offline rules from being misrepresented as LLM behavior. LLM mode discloses that conversation data is sent to the provider.

## Verification strategy

The suite exercises grounding, scoped lookup, missing information, confirmation, cancellation, state reset, duplicate races, invalid employees, SQL parameterization, failure recovery, session isolation, malformed model calls and the Streamlit interface. Mock SDK tests validate the function-calling contract. The actual test run and limitations appear in VALIDATION.md. Live model quality, enterprise authorization and deployment readiness are separate acceptance activities.

## Engineering practices and deployment scope

The package includes configuration examples, exact direct dependencies, an environment lock snapshot, gitignore rules, CI, operational guidance and reproducible demo commands. These are production-oriented practices, but the deployment remains local. A production rollout would require authenticated identity, access control, durable sessions, managed storage, backups, monitoring, security review and a live-model acceptance run.

## Conclusion

The implementation covers the brief's local assistant requirements and exposes the core agentic workflow in both code and UI traces. It provides a complete local submission and an evaluation walkthrough. Its documented boundaries prevent the offline demo or local identity selector from being mistaken for an enterprise GenAI deployment.
