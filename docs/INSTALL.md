# Installing PromptForge

## Prerequisites

- **Claude Code** with plugin support (`/plugin` commands available).
- **`python3`** on your `PATH` — check with `python3 --version`.
- An **API key** for one provider: Anthropic, OpenAI, or Google Gemini.

## Install from the marketplace

PromptForge is distributed as a Claude Code plugin via the marketplace defined
in this repo's `.claude-plugin/marketplace.json`.

```bash
# Add this repository as a marketplace (GitHub owner/repo shorthand)
/plugin marketplace add dhairya0210/prompt_enhancer

# Install the plugin (name@marketplace-name)
/plugin install promptforge@promptforge-tools
```

The marketplace **name** is `promptforge-tools` (the `name` field in
`marketplace.json`), which is what you install against — not the repository
name. Confirm what's registered with:

```bash
/plugin marketplace list
```

## Provide an API key

PromptForge reads your key from the environment. Set it in your shell profile
(`~/.zshrc`, `~/.bashrc`) so it persists:

```bash
export ANTHROPIC_API_KEY=sk-ant-...      # default provider
# or
export OPENAI_API_KEY=sk-...             # with PROMPTFORGE_PROVIDER=openai
# or
export GEMINI_API_KEY=...                # with PROMPTFORGE_PROVIDER=gemini
```

Restart Claude Code (or your terminal) so it picks up the variable.

## Verify it works

1. Set `PROMPTFORGE_LOG` to a temporary file so you can watch it run:

   ```bash
   export PROMPTFORGE_LOG=/tmp/promptforge.log
   ```

2. In Claude Code, submit a deliberately vague prompt like
   `fix the failing test`.

3. Claude should respond to a sharper, more specific version of your request.
   If the optimizer was skipped, check `/tmp/promptforge.log` for the reason
   (missing key, HTTP error, timeout). Because the hook fails open, your
   original prompt still runs even when optimization is skipped.

## Local development / testing the marketplace

Before pushing changes, validate and test against your working copy:

```bash
# Validate marketplace.json and the plugin manifest
claude plugin validate .

# Add your local checkout as a marketplace and install from it
/plugin marketplace add ./
/plugin install promptforge@promptforge-tools
```

You can also run the hook directly to test the optimizer in isolation:

```bash
echo '{"prompt": "make the login work"}' | python3 hooks/enhance.py
```

## Updating

After you push new commits, users refresh their copy with:

```bash
/plugin marketplace update
```

Bump `version` in both `plugin.json` and the marketplace entry on each release
so existing users actually receive the update.

## Uninstalling or pausing

- Pause without uninstalling: `export PROMPTFORGE_DISABLED=1`
- Remove entirely: `/plugin uninstall promptforge@promptforge-tools`
