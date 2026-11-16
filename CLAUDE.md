# PromptForge — project memory

A Claude Code plugin that optimizes prompts automatically: a `UserPromptSubmit`
hook sends each submitted prompt to an LLM, gets back a sharper, better-scoped
version, and injects it as context before Claude acts on it. This replaces the
old manual loop of polishing prompts in another model first.

See @README.md for the overview, @docs/INSTALL.md for setup, and
@docs/CONFIGURATION.md for all configuration options.

## Project layout

- `hooks/enhance.py` — the optimizer (standard-library-only Python). The heart of the tool.
- `hooks/hooks.json` — registers `enhance.py` on the `UserPromptSubmit` event.
- `.claude-plugin/plugin.json` — plugin manifest; references the hooks file.
- `.claude-plugin/marketplace.json` — marketplace catalog (marketplace name: `promptforge-tools`).
- `skills/prompt-optimization/SKILL.md` — the rewrite methodology, used on demand.
- `commands/enhance.md` — the `/enhance <prompt>` slash command.

## Invariants — do not break these

- **Fail open.** Any error, missing API key, or timeout must exit 0 with no
  output, so the user's prompt is never blocked. Keep every new code path inside
  this guarantee.
- **No dependencies.** `enhance.py` uses only the Python standard library — no
  `pip install` step, so it runs on any machine with `python3`.
- **Optimizer only rewrites.** It must output ONLY the rewritten prompt and must
  never answer the request itself.
- **Style lives in two places, kept in sync.** The rewrite instruction is
  `SYSTEM_PROMPT` in `enhance.py` and is mirrored in
  `skills/prompt-optimization/SKILL.md`. Change both together.
- **Config via env vars only.** Nothing is hard-coded; see CONFIGURATION.

## Commands

- Validate marketplace + manifest: `claude plugin validate .`
- Test the hook directly: `echo '{"prompt":"make login work"}' | python3 hooks/enhance.py`
- Install locally to test: `/plugin marketplace add ./` then `/plugin install promptforge@promptforge-tools`

## Release process

Bump `version` in BOTH `plugin.json` and the marketplace entry on every release,
or existing users won't receive the update. They refresh with
`/plugin marketplace update`.

## Current state / next steps

- Implemented and validated: JSON is valid; fail-open and short-prompt-skip paths tested.
- TODO before publishing: replace the `YOUR_USERNAME` / `YOUR_NAME` placeholders
  in `plugin.json`, `marketplace.json`, `README.md`, and `LICENSE`.
- TODO: open the PR — the project was built in a claude.ai session, so commit the
  files to a `feat/promptforge-plugin` branch, push, and open the PR.
- Default models (override with `PROMPTFORGE_MODEL` if stale): Anthropic
  `claude-haiku-4-5-20251001`, OpenAI `gpt-4o-mini`, Gemini `gemini-2.0-flash`.
