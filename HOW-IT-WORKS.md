# Skill Hub — How It Works

How the Claude Code plugin system loads skills from this directory marketplace. Authored after a 90-minute debugging session on 2026-05-19 to capture the actual mechanics versus assumed mechanics.

## The five layers

A plugin loaded from this marketplace requires all five layers to line up. Skipping any one of them produces silent failures or misleading errors.

### 1. Marketplace declaration (`~/.claude/settings.json`)

Tells Claude Code "a marketplace lives at this filesystem path":

```json
"extraKnownMarketplaces": {
  "skill-hub-local": {
    "source": {
      "source": "directory",
      "path": "~/dev/skill-hub"
    }
  }
}
```

Key detail: `source.source: "directory"` (NOT `"local"`, NOT `"github"`). For directory sources, Claude reads the marketplace live from disk — no clone, no cache. Mirror the same block in `~/.claude-work/settings.json` for tools that read the legacy location.

### 2. Marketplace manifest (`~/dev/skill-hub/.claude-plugin/marketplace.json`)

Filename must be exactly `marketplace.json` and live in `.claude-plugin/`. Lists each plugin:

```json
{
  "$schema": "https://anthropic.com/claude-code/marketplace.schema.json",
  "name": "skill-hub-local",
  "owner": { "name": "..." },
  "plugins": [
    {
      "name": "skill-hub-meta",
      "source": "./plugins/skill-hub-meta",
      "version": "0.1.0",
      "description": "..."
    }
  ]
}
```

`source` is a path relative to the marketplace root (parent of `.claude-plugin/`). String form `"./plugins/x"` works fine for directory marketplaces — there is no need to convert it to the object form `{"source": "directory", "path": "..."}` used by `git-subdir` plugins in `claude-plugins-official`.

### 3. Per-plugin folder layout (`~/dev/skill-hub/plugins/<plugin>/`)

Each plugin needs this exact structure:

```
plugins/skill-hub-meta/
├── .claude-plugin/
│   └── plugin.json          ← REQUIRED, minimum {name, description, version}
└── skills/
    ├── brainstorming/
    │   └── SKILL.md
    └── ...
```

**`plugin.json` minimum:**

```json
{
  "name": "skill-hub-meta",
  "description": "...",
  "version": "0.1.0"
}
```

**`SKILL.md` minimum — YAML frontmatter is MANDATORY:**

```markdown
---
name: brainstorming
description: "Use this before any creative work — explores intent before implementation"
---

# brainstorming

...body...
```

**Without the `---` frontmatter fences, Claude Code silently skips the SKILL.md.** This is the most common bug — old skill files without frontmatter get loaded as zero-skill plugins, producing misleading "plugin not found in marketplace" errors despite the file being on disk.

### 4. Per-scope enablement

Reference plugins as `<plugin>@<marketplace>`. Lives in any of:

- `~/.claude/settings.json` (user, global)
- `~/.claude-work/settings.json` (legacy user, global)
- `<project>/.claude/settings.json` (per-project override)

```json
"enabledPlugins": {
  "skill-hub-meta@skill-hub-local": true,
  "skill-hub-quality@skill-hub-local": true
}
```

Per-project settings deep-merge with global. Setting `"plugin": false` in a project file disables a globally-enabled plugin for that project only — but **note**: errors still fire for entries with `false` values because the loader validates all references regardless of value.

### 5. The reload command

```
/reload-plugins
```

Re-reads marketplaces from disk and refreshes the loaded set without restarting Claude Code. Run after any change to `marketplace.json`, `plugin.json`, or SKILL.md frontmatter.

After `/reload-plugins`, run `/doctor` for error details. The reload count is informational (`N plugins · M skills · ...`); the actual diagnosis lives in `/doctor`.

## What does NOT matter

These red herrings will waste your time:

- **`installed_plugins.json`** at `~/.claude-work/plugins/` — for directory-source marketplaces, this is just stale state pointing at deleted cache dirs. `/reload-plugins` ignores it and reads the marketplace live.
- **`gitCommitSha`** in `installed_plugins.json` — only used for github sources.
- **Plugin version mismatch** between `marketplace.json` and `plugin.json` — not fatal as long as both files parse.
- **The `source` field format in `marketplace.json`** — string form (`"./plugins/x"`) and object form (`{"source": "directory", "path": "..."}`) both work for directory marketplaces.
- **The `plugin-catalog-cache.json`** at `~/.claude-work/plugins/` — caches Anthropic-curated official-catalog metadata. Doesn't drive loading for local marketplaces, but may need invalidating if stale state is confusing the loader (delete the file and `/reload-plugins`).

## Pre-flight checklist before adding a new plugin

1. Create `~/dev/skill-hub/plugins/<plugin>/.claude-plugin/plugin.json`
2. Add `skills/<skill>/SKILL.md` files — **YAML frontmatter first, then body**
3. Append an entry to `~/dev/skill-hub/.claude-plugin/marketplace.json`
4. Add `"<plugin>@skill-hub-local": true` to the relevant settings.json
5. Run `/reload-plugins` in any Claude Code session
6. Confirm with `/doctor` — no errors expected

## Failure-mode signatures

