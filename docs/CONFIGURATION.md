# Configuring PromptForge

All behavior is controlled by environment variables. Set them in your shell
profile so they apply to every Claude Code session.

## Provider and model

| Variable | Default | Notes |
| --- | --- | --- |
| `PROMPTFORGE_PROVIDER` | `anthropic` | One of `anthropic`, `openai`, `gemini`. |
| `PROMPTFORGE_MODEL` | see below | Overrides the model id for the chosen provider. |

Default models per provider:

| Provider | Default model | Key variable |
| --- | --- | --- |
| `anthropic` | `claude-haiku-4-5-20251001` | `ANTHROPIC_API_KEY` |
| `openai` | `gpt-4o-mini` | `OPENAI_API_KEY` |
| `gemini` | `gemini-2.0-flash` | `GEMINI_API_KEY` or `GOOGLE_API_KEY` |

The defaults favor fast, inexpensive models because the optimizer runs on every
substantive prompt. If a default model id is out of date for your account, set
`PROMPTFORGE_MODEL` to a current one — the script does not assume any id is
valid, it just sends what you configure.

Example — use OpenAI:

```bash
export PROMPTFORGE_PROVIDER=openai
export PROMPTFORGE_MODEL=gpt-4o-mini
export OPENAI_API_KEY=sk-...
```

## Behavior

| Variable | Default | Notes |
| --- | --- | --- |
| `PROMPTFORGE_MIN_WORDS` | `4` | Prompts with fewer words pass through unchanged. Raise it if you find short prompts are being over-processed. |
| `PROMPTFORGE_TIMEOUT` | `30` | Seconds to wait for the API. On timeout the hook fails open. |
| `PROMPTFORGE_DISABLED` | unset | `1`, `true`, or `yes` turns the hook off without uninstalling. |
| `PROMPTFORGE_LOG` | unset | A file path; when set, skip/error reasons are appended there. |

## Customizing the optimization style

The instruction that drives the rewrite lives in `SYSTEM_PROMPT` near the top of
`hooks/enhance.py`. This is the heart of the tool — edit it to match how you
want prompts shaped (more terse, more exploratory, domain-specific conventions,
house style, etc.). Two guidelines:

- Keep the rule that it must output **only** the rewritten prompt with no
  preamble, or the extra text leaks into your context.
- Keep the rule that it must **not** answer the request itself.

The same methodology is mirrored in `skills/prompt-optimization/SKILL.md`, which
powers the `/enhance` command and on-demand rewrites. If you change your style,
update both so the automatic and manual paths stay consistent.

## How the optimized prompt reaches Claude

A `UserPromptSubmit` hook's stdout is **added to the conversation as context**,
not substituted for your original text. PromptForge prefixes its output with a
line telling Claude to treat the rewrite as the authoritative instruction, so
Claude follows the optimized version while still having your original wording
available.

## Per-project overrides

Environment variables are global to your shell. To vary behavior per project,
set the variables in a project-specific way (for example, a `direnv` `.envrc`
in the project root) so each repository can choose its own provider, model, or
`PROMPTFORGE_DISABLED` state.
