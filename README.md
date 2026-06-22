# PromptForge

A layer between you and Claude Code that **optimizes your prompts automatically**.

Instead of writing a rough prompt, pasting it into another model to polish, and
copying the result into Claude Code, PromptForge does that middle step for you.
It hooks into Claude Code, intercepts each prompt as you submit it, rewrites it
into a clearer and better-scoped instruction, and hands the refined version to
Claude — all without changing how you type.

## How it works

Claude Code fires a `UserPromptSubmit` hook the moment you submit a prompt,
before Claude processes it. PromptForge registers a small script on that hook:

```
you type a prompt  ──▶  UserPromptSubmit hook (enhance.py)
                              │  sends your prompt to an LLM
                              │  gets back an optimized version
                              ▼
                        optimized prompt added as context  ──▶  Claude Code acts
```

The optimizer runs on a fast, inexpensive model by default and **fails open**:
if there is no API key, or the network call errors or times out, the hook does
nothing and your original prompt goes through untouched. Your workflow never
breaks because of the enhancer.

## What's in the box

| Component | What it does |
| --- | --- |
| `hooks/enhance.py` | The optimizer — a dependency-free Python script run on every prompt. |
| `hooks/hooks.json` | Registers the script on the `UserPromptSubmit` event. |
| `skills/prompt-optimization/` | A Skill encoding the rewrite methodology, usable on demand. |
| `commands/enhance.md` | `/enhance <prompt>` — optimize a prompt without running it. |
| `.claude-plugin/` | Plugin manifest and marketplace catalog for distribution. |

## Quick start

```bash
# 1. In Claude Code, add this repo as a marketplace
/plugin marketplace add dhairya0210/prompt_enhancer

# 2. Install the plugin
/plugin install promptforge@promptforge-tools

# 3. Tell it which API key to use (Anthropic by default)
export ANTHROPIC_API_KEY=sk-ant-...
```

That's it — your next prompt will be optimized automatically. See
[`docs/INSTALL.md`](docs/INSTALL.md) for details and
[`docs/CONFIGURATION.md`](docs/CONFIGURATION.md) for all options.

## Configuration at a glance

Everything is controlled by environment variables; nothing is hard-coded.

| Variable | Default | Purpose |
| --- | --- | --- |
| `PROMPTFORGE_PROVIDER` | `anthropic` | `anthropic`, `openai`, or `gemini`. |
| `PROMPTFORGE_MODEL` | provider default | Override the model id. |
| `PROMPTFORGE_MIN_WORDS` | `4` | Skip prompts shorter than this. |
| `PROMPTFORGE_TIMEOUT` | `30` | API timeout in seconds. |
| `PROMPTFORGE_DISABLED` | unset | Set to `1` to pause without uninstalling. |
| `PROMPTFORGE_LOG` | unset | Append debug lines to this file path. |
| `ANTHROPIC_API_KEY` / `OPENAI_API_KEY` / `GEMINI_API_KEY` | — | Your provider key. |

## Requirements

- Claude Code with plugin support
- `python3` available on your `PATH`
- An API key for your chosen provider

No `pip install` is needed — the hook uses only the Python standard library.

## A note on trust and cost

Hooks run automatically during Claude Code's loop **with your environment's
credentials**, so review the hook code before installing — that advice applies
to any plugin, including this one. The script here is short and only calls the
provider you configure. Also note that optimization adds one extra LLM call per
substantive prompt, which is why a fast/cheap model is the default and short
prompts are skipped.

## License

MIT — see [LICENSE](LICENSE).
