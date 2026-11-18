# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)


def format_message(counters, label, message, timestamp=None):
    # <!-- custom: Count each speaker independently so an exported message is easy to cite.
    # Codex progress notes share its speaker's sequence, while optional tool entries have their own counters. (GPT-6.1-Sol) -->
    speaker = "CODEX" if label == "CODEX PROGRESS" else label
    counters[speaker] = counters.get(speaker, 0) + 1
    suffix = f" | {timestamp}" if timestamp else ""
    return f"=== {label} {counters[speaker]:05d}{suffix} ===\n{message}"
