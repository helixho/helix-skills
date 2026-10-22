# Interactive Testing

Read this only when a result depends on a real UI, browser, device, or other external interactive state, and code inspection and automated tests cannot give a trustworthy judgment.

## Choose the executor

- Give repeatable interactive scenarios with a clear path and observable results to an `Executor`.
- Keep product trade-offs, subjective visual judgment, weak criteria, and final experience acceptance in the main thread.
- Allow only one active operator per browser session, device, account, or external environment at a time.
- Run interactive tests in parallel only when browser contexts, accounts, devices, or test environments are isolated from each other.

## Write the brief

Besides the standard brief fields, state:

- Scenario: the user goal to verify and the starting state.
- Environment: browser, device, account, data, and permission boundaries.
- Actions: the minimum necessary steps; do not disguise exploration as a fixed script.
- Criteria: observable success, failure signals, and allowed tolerance.
- Evidence: the smallest sufficient set of screenshots, logs, recordings, network records, or state snapshots.
- Cleanup: how test data, temporary state, accounts, or environments are restored.

## Acceptance

- Reuse facts already proven by code, unit tests, and static checks instead of repeating clicks.
- When the environment is unavailable, the state is uncertain, or the criteria are insufficient, return a clear blocker rather than guessing success.
- The main thread checks the key evidence and completes final acceptance; the number of screenshots, tools, and device matrix follow the risk, with no fixed count.
