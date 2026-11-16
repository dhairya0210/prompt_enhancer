---
name: prompt-optimization
description: Rewrite a rough or underspecified coding request into a clear, well-scoped prompt before acting on it. Use this whenever the user hands over a vague, terse, or ambiguous instruction, asks you to "improve", "optimize", "tighten", or "clean up" a prompt, pastes a prompt they intend to run elsewhere, or runs the /enhance command. Apply it even when the user does not say the word "prompt" — if a request is missing obvious context the task needs, optimize it first, then proceed.
---

# Prompt Optimization

This skill turns a raw request into a precise instruction a coding agent can act
on without a round of follow-up questions. It complements the PromptForge hook,
which does the same thing automatically on every submitted prompt; use this skill
when optimizing on demand (for example, via the `/enhance` command) or when a
request clearly needs sharpening before you start work.

## When to apply

Optimize first when a request shows any of these:
- A goal stated as an outcome with no path ("make the tests pass").
- Missing targets — which file, function, directory, or service.
- Ambiguous scope — could mean a one-line fix or a refactor.
- Implied constraints the user knows but did not write (framework, version,
  style, performance, backwards-compatibility).
- A pasted prompt the user wants tightened rather than executed as-is.

Do **not** rewrite when the request is already specific and complete, or when it
is a trivial confirmation ("yes", "continue", "run it"). Over-optimizing short
prompts wastes effort and can distort intent.

## How to rewrite

Produce a single rewritten prompt that:

1. **States the goal explicitly.** Lead with the concrete outcome and the
   surface it applies to (file, module, endpoint, component).
2. **Preserves every concrete detail** the user gave — file names, languages,
   versions, exact error text, function names. Never drop specifics.
3. **Surfaces implied constraints** the task plainly needs, without inventing
   requirements the user did not imply. If a constraint is genuinely unknown
   and would change the approach, name it as an open question rather than
   guessing.
4. **Sets scope boundaries** — say what is in scope and, where it helps, what is
   out of scope, so the work does not sprawl.
5. **Names a success signal** when one is obvious (tests green, builds clean,
   endpoint returns expected shape).
6. **Keeps the user's intent and voice.** You are clarifying, not redesigning.

Keep the rewrite proportional: a small ask gets a tightened sentence or two, not
a specification document.

## Output

Return only the rewritten prompt — no preamble, no labels, no code fences —
unless the user asked to see the reasoning. If a critical detail is missing and
no reasonable default exists, append a short "Open questions:" list after the
rewrite instead of inventing an answer.

## Example

Raw: `fix the login bug`

Optimized:
> Investigate and fix the login failure in the authentication flow. Reproduce
> the issue, identify the root cause, and apply a minimal fix that keeps the
> existing public API unchanged. Add or update a test that fails on the current
> bug and passes after the fix. Report the root cause and the change made.
>
> Open questions: which file or component handles login, and what is the
> observed symptom (error message, wrong redirect, no response)?
