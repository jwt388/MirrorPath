#!/usr/bin/env python3
"""
mirror_auto.py

Reads a PathPlanner Auto Routine (.auto) file and writes a new file with the path
names reversed bewtween "left" and "right". The input file must include "left" or "right"
to specify the side. Each path in the auto is also mirrored left/right.

Usage:
  python mirror_auto.py <input.path> [output.path]

If output path is omitted, the mirrored file is written in the same folder with 
"left" and "right" reversed in filename.
"""
import json
import re
import shutil
import sys
from pathlib import Path
from mirror_path import mirror_path_file, default_output_path, replace_preserving_case

def copy_and_swap(source_path: str, dest_path: str | None = None) -> Path:
    source = Path(source_path)

    if not source.exists():
        raise FileNotFoundError(f"Source file not found: {source}")
        
    # Determine if we are starting with a Left or Right side auto
    if ("left" in source.stem.lower()):
        new_stem = replace_preserving_case(source.stem, "left", "right")
        left_input = True
    elif ("right" in source.stem.lower()):
        new_stem = replace_preserving_case(source.stem, "right", "left")
        left_input = False
    else:
        raise ValueError("Auto to mirror must be a left or right side auto.")

    # Build destination path if not provided
    if dest_path:
        dest = Path(dest_path)
    else:
        dest = source.with_name(new_stem + source.suffix)

    if dest.resolve() == source.resolve():
        raise ValueError("Destination path is the same as source. Provide a different output path.")

    # Copy file first to preserve any binary metadata, then overwrite text content
    shutil.copy2(source, dest)

    text = source.read_text(encoding="utf-8")
    if left_input:
        swapped = replace_preserving_case(text, "left", "right")
        changes = text.count("left") + text.count("Left") + text.count("LEFT")
    else:
        swapped = replace_preserving_case(text, "right", "left")
        changes = text.count("right") + text.count("Right") + text.count("RIGHT")

    dest.write_text(swapped, encoding="utf-8")

    print(f"Copied '{source}' → '{dest}'")
    print(f"Replaced {changes} occurrence(s) of 'left' / 'right'.")
    return dest

def list_path_names(file_path: str) -> list[str]:
    """Return all pathName values found in a PathPlanner .auto file."""
    source = Path(file_path)

    if not source.exists():
        raise FileNotFoundError(f"File not found: {source}")

    data = json.loads(source.read_text(encoding="utf-8"))
    path_names = extract_path_names(data)
    return path_names


def extract_path_names(obj, found: list[str] | None = None) -> list[str]:
    """Recursively walk the JSON structure and collect every 'pathName' value."""
    if found is None:
        found = []

    if isinstance(obj, dict):
        if "pathName" in obj and isinstance(obj["pathName"], str):
            found.append(obj["pathName"])
        for value in obj.values():
            extract_path_names(value, found)
    elif isinstance(obj, list):
        for item in obj:
            extract_path_names(item, found)

    return found

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python mirror_auto.py <source_file> [destination_file]")
        print("  source_file      Path to the PathPlanner .auto file")
        print("  destination_file (optional) Output path; defaults to same folder with 'left' / 'right' reversed in filename")
        sys.exit(1)

    src = sys.argv[1]
    dst = sys.argv[2] if len(sys.argv) > 2 else None
    # Create the new mirrored auto routine
    copy_and_swap(src, dst)  
    
    # Find the paths that need to be mirrored
    path_names = list_path_names(src)

    if not path_names:
        print("No pathName entries found.")
    else:
        print(f"Found {len(path_names)} pathName entry/entries:")
        for name in path_names:
            source_path = Path(name+".path")
            
            if not source_path.exists():
                print(f"Error: source path file not found: {source_path}", file=sys.stderr)
            else:
                dest_path: Path = default_output_path(source_path)
                mirror_path_file(source_path, dest_path)
                print(f"Mirrored '{source_path}' → '{dest_path}'")
          