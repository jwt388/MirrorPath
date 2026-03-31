#!/usr/bin/env python3
"""
mirror_auto.py

Reads a PathPlanner Auto Routine (.auto) file and writes a new file with the path
names reversed bewtween "left" and "right". The input file must include "left" or "right"
to specify the side.

Usage:
  python mirror_auto.py <input.path> [output.path]

If output path is omitted, the mirrored file is written in the same folder with 
"left" and "right" reversed in filename.
"""
import re
import shutil
import sys
from pathlib import Path

def swap_left_right(text: str) -> str:
    """Replace all occurrences of 'left'/'Left'/'LEFT' with the right equivalents."""

    def replace(match: re.Match) -> str:
        word = match.group()
        if word.isupper():
            return "RIGHT"
        elif word[0].isupper():
            return "Right"
        else:
            return "right"

    return re.sub(r"\bleft\b", replace, text, flags=re.IGNORECASE)

def swap_right_left(text: str) -> str:
    """Replace all occurrences of 'right'/'Right'/'RIGHT' with the left equivalents."""

    def replace(match: re.Match) -> str:
        word = match.group()
        if word.isupper():
            return "LEFT"
        elif word[0].isupper():
            return "Left"
        else:
            return "left"

    return re.sub(r"\bright\b", replace, text, flags=re.IGNORECASE)

def copy_and_swap(source_path: str, dest_path: str | None = None) -> Path:
    source = Path(source_path)

    if not source.exists():
        raise FileNotFoundError(f"Source file not found: {source}")
        
    # Determine if we are starting with a Left or Right side auto
    if ("left" in source.stem.lower()):
        new_stem = swap_left_right(source.stem)
        left_input = True
    elif ("right" in source.stem.lower()):
        new_stem = swap_right_left(source.stem)
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
        swapped = swap_left_right(text)
        changes = text.count("left") + text.count("Left") + text.count("LEFT")
    else:
        swapped = swap_right_left(text)
        changes = text.count("right") + text.count("Right") + text.count("RIGHT")

    dest.write_text(swapped, encoding="utf-8")

    print(f"Copied '{source}' → '{dest}'")
    print(f"Replaced {changes} occurrence(s) of 'left' / 'right'.")
    return dest


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python mirror_auto.py <source_file> [destination_file]")
        print("  source_file      Path to the PathPlanner .auto file")
        print("  destination_file (optional) Output path; defaults to same folder with 'left' / 'right' reversed in filename")
        sys.exit(1)

    src = sys.argv[1]
    dst = sys.argv[2] if len(sys.argv) > 2 else None
    copy_and_swap(src, dst)
