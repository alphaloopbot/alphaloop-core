# Cursor Agent Playbook (Project Guardrails)

## Always
- Use **Auto** model unless I explicitly say **“Max Mode.”**
- Work **only on files I select** or **paths I name**.
- For anything larger than a few lines or >1 file: **propose a step-by-step plan first** and wait for my OK.
- Prefer **small, reviewable diffs**; explain *why* each change is needed.

## Never (without explicit OK in my last message)
- Do **not** run `docker build`, `npm install`, `pip install`, or `pytest` **on the whole repo**.
- Do **not** scan the entire repo.
- Do **not** open long-running terminals or background processes.

## Preferred workflow
1) **Show a minimal plan** (bullets, 3–6 steps max).
2) **Edit a single file or a small set** strictly under the paths I mentioned.
3) **Stop and ask for confirmation** before any terminal command or edits outside the declared scope.
4) **I** run tests/linters and paste errors; **you** fix iteratively.

---

## Autonomous Changes (Allowed When “Reasonably Certain”)
- Cursor **may apply changes without asking** *only if* it is **~80% confident** they will work **and** they are **small, localized, and reversible**.
- If the autonomous change **fails**, it may perform **one (1) additional attempt** to correct it—**no more**.
- After that, **stop** and **ask for guidance** (or escalate to external consultant per below).

### Examples of “safe” autonomous changes
- Reordering imports; fixing obvious typos; adding/adjusting type hints; updating config values that are unambiguous; adding missing exports; trivial refactors that don’t change behavior.

### Examples that **require confirmation**
- API/contract changes, migrations, cross-cutting refactors, dependency upgrades, build system changes, CI workflow edits, secrets/credentials handling.

---

## Scope Control
- Treat the **paths/files I named** as the **hard boundary**.
- If you **need to touch anything outside** that scope, show:
    - the exact file(s) you propose to modify,
    - the minimal diff,
    - and why it’s necessary.

---

## Command Approval
- Before any shell command, show:
    - the exact command(s),
    - the **purpose** and **expected outcome**,
    - the **risk** (data loss? long-running? network?),
    - the **fallback** if it fails.
- Wait for **my explicit “OK”**.

---

## External Consultant Escalation (Allowed Anytime After One Failed Retry)
If you’re blocked or <80% confident, you may **draft a consultant request**.
**Include this template** so I can copy-paste to ChatGPT (or forward):

**Consultant Brief**
- **Problem summary:**
    _One paragraph; what’s broken? What’s the goal behavior?_
- **Context & constraints:**
    _Tooling versions, src layout, CI rules, performance/security constraints._
- **What we tried:**
    _Numbered list of attempts with outcomes & error snippets._
- **Files & architecture:**
    _Repo layout (only relevant parts), affected modules, entry points._
- **Exact errors/logs:**
    _Clean, copy-pasteable snippets._
- **What we need from you:**
    _e.g., mypy config pattern, minimal diff, command sequence, risks._
- **Current hypothesis:**
    _Where we think the root cause lies; what to verify next._

---

## Status Messages (Use These)
- **“Autonomous safe fix applied.”**
    _Why_: short reason · _Files_: list · _Diff summary_: 1–3 bullets · _Result_: e.g., linter now passes.
- **“Confidence <80%; asking for approval.”**
    _Plan_: bullets · _Risks_: bullets · _Expected outcome_.
- **“First attempt failed; performing one final try.”**
    _Change_: what you’ll do · _Why it should work_.
- **“Second attempt failed; escalating to consultant.”**
    _Include the Consultant Brief above._
