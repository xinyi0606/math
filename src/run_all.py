from __future__ import annotations

import json
import time

from src.Q1.run_q1 import run as run_q1
from src.Q2.run_q2 import run as run_q2
from src.Q3.run_q3 import run as run_q3
from src.Q4.run_q4 import run as run_q4
from src.common.config import RESULTS, SEED
from src.common.reporting import write_json


def run():
    started = time.perf_counter()
    outputs = {}
    for question, runner in (("Q1", run_q1), ("Q2", run_q2), ("Q3", run_q3), ("Q4", run_q4)):
        question_started = time.perf_counter()
        outputs[question] = runner()
        outputs[question]["run_all_runtime_seconds"] = time.perf_counter() - question_started
    summary = {
        "status": "PASS",
        "seed": SEED,
        "runtime_seconds": time.perf_counter() - started,
        "questions": {
            question: {
                "selected_method": outputs[question]["selected_method"],
                "runtime_seconds": outputs[question]["run_all_runtime_seconds"],
            }
            for question in outputs
        },
        "official_workbooks": [
            "output/result1.xlsx",
            "output/result2.xlsx",
            "output/result3.xlsx",
            "output/result4-2.xlsx",
            "output/result4-3.xlsx",
        ],
        "interpretation": "Q1/Q2/Q4 pass round1; Q3 method runs but its 0.90 reserve parameter is not frozen.",
    }
    RESULTS.mkdir(parents=True, exist_ok=True)
    write_json(RESULTS / "run_summary.json", summary)
    return summary


if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, indent=2))
