"""
Generate DocFx toc.yml files from Azure DevOps Wiki .order files.

Azure DevOps wiki uses .order files to define page ordering.
Each line in .order is a page name (without .md extension, with dashes for spaces).

Strategy: Generate a toc.yml in each directory that has content.
Sub-directories are referenced via href: subdir/ which makes DocFx look for subdir/toc.yml.
"""

import sys
from pathlib import Path
from urllib.parse import unquote


def decode_name(filename: str) -> str:
    """Convert wiki filename to human-readable name.
    E.g., 'Architecture-Decision-Records' -> 'Architecture Decision Records'
    """
    name = filename.replace('.md', '')
    name = unquote(name)
    name = name.replace('-', ' ')
    return name


def get_ordered_names(directory: Path) -> list:
    """Get ordered list of page names from .order file or fallback to alphabetical."""
    order_file = directory / ".order"
    if order_file.exists():
        return [
            line.strip()
            for line in order_file.read_text(encoding='utf-8').splitlines()
            if line.strip()
        ]
    # Fallback: alphabetical order of .md files
    return sorted([f.stem for f in directory.glob("*.md")])


def write_toc_yaml_lines(items: list, indent: int = 0) -> list:
    """Generate YAML lines for TOC items."""
    prefix = "  " * indent
    lines = []
    for item in items:
        lines.append(f"{prefix}- name: {item['name']}")
        if "href" in item:
            lines.append(f"{prefix}  href: {item['href']}")
        if "topicHref" in item:
            lines.append(f"{prefix}  topicHref: {item['topicHref']}")
    return lines


def generate_toc_recursive(directory: Path):
    """Generate toc.yml for a directory and all subdirectories."""
    ordered_names = get_ordered_names(directory)
    items = []
    seen = set()

    for name in ordered_names:
        md_file = directory / f"{name}.md"
        sub_dir = directory / name
        display_name = decode_name(name)
        seen.add(name)

        item = {"name": display_name}

        if sub_dir.exists() and sub_dir.is_dir():
            # Has sub-pages: generate sub toc.yml and reference the directory
            generate_toc_recursive(sub_dir)
            item["href"] = f"{name}/"
            if md_file.exists():
                item["topicHref"] = f"{name}.md"
        elif md_file.exists():
            item["href"] = f"{name}.md"
        else:
            continue

        items.append(item)

    # Add any .md files not in .order
    for md_file in sorted(directory.glob("*.md")):
        name = md_file.stem
        if name not in seen:
            items.append({
                "name": decode_name(name),
                "href": md_file.name
            })

    if not items:
        return

    toc_file = directory / "toc.yml"
    lines = write_toc_yaml_lines(items)
    toc_file.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(f"  [+] {toc_file} ({len(items)} items)")


def main():
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <wiki_dir>")
        sys.exit(1)

    wiki_dir = Path(sys.argv[1])
    if not wiki_dir.exists():
        print(f"[!] Wiki dir {wiki_dir} does not exist, skipping...")
        return

    generate_toc_recursive(wiki_dir)


if __name__ == "__main__":
    main()
