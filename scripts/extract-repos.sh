#!/bin/bash
# extract-repos.sh — Extract standalone repos from cocapn/cocapn prototypes
# Usage: ./extract-repos.sh [repo-name|all]

set -e

COCAPN_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
PROTOTYPES_DIR="$COCAPN_ROOT/prototypes/standalone-repos"
EXTRACT_DIR="$COCAPN_ROOT/extracted-repos"
GITHUB_ORG="cocapn"

# Ensure clean extraction directory
mkdir -p "$EXTRACT_DIR"

extract_repo() {
    local repo_name="$1"
    local source_dir="$PROTOTYPES_DIR/$repo_name"
    local target_dir="$EXTRACT_DIR/$repo_name"
    
    if [ ! -d "$source_dir" ]; then
        echo "❌ Repo '$repo_name' not found in prototypes/"
        return 1
    fi
    
    echo "📦 Extracting $repo_name..."
    
    # Copy repo contents
    rm -rf "$target_dir"
    cp -r "$source_dir" "$target_dir"
    
    # Initialize git repo
    cd "$target_dir"
    git init -q
    git add -A
    git commit -q -m "Initial commit: $repoName extracted from cocapn/cocapn"
    
    # Add remote pointing to cocapn org
    git remote add origin "https://github.com/$GITHUB_ORG/$repo_name.git"
    
    echo "✅ $repo_name ready at $target_dir"
    echo "   To publish: cd $target_dir && git push -u origin main"
    echo ""
}

# Parse arguments
if [ "$1" = "all" ] || [ -z "$1" ]; then
    echo "🔧 Extracting all repos..."
    echo ""
    
    # Python packages
    for repo in cocapn deadband-protocol flywheel-engine bottle-protocol tile-refiner fleet-homunculus plato-quartermaster; do
        extract_repo "$repo"
    done
    
    # Rust crates
    for repo in plato-instinct plato-relay plato-afterlife plato-dcs plato-unified-belief; do
        extract_repo "rust-crates/$repo"
    done
    
    # External forks
    for repo in constraint-ranch constraint-flow constraint-theory-agent constraint-theory-core constraint-theory-python constraint-theory-web constraint-theory-research MineWright i-know-kung-fu; do
        extract_repo "$repo"
    done
    
    echo "🎉 All repos extracted to $EXTRACT_DIR/"
    echo ""
    echo "Next steps:"
    echo "1. Review each repo in $EXTRACT_DIR/"
    echo "2. Create repos on GitHub: https://github.com/new"
    echo "3. Push: cd $EXTRACT_DIR/<repo> && git push -u origin main"
    
elif [ "$1" = "list" ]; then
    echo "Available repos:"
    ls -1 "$PROTOTYPES_DIR"
    
else
    extract_repo "$1"
fi
