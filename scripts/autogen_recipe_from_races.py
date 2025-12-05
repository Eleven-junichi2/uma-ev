from pathlib import Path
import json
import argparse
import random
import sys
import time

import pandas as pd

import __init__  # noqa


def run():
    for date_dir in Path("data/race").iterdir():
        for race_course_dir in date_dir.iterdir():
            for race_num_dir in race_course_dir.iterdir():
                race_dir = race_num_dir
                if Path(race_dir / "racecard.csv").exists():
                    recipe = {
                        "race_date": date_dir.stem,
                        "racecourse": race_course_dir.stem,
                        "race_num": race_num_dir.stem,
                        "factors": [],
                        "pipelines": {},
                        "weights": {},
                    }
                    recipe_filepath = Path(
                        f"recipes/{date_dir.stem}_{race_course_dir.stem}_{race_num_dir.stem}.json"
                    )
                    print(recipe)
                    if not recipe_filepath.exists():
                        with open(recipe_filepath, "w", encoding="utf-8") as f:
                            json.dump(recipe, f, indent=4, ensure_ascii=False)


if __name__ == "__main__":
    run()
