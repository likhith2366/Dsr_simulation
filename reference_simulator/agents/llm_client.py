"""
llm_client.py — the one place that talks to the language model.

Both agents (scout_agent.py, rc_agent.py) import from here, so swapping the
model or the backend only ever touches this file.

Backend : Ollama running locally (https://ollama.com), default port 11434.
Model   : qwen3:4b. Pull it once with `ollama pull qwen3:4b`.

Two functions:
    llm(system, user, prefill, budget) -> raw text reply
    extract_json(raw, fallback)        -> dict parsed out of that reply
"""

import json

import requests

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL      = "qwen3:4b"


def llm(system: str, user: str, prefill: str, budget: int = 120) -> str:
    """
    Send one chat request and return the model's raw reply as a string.

    Args:
        system:  the agent's standing instructions (its SYSTEM_PROMPT).
        user:    this round's situation, rendered as plain text.
        prefill: the first characters of the reply, written by us. See below.
        budget:  max tokens the model may generate (Ollama `num_predict`).

    WHY THE PREFILL EXISTS — read this before changing anything here.
    qwen3:4b is a "thinking" model. Asked normally, it opens every reply with
    a long hidden reasoning block, and a single call took ~300 seconds. Setting
    "think": False alone did not stop it. What does work: we add a partial
    assistant message such as '{"type":' to the conversation. The model then
    believes it has already started answering in JSON and simply continues
    from there, skipping the reasoning entirely. Calls drop to ~3 seconds.
    The returned string therefore includes the prefill at the front.

    The scout uses prefill '{"type":'  (one command object).
    The controller uses '{"RC1":'      (an object keyed by crew name).
    """
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system",    "content": system},
            {"role": "user",      "content": user},
            {"role": "assistant", "content": prefill},   # the prefill trick
        ],
        "stream": True,                 # stream so we can stop early, below
        "think": False,
        # low temperature: we want the same situation to give the same command
        "options": {"temperature": 0.1, "num_predict": budget},
    }
    r = requests.post(OLLAMA_URL, json=payload, timeout=60, stream=True)
    r.raise_for_status()

    chunks = [prefill]
    need = prefill.count("{")   # braces already opened by the prefill

    # Ollama streams one JSON object per line, each carrying a text fragment.
    for line in r.iter_lines(decode_unicode=True):
        if not line:
            continue
        try:
            data = json.loads(line)
        except json.JSONDecodeError:
            continue
        chunks.append(data.get("message", {}).get("content", ""))
        combined = "".join(chunks)

        # Stop reading the moment the JSON object is closed. Without this the
        # model keeps writing explanations after the JSON and we wait for them.
        if combined.count("{") >= need and combined.count("{") == combined.count("}"):
            r.close()
            break
        if data.get("done"):
            break

    return "".join(chunks).strip()


def extract_json(raw: str, fallback: dict) -> dict:
    """
    Pull the outermost complete JSON object out of a model reply.

    The model sometimes wraps the JSON in stray text or produces something
    unparseable (it once wrote [[12, -15 + 7]] — arithmetic inside JSON).
    Rather than crash, we return `fallback`, which callers set to a harmless
    command such as {"type": "stay"}.

    Method: find the LAST '}' and walk backwards counting brace depth until
    the matching '{' is found, then json.loads that slice.
    """
    end = raw.rfind("}")
    if end == -1:
        return fallback

    depth, start = 0, -1
    for i in range(end, -1, -1):
        if raw[i] == "}":
            depth += 1
        elif raw[i] == "{":
            depth -= 1
        if depth == 0:
            start = i
            break
    if start == -1:
        return fallback

    try:
        return json.loads(raw[start:end + 1])
    except json.JSONDecodeError:
        return fallback
