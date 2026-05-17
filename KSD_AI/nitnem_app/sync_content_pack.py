#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
NITNEM_APP_DIR = ROOT / "nitnem_app"
CONTENT_FILE = NITNEM_APP_DIR / "content" / "nitnem_ru_ksd_v1.json"
MOBILE_ASSET = ROOT / "nitnem_mobile" / "app" / "src" / "main" / "assets" / CONTENT_FILE.name
SGGS_MOBILE_ASSET = ROOT / "sggs_mobile" / "app" / "src" / "main" / "assets" / CONTENT_FILE.name
PACKAGE_ID = "nitnem_ru_sikhizm_resolved"


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a JSON object")
    return data


def validate_pack(path: Path) -> dict[str, Any]:
    data = load_json(path)
    package_id = data.get("package_id")
    if package_id != PACKAGE_ID:
        raise ValueError(f"{path} has package_id {package_id!r}, expected {PACKAGE_ID!r}")
    if int(data.get("schema_version", 0)) < 1:
        raise ValueError(f"{path} has invalid schema_version")
    if int(data.get("content_version", 0)) < 1:
        raise ValueError(f"{path} has invalid content_version")
    if not data.get("angs"):
        raise ValueError(f"{path} has no angs")
    return data


def copy_pack(source: Path, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)


def run_export() -> None:
    env = os.environ.copy()
    if "NITNEM_CONTENT_VERSION" not in env and CONTENT_FILE.is_file():
        env["NITNEM_CONTENT_VERSION"] = str(load_json(CONTENT_FILE).get("content_version", 1))
    subprocess.run(
        [sys.executable, str(NITNEM_APP_DIR / "export_nitnem_content.py")],
        cwd=str(ROOT),
        env=env,
        check=True,
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Export the Nitnem content pack and copy the exact JSON to app assets.",
    )
    parser.add_argument(
        "--no-export",
        action="store_true",
        help="Only validate/copy the existing generated content file.",
    )
    parser.add_argument(
        "--content-version",
        type=int,
        help="Set NITNEM_CONTENT_VERSION for the export. Use this when publishing a new content release.",
    )
    args = parser.parse_args()

    if args.content_version is not None:
        os.environ["NITNEM_CONTENT_VERSION"] = str(args.content_version)

    if not args.no_export:
        run_export()

    pack = validate_pack(CONTENT_FILE)
    targets = [MOBILE_ASSET, SGGS_MOBILE_ASSET]
    for target in targets:
        copy_pack(CONTENT_FILE, target)
        validate_pack(target)
        if CONTENT_FILE.read_bytes() != target.read_bytes():
            raise ValueError(f"{target} is not byte-identical to {CONTENT_FILE}")

    print("Nitnem content pack synchronized")
    print(f"  package_id: {pack['package_id']}")
    print(f"  schema_version: {pack['schema_version']}")
    print(f"  content_version: {pack['content_version']}")
    for target in targets:
        print(f"  copied: {target.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