| Symptom | Likely cause | Fix |
|---|---|---|
| `Plugin X not found in marketplace Y` | SKILL.md missing YAML frontmatter → plugin loads with 0 skills → reported as missing | Check `head -1 SKILL.md` returns `---`; check `name:` and `description:` keys present |
| `Marketplace Y not found` | Marketplace not declared in `extraKnownMarketplaces`, OR `source.source` value invalid (must be `"github"` or `"directory"`, not `"local"`) | Add the block to `~/.claude/settings.json`; restart Claude Code |
| Symlink at `~/.claude/plugins/marketplaces/<name>/` resolves but plugins still not found | Symlink isn't strictly required for directory sources, but doesn't hurt; check the marketplace.json reachable through symlink | Verify `ls -la ~/.claude/plugins/marketplaces/<name>/.claude-plugin/marketplace.json` resolves |
| Errors persist after fixing files | Stale `plugin-catalog-cache.json` may be confusing the loader | `rm ~/.claude-work/plugins/plugin-catalog-cache.json && /reload-plugins` |

## Known issue: skill-hub-agent anomaly (2026-05-19)

During a debugging session, all 6 other skill-hub plugins (`-data`, `-quality`, `-patterns`, `-meta`, `-lifecycle`, `-tools`) errored on `/doctor` with "Plugin not found in marketplace skill-hub-local", but **skill-hub-agent did not error**.

All 7 plugins have identical structural validity at the time of writing:

- ✅ Valid plugin.json with name/description/version
- ✅ All SKILL.md files have proper YAML frontmatter
- ✅ Listed in marketplace.json with valid source paths

`skill-hub-agent` is the **7th and last** entry in `marketplace.json.plugins[]`. Hypothesis: the loader may short-circuit error reporting after a threshold, masking failures for later entries. Alternative hypothesis: `skill-hub-agent` is in a special enablement state (enabled in both `~/.claude/settings.json` and `~/.claude-work/settings.json`, never successfully installed) that produces a different code path.

Action item for future debugging: temporarily reorder `marketplace.json` so a different plugin is 7th and check if it survives the error list. If yes → enumeration order bug. If no → genuine state difference for skill-hub-agent.

## File locations cheat sheet

| Purpose | Path |
|---|---|
| Marketplace manifest | `~/dev/skill-hub/.claude-plugin/marketplace.json` |
| Plugin manifest | `~/dev/skill-hub/plugins/<plugin>/.claude-plugin/plugin.json` |
| Skill content | `~/dev/skill-hub/plugins/<plugin>/skills/<skill>/SKILL.md` |
| Marketplace declaration (active) | `~/.claude/settings.json` → `extraKnownMarketplaces` |
| Marketplace declaration (legacy) | `~/.claude-work/settings.json` → `extraKnownMarketplaces` |
| Marketplace symlink (optional but recommended) | `~/.claude/plugins/marketplaces/skill-hub-local` → `~/dev/skill-hub` |
| Per-project enablement | `<project>/.claude/settings.json` → `enabledPlugins` |
| Catalog cache (purge to invalidate) | `~/.claude-work/plugins/plugin-catalog-cache.json` |

## Confirmed Claude Code limitation (2026-05-19, session 2)

After validating every layer above (frontmatter, plugin.json, marketplace.json schema, symlink, settings registration, cache invalidation), `/reload-plugins` still produced the same 11 errors:

- 6 from skill-hub-local (all except skill-hub-agent — see anomaly section)
- 5 from financial-services-plugins (GitHub-source, supposedly fully supported)

Steps already attempted that did NOT clear the errors:

1. Converted marketplace.json plugin sources from string form to object form
2. Reverted that change (proved format isn't the issue)
3. Fixed `~/.claude/plugins/known_marketplaces.json` source type from `"local"` to `"directory"`
4. Added `extraKnownMarketplaces` block to `~/.claude/settings.json`
5. Created symlink at `~/.claude/plugins/marketplaces/skill-hub-local` → `~/dev/skill-hub`
6. Deleted `plugin-catalog-cache.json` and reloaded

Conclusion: **This Claude Code version's plugin loader requires plugins to exist in the centralized Anthropic-hosted plugin catalog (`plugin-catalog-cache.json`), which only contains `@claude-plugins-official` entries.** Local multi-plugin marketplaces register successfully but produce 0 loaded skills.

**Workaround**: For skills you actually need (e.g., `fullstack-guardian`, `code-review-suite`), copy the SKILL.md directory directly into `~/.claude/skills/`:

```bash
cp -r ~/dev/skill-hub/plugins/skill-hub-meta/skills/fullstack-guardian ~/.claude/skills/
```

Skills loaded from `~/.claude/skills/` bypass the plugin/catalog system entirely. This is how the 50+ skills currently working (architect, archon, do, marshal, etc.) are loaded.

**Working plugins in this Claude Code version**:
- Plugins under `@claude-plugins-official` (the curated Anthropic catalog)
- Single-plugin local marketplaces (like Citadel — no `plugins` array in marketplace.json)

**Not working**:
- Multi-plugin local marketplaces (this repo's design)
- Multi-plugin GitHub marketplaces that aren't in the official catalog (e.g., `anthropics/financial-services-plugins` works structurally but plugins don't surface)

Until this is resolved upstream, the practical path is the skill-sync approach: copy SKILL.md trees into `~/.claude/skills/`.
