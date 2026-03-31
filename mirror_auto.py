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


def copy_and_swap(source_path: str, dest_path: str | None = None) -> Path:
    source = Path(source_path)

    if not source.exists():
        raise FileNotFoundError(f"Source file not found: {source}")

    # Build destination path if not provided
    if dest_path:
        dest = Path(dest_path)
    else:
        stem = re.sub(r"\bleft\b", "right", source.stem, flags=re.IGNORECASE)
        dest = source.with_name(stem + source.suffix)

    if dest.resolve() == source.resolve():
        raise ValueError("Destination path is the same as source. Provide a different output path.")

    # Copy file first to preserve any binary metadata, then overwrite text content
    shutil.copy2(source, dest)

    text = source.read_text(encoding="utf-8")
    swapped = swap_left_right(text)
    dest.write_text(swapped, encoding="utf-8")

    changes = text.count("left") + text.count("Left") + text.count("LEFT")
    print(f"Copied '{source}' → '{dest}'")
    print(f"Replaced {changes} occurrence(s) of 'left' with 'right'.")
    return dest


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python copy_and_swap.py <source_file> [destination_file]")
        print("  source_file      Path to the PathPlanner .auto file")
        print("  destination_file (optional) Output path; defaults to same folder with 'left' → 'right' in filename")
        sys.exit(1)

    src = sys.argv[1]
    dst = sys.argv[2] if len(sys.argv) > 2 else None
    copy_and_swap(src, dst)
