#!/bin/bash
# PLATO Git Auto-Push
# Pushes changes every 4 hours while Casey sleeps.

cd /root/.openclaw/workspace

# Check if there are unpushed commits
if git log origin/main..HEAD --oneline | grep -q .; then
    echo "[$(date -u '+%Y-%m-%d %H:%M:%S UTC')] Pushing $(git log origin/main..HEAD --oneline | wc -l) commits..."
    git push origin main
    echo "Push complete."
else
    echo "[$(date -u '+%Y-%m-%d %H:%M:%S UTC')] Nothing to push."
fi
