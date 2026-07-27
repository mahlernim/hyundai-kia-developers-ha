# Repository guidance

## Writing style

- Do not use em dashes.
- Minimize colons and semicolons in prose.

## Public communication

Treat pull requests, issues, changelogs, release notes, and README content as
public-facing writing for users and maintainers of this integration.

- Include only information that helps someone understand, review, test, or use
  the change.
- Write for general Hyundai, Kia, and Genesis Developers users rather than for
  one account, vehicle, or development environment.
- Do not mention Codex, agent workflows, local operating-system limitations,
  shell commands, tooling workarounds, temporary failures, resolved debugging
  history, or other implementation-process details unless they materially
  affect the submitted code.
- Do not disclose credentials, private API payloads, account details,
  vehicle-specific diagnostics, or other private testing context.
- In validation sections, list the canonical checks and their final results.
  Do not explain local execution differences when canonical CI passes.
- Mention a limitation only when a required check remains incomplete, affects
  reproducibility or correctness, or requires action from a reviewer.

Before publishing or editing public text, perform a public-message audit and
remove anything that does not change how a user or reviewer evaluates the
change.
