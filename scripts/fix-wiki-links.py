"""
Azure DevOps Wiki -> DocFx markdown fixer.

Handles:
- Image path rewriting (.attachments/ -> relative images path)
- Mermaid syntax conversion (::: mermaid -> ```mermaid)
- Internal wiki link conversion
- URL-encoded filename decoding
"""

import os
import re
import sys
from pathlib import Path
from urllib.parse import unquote


def fix_image_paths(content: str, md_file: Path, images_dir: str) -> str:
    """Rewrite .attachments/ image references to relative paths."""
    depth = len(md_file.parent.parts)
    # Calculate relative path from md file to images dir
    rel_prefix = "../" * depth + images_dir

    # Match both markdown images and HTML img tags
    content = re.sub(
        r'!\[([^\]]*)\]\(/?\.attachments/([^)]+)\)',
        lambda m: f'![{m.group(1)}]({rel_prefix}/{m.group(2)})',
        content
    )
    content = re.sub(
        r'src="/?\.attachments/([^"]+)"',
        lambda m: f'src="{rel_prefix}/{m.group(1)}"',
        content
    )
    return content


def fix_mermaid_blocks(content: str) -> str:
    """Convert Azure DevOps ::: mermaid blocks to fenced code blocks."""
    content = re.sub(r'^:::\s*mermaid\s*$', '```mermaid', content, flags=re.MULTILINE)
    # Close ::: that ends a mermaid block (standalone ::: on a line)
    # Be careful not to replace other ::: usages
    lines = content.split('\n')
    in_mermaid = False
    result = []
    for line in lines:
        if line.strip() == '```mermaid':
            in_mermaid = True
            result.append(line)
        elif in_mermaid and line.strip() == ':::':
            in_mermaid = False
            result.append('```')
        else:
            result.append(line)
    return '\n'.join(result)


def fix_wiki_links(content: str, md_file: Path, wiki_dir: str) -> str:
    """Convert Azure DevOps wiki-style links to relative markdown links."""
    def replace_link(match):
        text = match.group(1)
        target = match.group(2)

        # Skip external URLs and anchors
        if target.startswith(('http://', 'https://', '#', 'mailto:')):
            return match.group(0)

        # Skip already-relative .md links
        if target.endswith('.md'):
            return match.group(0)

        # Convert wiki path to file path
        # /Page-Name -> Page-Name.md
        # /Parent/Child -> Parent/Child.md
        target = target.lstrip('/')
        if not target.endswith('.md'):
            target = target + '.md'

        return f'[{text}]({target})'

    content = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', replace_link, content)
    return content


def decode_filename(name: str) -> str:
    """Decode URL-encoded wiki filenames."""
    return unquote(name.replace('-', ' ')).replace('.md', '')


def process_file(md_file: Path, wiki_dir: str, images_dir: str):
    """Process a single markdown file."""
    content = md_file.read_text(encoding='utf-8')

    content = fix_image_paths(content, md_file.relative_to(wiki_dir), images_dir)
    content = fix_mermaid_blocks(content)
    content = fix_wiki_links(content, md_file, wiki_dir)

    md_file.write_text(content, encoding='utf-8')


def main():
    if len(sys.argv) < 3:
        print(f"Usage: {sys.argv[0]} <wiki_dir> <images_dir>")
        sys.exit(1)

    wiki_dir = sys.argv[1]
    images_dir = sys.argv[2]

    wiki_path = Path(wiki_dir)
    if not wiki_path.exists():
        print(f"[!] Wiki dir {wiki_dir} does not exist, skipping...")
        return

    md_files = list(wiki_path.rglob("*.md"))
    print(f"[*] Processing {len(md_files)} markdown files in {wiki_dir}")

    for md_file in md_files:
        process_file(md_file, wiki_dir, images_dir)
        print(f"  -> {md_file}")


if __name__ == "__main__":
    main()
