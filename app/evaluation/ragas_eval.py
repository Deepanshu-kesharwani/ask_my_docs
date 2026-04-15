from __future__ import annotations

import json
from pathlib import Path
from app.settings import get_settings

def run_ragas_eval():
    """
    Expected dataset format (JSONL):
    {"question": "...", "answer": "...", "contexts": ["...", "..."], "ground_truth": "..."}
    """
    s = get_settings()
    path = Path("configs/eval_dataset.jsonl")
    if not path.exists():
        return {"status": "no_dataset", "message": "configs/eval_dataset.jsonl not found"}

    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    # Plug RAGAS here in your actual environment:
    # from ragas import evaluate
    # from ragas.metrics import faithfulness, answer_relevancy, context_precision, context_recall
    # result = evaluate(...)
    # return result.to_pandas().to_dict(orient="records")
    return {
        "status": "stub",
        "rows": len(rows),
        "thresholds": {
            "faithfulness": s.faithfulness_threshold,
            "answer_relevance": s.answer_relevance_threshold,
            "context_precision": s.context_precision_threshold,
            "context_recall": s.context_recall_threshold,
        },
    }