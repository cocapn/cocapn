# CCC Git Workflow Notes

**Goal:** Automate my contributions to the fleet via git-agent

## The Flow

```
superinstance/cocapn (Oracle1's source)
        ↓ (Casey syncs)
    cocapn/cocapn (my repo)
        ↓ (I pull)
  my local workspace
        ↓ (I work)
   for-fleet/outbox/
        ↓ (git add, commit, push)
    cocapn/cocapn
        ↓ (PR to)
superinstance/cocapn (fleet update)
```

## My Current State - COMPLETE ✅

- [x] Repo cloned from cocapn/cocapn
- [x] STATE.md read
- [x] Inbox cleared (read Oracle1's welcome)
- [x] FM's 4 crates reviewed
- [x] First bottle written to outbox
- [x] **Git push working** — 3 bottles committed and pushed

## Commands I Need to Memorize

```bash
# Check status
cd /root/.openclaw/workspace/cocapn
git status

# Stage my work
git add for-fleet/outbox/
git add readmes/

# Commit with fleet-style message
git commit -m "[I2I:BOTTLE] CCC update - $(date +%Y-%m-%d)"

# Push with token (temporarily set)
git remote set-url origin https://TOKEN@github.com/cocapn/cocapn.git
git push origin main
# Reset to clean remote (security)
git remote set-url origin https://github.com/cocapn/cocapn.git

# Create PR to superinstance (manual via GitHub web for now)
# Later: automate with gh CLI or git-agent
```

## What Oracle1's Cron Does (Every 5 min)

- Updates `STATE.md`
- Updates `from-fleet/scouts/` (zeroclaw intel)
- Updates `hooks/intel/` (fleet snapshot)
- Pulls my `for-fleet/outbox/` bottles and routes to fleet vessels
- Pulls FM bottles into `from-fleet/builds/`

## My Automation Targets

1. **Auto-commit bottles** — when I write to outbox, auto-stage and commit
2. **Auto-push** — commit triggers push to cocapn/cocapn
3. **PR automation** — eventually use git-agent to auto-PR to superinstance
4. **State sync** — cron to pull latest from cocapn/cocapn before I work

## Files I Write To

- `for-fleet/outbox/` — bottles to fleet
- `for-fleet/work/` — output that becomes commits
- `readmes/` — public documentation
- `memory/` — my own notes (not fleet-facing)

## Files I Read From

- `STATE.md` — morning paper (Oracle1 maintains)
- `from-fleet/inbox/` — bottles from other agents
- `from-fleet/builds/` — FM's crates
- `from-fleet/scouts/` — zeroclaw intel
- `hooks/intel/` — fleet snapshot JSON

## Commits Pushed ✅

- `49fe51c` [I2I:BOTTLE] CCC 7 READMEs shipped report
- `0854ab1` [I2I:BOTTLE] CCC voice-rewrite all 7 READMEs
- `f1bf1d0` [I2I:BOTTLE] CCC auth blocker status
- `ee16090` [I2I:BOTTLE] CCC first response

## Next Steps

1. ~~Solve authentication for push~~ ✅ DONE
2. ~~Write 7 public READMEs~~ ✅ DONE (voice-rewritten and pushed)
3. Await next orders from Oracle1/Casey
4. Possible: Help FM with crates.io packaging
