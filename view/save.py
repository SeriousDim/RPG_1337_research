from datetime import datetime
from pathlib import Path
from uuid import uuid4
import json
import os


def save_current_answers(answers: dict) -> None:
    result_dir = Path(os.getenv("RESULTS_DIR", Path(__file__).resolve().parent / "results"))
    result_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%d-%m-%Y-%H_%M_%S")
    file_name = f"{timestamp}_{uuid4()}.json"
    file_path = result_dir / file_name

    with file_path.open("w", encoding="utf-8") as f:
        json.dump(answers, f, ensure_ascii=False, indent=2)

