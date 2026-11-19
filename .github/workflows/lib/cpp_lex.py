# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: Reuse the source-provenance masker in both C++ checks so comments and literals cannot be mistaken for active code.
# Keep character positions and line breaks for the diagnostics. See KI#1098.2. (GPT-6.2-Sol) -->

def mask_cpp(text: str) -> str:
    chars = list(text)
    i = 0
    n = len(chars)
    state = "code"
    quote = ""
    while i < n:
        ch = chars[i]
        nxt = chars[i + 1] if i + 1 < n else ""
        if state == "code":
            if ch in ('"', "'"):
                state = "string"
                quote = ch
                chars[i] = " "
                i += 1
                continue
            if ch == "/" and nxt == "/":
                chars[i] = chars[i + 1] = " "
                i += 2
                while i < n and chars[i] != "\n":
                    chars[i] = " "
                    i += 1
                continue
            if ch == "/" and nxt == "*":
                chars[i] = chars[i + 1] = " "
                i += 2
                while i < n - 1 and not (chars[i] == "*" and chars[i + 1] == "/"):
                    if chars[i] != "\n":
                        chars[i] = " "
                    i += 1
                if i < n - 1:
                    chars[i] = chars[i + 1] = " "
                    i += 2
                continue
        else:
            if ch == "\\":
                chars[i] = " "
                if i + 1 < n and chars[i + 1] != "\n":
                    chars[i + 1] = " "
                i += 2
                continue
            if ch == quote:
                state = "code"
            if ch != "\n":
                chars[i] = " "
            i += 1
            continue
        i += 1
    return "".join(chars)
