from __future__ import annotations

import shutil
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SOURCE_DIR = PROJECT_ROOT / "outputs" / "predictions"
FRONTEND_DIR = PROJECT_ROOT / "frontend"
FILES = (
    "world_cup_team_metrics.json",
    "tournament_predictions.json",
    "world_cup_probabilities.json",
    "group_results.json",
    "representative_tournament.json",
)


def sync_frontend_data(
    source_dir: Path = SOURCE_DIR,
    frontend_dir: Path = FRONTEND_DIR,
) -> bool:
    """Copy prediction exports to the frontend, if the frontend exists."""

    if not frontend_dir.is_dir():
        print(f"Warning: frontend directory not found; skipping data sync: {frontend_dir}")
        return False

    missing = [source_dir / filename for filename in FILES if not (source_dir / filename).is_file()]
    if missing:
        missing_files = "\n".join(f"- {path}" for path in missing)
        raise FileNotFoundError(f"Missing required prediction files:\n{missing_files}")

    destination_dir = frontend_dir / "public" / "data"
    destination_dir.mkdir(parents=True, exist_ok=True)
    for filename in FILES:
        source = source_dir / filename
        destination = destination_dir / filename
        shutil.copyfile(source, destination)
        print(f"Copied {source} -> {destination}")

    return True


def main() -> None:
    """Run the frontend data sync as a standalone script."""

    try:
        sync_frontend_data()
    except FileNotFoundError as error:
        raise SystemExit(str(error)) from error


if __name__ == "__main__":
    main()
