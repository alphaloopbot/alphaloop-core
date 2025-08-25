# Cursor Agent Playbook (Project Guardrails)

## Always
- Use **Auto** model unless I explicitly say "Max Mode".
- Work **only on files I select** or paths I name.
- For large tasks: **propose a step-by-step plan first**, wait for my OK.

## Never (without explicit OK in the last message)
- Do NOT run: `docker build`, `npm install`, `pip install`, `pytest` on the whole repo.
- Do NOT scan the entire repo.
- Do NOT open long-running terminals or background processes.

## Preferred workflow
1) Show a minimal plan.
2) Edit a single file or small set of files.
3) Stop and ask for confirmation before any terminal command.
4) I will run tests/linters locally and paste errors for you to fix.
