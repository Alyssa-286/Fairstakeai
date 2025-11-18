from typing import List


def segment_clauses(text: str) -> List[str]:
    """
    Simple heuristic splitter: split on double newlines or bullet markers.
    """
    candidates = []
    for chunk in text.split("\n\n"):
        cleaned = chunk.strip().replace("\n", " ")
        if not cleaned:
            continue
        if cleaned.startswith(("-", "*", "•")):
            cleaned = cleaned[1:].strip()
        candidates.append(cleaned)
    return candidates

