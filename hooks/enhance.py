#!/usr/bin/env python3
"""
PromptForge — UserPromptSubmit hook for Claude Code.

Reads the prompt Claude Code sends on stdin (as JSON), asks an LLM to rewrite
it into a clearer, better-scoped instruction, and prints the result to stdout.
Claude Code adds stdout from a UserPromptSubmit hook to the conversation as
context, so the optimized version reaches Claude alongside the original.

Design rules:
  * Zero third-party dependencies — only the Python standard library, so the
    hook runs anywhere `python3` exists, with no `pip install` step.
  * Fail open — if anything goes wrong (no API key, network error, timeout),
    the hook exits 0 and prints nothing, so your prompt is never blocked.
  * Configurable — provider, model, and behavior are controlled by env vars.

Configuration (all optional except an API key for your chosen provider):
  PROMPTFORGE_DISABLED   "1"/"true" to turn the hook off without uninstalling.
  PROMPTFORGE_PROVIDER   "anthropic" (default), "openai", or "gemini".
  PROMPTFORGE_MODEL      Override the model id for the chosen provider.
  PROMPTFORGE_MIN_WORDS  Skip prompts shorter than this many words (default 4),
                         so "yes", "continue", etc. pass through untouched.
  PROMPTFORGE_TIMEOUT    API request timeout in seconds (default 30).
  PROMPTFORGE_LOG        Path to a file to append debug lines to (optional).

  ANTHROPIC_API_KEY / OPENAI_API_KEY / GEMINI_API_KEY  Your provider key.
"""

import json
import os
import sys
import urllib.request
import urllib.error

SYSTEM_PROMPT = (
    "You are a prompt optimizer for a coding agent (Claude Code). "
    "Rewrite the user's request so the agent can act on it accurately and "
    "without follow-up questions. Make the goal explicit, surface implied "
    "constraints, and keep any concrete details the user gave (file names, "
    "languages, versions, error text). Do not invent requirements the user "
    "did not imply, do not add commentary, and do not answer the request "
    "yourself. Preserve the user's intent and scope exactly. "
    "Output ONLY the rewritten prompt, with no preamble, labels, or fences."
)

DEFAULT_MODELS = {
    "anthropic": "claude-haiku-4-5-20251001",
    "openai": "gpt-4o-mini",
    "gemini": "gemini-2.0-flash",
}


def log(msg):
    path = os.environ.get("PROMPTFORGE_LOG")
    if not path:
        return
    try:
        with open(path, "a", encoding="utf-8") as fh:
            fh.write(f"[promptforge] {msg}\n")
    except Exception:
        pass


def _post(url, headers, payload, timeout):
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def call_anthropic(prompt, model, timeout):
    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        raise RuntimeError("ANTHROPIC_API_KEY is not set")
    body = _post(
        "https://api.anthropic.com/v1/messages",
        {
            "x-api-key": key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        {
            "model": model,
            "max_tokens": 1024,
            "system": SYSTEM_PROMPT,
            "messages": [{"role": "user", "content": prompt}],
        },
        timeout,
    )
    return "".join(
        b.get("text", "") for b in body.get("content", []) if b.get("type") == "text"
    ).strip()


def call_openai(prompt, model, timeout):
    key = os.environ.get("OPENAI_API_KEY")
    if not key:
        raise RuntimeError("OPENAI_API_KEY is not set")
    body = _post(
        "https://api.openai.com/v1/chat/completions",
        {"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        {
            "model": model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
        },
        timeout,
    )
    return body["choices"][0]["message"]["content"].strip()


def call_gemini(prompt, model, timeout):
    key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not key:
        raise RuntimeError("GEMINI_API_KEY is not set")
    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"{model}:generateContent?key={key}"
    )
    body = _post(
        url,
        {"Content-Type": "application/json"},
        {
            "system_instruction": {"parts": [{"text": SYSTEM_PROMPT}]},
            "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        },
        timeout,
    )
    parts = body["candidates"][0]["content"]["parts"]
    return "".join(p.get("text", "") for p in parts).strip()


PROVIDERS = {
    "anthropic": call_anthropic,
    "openai": call_openai,
    "gemini": call_gemini,
}


def main():
    if os.environ.get("PROMPTFORGE_DISABLED", "").lower() in ("1", "true", "yes"):
        sys.exit(0)

    try:
        data = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    raw = (data.get("prompt") or "").strip()
    min_words = int(os.environ.get("PROMPTFORGE_MIN_WORDS", "4"))
    if not raw or len(raw.split()) < min_words:
        sys.exit(0)

    provider = os.environ.get("PROMPTFORGE_PROVIDER", "anthropic").lower()
    call = PROVIDERS.get(provider)
    if call is None:
        log(f"unknown provider '{provider}', skipping")
        sys.exit(0)

    model = os.environ.get("PROMPTFORGE_MODEL") or DEFAULT_MODELS[provider]
    timeout = float(os.environ.get("PROMPTFORGE_TIMEOUT", "30"))

    try:
        refined = call(raw, model, timeout)
    except urllib.error.HTTPError as exc:
        log(f"HTTP {exc.code} from {provider}: {exc.reason}")
        sys.exit(0)
    except Exception as exc:  # noqa: BLE001 — fail open on anything
        log(f"enhancement skipped: {exc}")
        sys.exit(0)

    if refined and refined != raw:
        print(
            "The following is an optimized version of the user's request, "
            "produced by PromptForge. Treat it as the authoritative "
            "instruction for this turn:\n\n" + refined
        )
    sys.exit(0)


if __name__ == "__main__":
    main()
