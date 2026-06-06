from __future__ import annotations

import shutil
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SOURCE_DIR = PROJECT_ROOT / "outputs" / "predictions"
DESTINATION_DIR = PROJECT_ROOT / "frontend" / "public" / "data"
FILES = (
    "world_cup_team_metrics.json",
    "tournament_predictions.json",
    "world_cup_probabilities.json",
    "group_results.json",
)


def main() -> None:
    """Copy backend prediction exports into the frontend public data directory."""

    missing = [SOURCE_DIR / filename for filename in FILES if not (SOURCE_DIR / filename).is_file()]
    if missing:
        missing_files = "\n".join(f"- {path.relative_to(PROJECT_ROOT)}" for path in missing)
        raise SystemExit(f"Missing required prediction files:\n{missing_files}")

    DESTINATION_DIR.mkdir(parents=True, exist_ok=True)
    for filename in FILES:
        source = SOURCE_DIR / filename
        destination = DESTINATION_DIR / filename
        shutil.copyfile(source, destination)
        print(f"Copied {source.relative_to(PROJECT_ROOT)} -> {destination.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
