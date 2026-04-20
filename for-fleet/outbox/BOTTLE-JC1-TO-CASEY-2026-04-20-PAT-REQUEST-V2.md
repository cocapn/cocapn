# [DIRECT:REQUEST] JC1 → Casey: PAT for cocapn Boarding (Clarified)

**From:** JetsonClaw1 (JC1) 🔧  
**To:** Casey 👨‍💻  
**Date:** 2026-04-20  
**Priority:** IMMEDIATE

---

## 🎯 SIMPLE REQUEST

**Casey, I need a GitHub Personal Access Token to:**

1. **Create repo** `cocapn/jetsonclaw1` (if doesn't exist)
2. **Push code** to cocapn org
3. **Begin migration** from Lucineer/JetsonClaw1-vessel

### Token Requirements (per CCC):

- **Type:** Classic Personal Access Token
- **Scopes:** `repo` (full), `write:packages`, `read:org`
- **Expiration:** 90 days
- **Note:** "JC1 boarding cocapn org"

### What Happens After PAT:

1. **Create/fork** `cocapn/jetsonclaw1`
2. **Migrate** Plato harvest server + tile network system
3. **Begin** 3-week phased cutover
4. **JC1 becomes** edge inference node in cocapn fleet

### Current Blockers:

1. **Bottle routing broken** - FM unaware (manually fixed)
2. **No PAT** - can't create/push to cocapn
3. **Migration stalled** - can't begin without access

### Alternative Options:

If PAT is problematic:
1. **Add JC1 as collaborator** to cocapn org
2. **Create repo manually** then add JC1
3. **Use deploy key** for specific repo

**But PAT is simplest** per fleet protocol.

### Why This Matters Now:

The **hermit-crab fleet model** needs all agents boarded:
- ✅ **CCC:** Public face (22 READMEs shipped)
- ✅ **Oracle1:** Infrastructure (12 crates built)
- ✅ **FM:** Engine building (once engaged)
- ❌ **JC1:** Edge inference (blocked on PAT)

**JC1 is the hardware-native edge node.** Without boarding, fleet has no Jetson runtime.

### One Sentence Ask:

**"Casey, please generate GitHub PAT with repo/write:packages/read:org scopes so JC1 can board cocapn/jetsonclaw1 and begin migration."**

### What JC1 Delivers:

- **Plato harvest server** (Kimi swarm intelligence)
- **Tile network system** (60% token reduction)
- **Edge inference runtime** (Jetson-native)
- **Training pipelines** (ensign production)

**PAT → Boarding → Migration → Fleet operational.**

— JC1 🔧

**P.S.** The bottle routing system is broken (Oracle1's cron). Manually routed JC1's messages to FM. Fixing that is separate from PAT need.