# Operations and deployment boundaries

## Supported deployment

One local machine, Python 3.12, a writable SQLite directory and a browser connected to localhost. Start from the project root so Streamlit reads its local configuration. The default listener is 127.0.0.1. Do not expose the employee selector to untrusted users.

## Data lifecycle

The runtime directory contains mutable database files and stays outside version control. Do not edit seed ticket IDs to represent ongoing status updates: startup uses insert-or-ignore, not a migration mechanism. To test with a clean database, set DATABASE_PATH to a new path. Conversation reset never deletes ticket data.

For backups, stop the app before copying the database and associated WAL files, or use Python's SQLite backup API while it is running. Verify restoration into a separate directory before relying on a backup. Seed data is not a backup of newly created tickets.

## Logging and recovery

Console logging records planner/tool failure categories, not message bodies or secrets. A failed planner does not write. A failed tool leaves a recoverable response. If a ticket commit succeeded before a response was lost, a retry with the same description reuses the active ticket. Do not retry altered descriptions without checking existing tickets.

## Production acceptance work

1. Replace the demo selector with verified SSO identity. Map it to employee scope on the server.
2. Add access policies and tests for every data operation. Enforce retention and privacy requirements.
3. Evaluate the configured model with paraphrases, adversarial inputs, refusal handling and cost/latency measurements.
4. Introduce managed persistence and schema migrations if scale requires it. Add durable conversation state when needed.
5. Add service monitoring, centralized redacted logs, encrypted backups and restore exercises.
6. Review dependencies and CI actions, pin supply-chain artifacts, and run security/load tests for the target environment.
7. Deploy behind authenticated TLS ingress with rate limits. Review provider data handling before real employee use.

These are deployment prerequisites, not completed features. No enterprise security certification or production availability claim accompanies this submission.
