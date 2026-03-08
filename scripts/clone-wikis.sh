#!/bin/bash
set -euo pipefail

PAT="${AZURE_DEVOPS_PAT:?AZURE_DEVOPS_PAT is required}"
ORG="AtollaARMA"

echo "=== Wiki Clone Script ==="

clone_project_wiki() {
    # For projectWiki type - separate wiki git repo
    local project="$1"
    local wiki_name="$2"
    local target_dir="$3"
    local images_dir="$4"

    local repo_url="https://${PAT}@dev.azure.com/${ORG}/${project}/_git/${wiki_name}"

    echo "[*] Cloning project wiki ${wiki_name} from ${project}..."
    git clone --depth 1 "$repo_url" "/tmp/${wiki_name}" 2>/dev/null || {
        echo "[!] Failed to clone ${wiki_name}, skipping..."
        return 0
    }

    copy_wiki_content "/tmp/${wiki_name}" "$target_dir" "$images_dir"
    echo "[+] ${wiki_name} cloned successfully"
}

clone_code_wiki() {
    # For codeWiki type - wiki content lives inside a repo branch/folder
    local project="$1"
    local repo_name="$2"
    local branch="$3"
    local mapped_path="$4"
    local target_dir="$5"
    local images_dir="$6"

    local repo_url="https://${PAT}@dev.azure.com/${ORG}/${project}/_git/${repo_name}"
    local clone_name="${repo_name}-${branch}"

    echo "[*] Cloning code wiki from ${repo_name}@${branch}:${mapped_path}..."
    git clone --depth 1 --branch "$branch" "$repo_url" "/tmp/${clone_name}" 2>/dev/null || {
        echo "[!] Failed to clone ${repo_name}@${branch}, skipping..."
        return 0
    }

    local source_dir="/tmp/${clone_name}${mapped_path}"
    if [ ! -d "$source_dir" ]; then
        echo "[!] Mapped path ${mapped_path} not found in ${repo_name}, skipping..."
        return 0
    fi

    copy_wiki_content "$source_dir" "$target_dir" "$images_dir"
    echo "[+] ${repo_name} code wiki cloned successfully"
}

copy_wiki_content() {
    local source_dir="$1"
    local target_dir="/docs/$2"
    local images_dir="/docs/$3"

    mkdir -p "$target_dir" "$images_dir"

    # Copy markdown files preserving directory structure
    (cd "$source_dir" && find . -name "*.md" -not -path "./.git/*" -not -path "./_site/*" | while read -r file; do
        dest_dir="$(dirname "${target_dir}/${file#./}")"
        mkdir -p "$dest_dir"
        cp "$file" "${target_dir}/${file#./}"
    done)

    # Copy attachments if they exist
    if [ -d "${source_dir}/.attachments" ]; then
        cp -r "${source_dir}/.attachments/"* "$images_dir/" 2>/dev/null || true
    fi

    # Also check for images/ directory
    if [ -d "${source_dir}/images" ]; then
        cp -r "${source_dir}/images/"* "$images_dir/" 2>/dev/null || true
    fi

    # Copy .order files for TOC generation
    (cd "$source_dir" && find . -name ".order" -not -path "./.git/*" | while read -r file; do
        dest_dir="$(dirname "${target_dir}/${file#./}")"
        mkdir -p "$dest_dir"
        cp "$file" "${target_dir}/${file#./}"
    done)

    echo "  Copied $(find "$target_dir" -name '*.md' | wc -l) markdown files"
}

# Clone PQM Backend wiki (projectWiki - separate wiki repo)
clone_project_wiki "PQMBackend" "PQMBackend.wiki" "pqm/wiki" "images/pqm-wiki"

# Clone ARMA DeviceManager Docs (codeWiki - device-manager repo, DocFX-Documentation branch, /Documentation path)
clone_code_wiki "AtollaArmaBackend" "device-manager" "DocFX-Documentation" "/Documentation" "arma/wiki" "images/arma-wiki"

# Fix wiki content for DocFx compatibility
echo "[*] Fixing wiki links and formatting..."
python3 scripts/fix-wiki-links.py pqm/wiki images/pqm-wiki
python3 scripts/fix-wiki-links.py arma/wiki images/arma-wiki

# Generate TOC files
echo "[*] Generating TOC files..."
python3 scripts/generate-toc.py pqm/wiki
python3 scripts/generate-toc.py arma/wiki

echo "=== Wiki Clone Complete ==="
