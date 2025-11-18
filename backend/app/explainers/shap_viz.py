from typing import Dict, List


def summarize_explanations(explanations: List[Dict[str, float]]) -> Dict[str, List[Dict[str, float]]]:
    return {"explanations": explanations}

