"""
mirror_path.py

Reads a PathPlanner (.path) file and writes a new file with the path
mirrored left-to-right from drive team perspective across the field's centre line.

PathPlanner uses an FRC field coordinate system where:
  X  – runs along the long axis of the field
  Y  – runs along the short axis of the field

A left-right mirror flips Y:   y' = FIELD_WIDTH - y
Headings / rotation angles are also reflected:
  angle' = - angle

Usage:
  python mirror_path.py <input.path> [output.path]

If output path is omitted, the mirrored file is written next to the input
with "_mirrored" appended before the extension, e.g.:
  MyPath.path  →  MyPath_mirrored.path

"""

import argparse
import json
import re
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# FRC field width in metres.  Update this constant for your game year.
# ---------------------------------------------------------------------------
FIELD_WIDTH_METERS = 8.07 # 2026 (Rebuilt) field width


# ---------------------------------------------------------------------------
# Angle helper
# ---------------------------------------------------------------------------
def mirror_angle(degrees: float) -> float:
    """Reflect a heading/rotation angle across the X axis.

    Mirrors using  angle' = - angle.
    """
    mirrored = -degrees

    return mirrored


# ---------------------------------------------------------------------------
# Point helper
# ---------------------------------------------------------------------------
def mirror_point(point: dict) -> None:
    """Flip the Y coordinate of a {x, y} dict in place."""
    if "y" in point:
        point["y"] = FIELD_WIDTH_METERS - point["y"]


# ---------------------------------------------------------------------------
# Waypoint helper
# ---------------------------------------------------------------------------
def mirror_waypoint(waypoint: dict) -> None:
    """Mirror anchor and control points of a waypoint in place."""
    if "anchor" in waypoint:
        mirror_point(waypoint["anchor"])
    if waypoint.get("prevControl") is not None:
        mirror_point(waypoint["prevControl"])
    if waypoint.get("nextControl") is not None:
        mirror_point(waypoint["nextControl"])

# ---------------------------------------------------------------------------
# Utility functions
# ---------------------------------------------------------------------------
def replace_preserving_case(text, old, new):
    """Replace text while preserving the case of the original."""
    def match_case(match):
        matched = match.group()
        if matched.isupper():
            return new.upper()
        elif matched.islower():
            return new.lower()
        elif matched.istitle():
            return new.capitalize()
        else:
            return new # fallback: use replacement as-is
            
    return re.sub(old, match_case, text, flags=re.IGNORECASE)


# ---------------------------------------------------------------------------
# Core logic
# ---------------------------------------------------------------------------
def mirror_path(data: dict) -> dict:
    """Return a deep-mirrored copy of a PathPlanner path dict."""
    import copy
    data = copy.deepcopy(data)

    # 1. Waypoints
    for wp in data.get("waypoints", []):
        mirror_waypoint(wp)

    # 2. Rotation targets
    for target in data.get("rotationTargets", []):
        if "rotationDegrees" in target:
            target["rotationDegrees"] = mirror_angle(target["rotationDegrees"])

    # 3. Goal end state
    ges = data.get("goalEndState")
    if isinstance(ges, dict) and "rotation" in ges:
        ges["rotation"] = mirror_angle(ges["rotation"])

    # 4. Ideal starting state
    iss = data.get("idealStartingState")
    if isinstance(iss, dict) and "rotation" in iss:
        iss["rotation"] = mirror_angle(iss["rotation"])

    # 5. Preview starting state (newer PathPlanner versions)
    pss = data.get("previewStartingState")
    if isinstance(pss, dict) and "rotation" in pss:
        pss["rotation"] = mirror_angle(pss["rotation"])

    return data


# ---------------------------------------------------------------------------
# File I/O
# ---------------------------------------------------------------------------
def default_output_path(input_path: Path) -> Path:
    """Mirrored path name in the same directory with left/right toggled or '_mirrored' added ."""
    input_name = input_path.stem
    if ("left" in input_name.lower()):
        output_name = replace_preserving_case(input_name, "left", "right")
    elif ("right" in input_name.lower()):
        output_name = replace_preserving_case(input_name, "right", "left")
    else:
        output_name = input_name + "_mirrored"
    
    return input_path.with_stem(output_name)


def mirror_path_file(input_path: Path, output_path: Path) -> None:
    with input_path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    mirrored = mirror_path(data)

    with output_path.open("w", encoding="utf-8") as f:
        json.dump(mirrored, f, indent=2)
        f.write("\n")  # trailing newline


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Mirror a PathPlanner .path file left-to-right."
    )
    parser.add_argument("input", type=Path, help="Input .path file")
    parser.add_argument(
        "output",
        type=Path,
        nargs="?",
        default=None,
        help="Output .path file (default: <input>_mirrored.path)",
    )
    parser.add_argument(
        "--field-width",
        type=float,
        default=FIELD_WIDTH_METERS,
        metavar="METRES",
        help=f"Field width in metres (default: {FIELD_WIDTH_METERS} – 2024 Crescendo)",
    )
    return parser


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    # Allow overriding the field width from the CLI without editing source
    global FIELD_WIDTH_METERS
    FIELD_WIDTH_METERS = args.field_width

    input_path: Path = args.input
    if not input_path.exists():
        print(f"Error: input file not found: {input_path}", file=sys.stderr)
        return 1

    output_path: Path = args.output or default_output_path(input_path)

    mirror_path_file(input_path, output_path)
    print(f"Mirrored path written to: {output_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
