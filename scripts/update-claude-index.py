#!/usr/bin/env python3
"""Regenerate ~/dev/CLAUDE-INDEX.md from filesystem state.

Why: single pane of glass over the entire Claude Code config — plugins, skills,
commands, hooks, per-project overrides — categorized by work vs personal.
Deps: PyYAML (for stack-context.yaml).
"""

import json
import re
from datetime import datetime
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None

HOME = Path.home()
CLAUDE = HOME / '.claude'
SH = HOME / 'dev/skill-hub'
INDEX = HOME / 'dev/CLAUDE-INDEX.md'


# ---------------------------------------------------------------------------
# Work / personal classification rules
# ---------------------------------------------------------------------------

WORK_PATTERNS = [
    re.compile(r'^dqi[-_]'),
    re.compile(r'^hudl[-_]'),
    re.compile(r'^equity[-_]'),
    re.compile(r'^finance[-_]'),
    re.compile(r'^trial[-_]'),
]
PERSONAL_PATTERNS = [
    re.compile(r'^project[-_]pegasus'),
    re.compile(r'^project[-_]ahre'),
    re.compile(r'^personal[-_]'),
    re.compile(r'^pokergpt'),
    re.compile(r'^dokkan'),
    re.compile(r'^finance[-_]app$'),  # exception — this one IS work
]


def classify(project_name: str) -> str:
    if project_name == 'finance-app':
        return 'work'
    for p in WORK_PATTERNS:
        if p.match(project_name):
            return 'work'
    for p in PERSONAL_PATTERNS:
        if p.match(project_name):
            return 'personal'
    return 'other'


# ---------------------------------------------------------------------------
# Data gathering
# ---------------------------------------------------------------------------

def read_json(p: Path):
    try:
        return json.loads(p.read_text())
    except Exception:
        return None


def get_global_settings():
    return read_json(CLAUDE / 'settings.json') or {}


def get_known_marketplaces():
    return read_json(CLAUDE / 'plugins/known_marketplaces.json') or {}


def get_skill_hub_plugins():
    """Return {plugin_name: [skill_names]} for the skill-hub marketplace."""
    plugins = {}
    plugins_dir = SH / 'plugins'
    if not plugins_dir.exists():
        return plugins
    for p in sorted(plugins_dir.iterdir()):
        if not p.is_dir():
            continue
        skills_dir = p / 'skills'
        skills = sorted([s.name for s in skills_dir.iterdir() if s.is_dir()]) if skills_dir.exists() else []
        plugins[p.name] = skills
    return plugins


def get_per_project_settings():
    """Walk ~/dev/ for projects with .claude/settings.json that enable plugins."""
    projects = {}
    dev = HOME / 'dev'
    if not dev.exists():
        return projects
    for p in sorted(dev.iterdir()):
        if not p.is_dir():
            continue
        settings_path = p / '.claude/settings.json'
        if not settings_path.exists():
            continue
        s = read_json(settings_path) or {}
        ep = s.get('enabledPlugins', {})
        if ep:
            enabled = [k for k, v in ep.items() if v]
            if enabled:
                projects[p.name] = enabled
    return projects


def get_skills_inventory():
    skills_dir = CLAUDE / 'skills'
    if not skills_dir.exists():
        return []
    return sorted([d.name for d in skills_dir.iterdir() if d.is_dir() or d.is_symlink()])


def get_commands_inventory():
    cmds_dir = CLAUDE / 'commands'
    if not cmds_dir.exists():
        return []
    return sorted([f.stem for f in cmds_dir.glob('*.md')])


def get_hooks(settings: dict):
    return settings.get('hooks', {})


# ---------------------------------------------------------------------------
# Markdown rendering
# ---------------------------------------------------------------------------

def render():
    settings = get_global_settings()
    marketplaces = get_known_marketplaces()
    sh_plugins = get_skill_hub_plugins()
    proj_settings = get_per_project_settings()
    skills = get_skills_inventory()
    commands = get_commands_inventory()
    hooks = get_hooks(settings)

    enabled_plugins = settings.get('enabledPlugins', {})
    global_on = sorted([k for k, v in enabled_plugins.items() if v])

    # Categorize projects
    work_projects = {}
    personal_projects = {}
    other_projects = {}
    for name, plugins in proj_settings.items():
        bucket = classify(name)
        if bucket == 'work':
            work_projects[name] = plugins
        elif bucket == 'personal':
            personal_projects[name] = plugins
        else:
            other_projects[name] = plugins

    out = []
    out.append(f'# Claude Code Config Index')
    out.append('')
    out.append(f'_Last regenerated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}_  ')
    out.append(f'_Regenerate with: `python3 ~/dev/skill-hub/scripts/update-claude-index.py`_')
    out.append('')
    out.append('Single pane of glass for the entire Claude Code config. Auto-generated from filesystem state.')
    out.append('')
    out.append('---')
    out.append('')

    # Section 1: TL;DR
    out.append('## TL;DR — what loads where')
    out.append('')
    out.append(f'- **Global plugins** (always on): {len(global_on)}')
    out.append(f'- **Skill-hub sub-plugins**: {len(sh_plugins)} ({sum(len(v) for v in sh_plugins.values())} skills total)')
    out.append(f'- **Work projects** with custom overrides: {len(work_projects)}')
    out.append(f'- **Personal projects** with custom overrides: {len(personal_projects)}')
    out.append(f'- **Skills installed in `~/.claude/skills/`**: {len(skills)}')
    out.append(f'- **Commands in `~/.claude/commands/`**: {len(commands)}')
    out.append(f'- **Skill description budget**: {settings.get("skillListingBudgetFraction", "default (1%)")}')
    out.append('')
    out.append('---')
    out.append('')

    # Section 2: Plugins overview
    out.append('## Plugins')
    out.append('')
    out.append('### Marketplaces registered')
    out.append('')
    out.append('| Marketplace | Source |')
    out.append('|---|---|')
    for name, info in marketplaces.items():
        source = info.get('source', {})
        if source.get('source') == 'github':
            src_str = f'github: {source.get("repo")}'
        elif source.get('source') == 'local':
            src_str = f'local: `{source.get("path")}`'
        else:
            src_str = json.dumps(source)
        out.append(f'| `{name}` | {src_str} |')
    out.append('')

    out.append('### Global (always-on) plugins')
    out.append('')
    out.append('Set in `~/.claude/settings.json` → `enabledPlugins`. Loaded in every session.')
    out.append('')
    if global_on:
        out.append('| Plugin@Marketplace | Source |')
        out.append('|---|---|')
        for p in global_on:
            if '@' in p:
                plugin_name, mkt = p.rsplit('@', 1)
            else:
                plugin_name, mkt = p, 'unknown'
            out.append(f'| `{plugin_name}` | {mkt} |')
    else:
        out.append('_(none)_')
    out.append('')

    out.append('### Skill-hub sub-plugins')
    out.append('')
    out.append('All under `~/dev/skill-hub/plugins/`. Marketplace = `skill-hub-local`.')
    out.append('')
    for plugin, sks in sh_plugins.items():
        global_marker = '🌐 global' if f'{plugin}@skill-hub-local' in global_on else '📦 per-project'
        out.append(f'#### `{plugin}` ({len(sks)} skills, {global_marker})')
        out.append('')
        for s in sks:
            out.append(f'- `{s}`')
        out.append('')

    out.append('---')
    out.append('')

    # Section 3: Per-project overrides — WORK
    out.append('## Per-project plugin overrides')
    out.append('')
    out.append('Each project\'s `.claude/settings.json` can add `enabledPlugins` on top of the global set.')
    out.append('')
    out.append('### Work projects')
    out.append('')
    if work_projects:
        out.append('| Project | Plugins added |')
        out.append('|---|---|')
        for name, plugins in sorted(work_projects.items()):
            short = ', '.join(p.replace('@skill-hub-local', '').replace('@claude-plugins-official', ' (official)') for p in plugins)
            out.append(f'| `{name}` | {short} |')
    else:
        out.append('_(none yet — add overrides in each project\'s `.claude/settings.json`)_')
    out.append('')

    out.append('### Personal projects')
    out.append('')
    if personal_projects:
        out.append('| Project | Plugins added |')
        out.append('|---|---|')
        for name, plugins in sorted(personal_projects.items()):
            short = ', '.join(p.replace('@skill-hub-local', '').replace('@claude-plugins-official', ' (official)') for p in plugins)
            out.append(f'| `{name}` | {short} |')
    else:
        out.append('_(none — personal projects use only global plugins)_')
    out.append('')

    if other_projects:
        out.append('### Other (uncategorized) projects')
        out.append('')
        out.append('| Project | Plugins added |')
        out.append('|---|---|')
        for name, plugins in sorted(other_projects.items()):
            short = ', '.join(p.replace('@skill-hub-local', '').replace('@claude-plugins-official', ' (official)') for p in plugins)
            out.append(f'| `{name}` | {short} |')
        out.append('')

    out.append('---')
    out.append('')

    # Section 4: Hooks
    out.append('## Hooks (`~/.claude/settings.json`)')
    out.append('')
    if hooks:
        out.append('| Event | Matcher | Script |')
        out.append('|---|---|---|')
        for event, configs in hooks.items():
            for c in configs:
                m = c.get('matcher', '*')
                for h in c.get('hooks', []):
                    cmd = h.get('command', '')
                    out.append(f'| `{event}` | `{m}` | `{cmd}` |')
    else:
        out.append('_(none configured)_')
    out.append('')
    out.append('---')
    out.append('')

    # Section 5: Inventory
    out.append('## Inventory (`~/.claude/`)')
    out.append('')
    out.append(f'- `skills/` — {len(skills)} entries (mostly Citadel plugin\'s skills + repowise + tools)')
    out.append(f'- `commands/` — {len(commands)} slash commands')
    out.append('')

    out.append('---')
    out.append('')

    # Section 5b: Registry drift warning
    out.append('## Where skill information lives (and why counts drift)')
    out.append('')
    out.append('Five separate sources track skill state. They drift independently — **never trust a hardcoded skill count in any CLAUDE.md or doc**:')
    out.append('')
    out.append('| Source | What it tracks | When it updates | Authoritative? |')
    out.append('|---|---|---|---|')
    out.append('| `~/.claude-work/plugins/installed_plugins.json` | Claude Code\'s actual plugin install state | `/plugin install` / `/plugin update` | ✅ YES — what actually loads |')
    out.append('| `~/.claude-work/plugins/known_marketplaces.json` | Registered plugin marketplaces | `/plugin marketplace add` | ✅ YES |')
    out.append('| `~/.claude-work/settings.json` | `enabledPlugins`, `extraKnownMarketplaces` | Claude Code on settings change | ✅ YES (effective config) |')
    out.append('| `~/.claude/harness.json` | Citadel\'s skill registry (used by `/do` routing) | `/setup` run, manual edits | Snapshot, can drift |')
    out.append('| `<project>/.claude/harness.json` | Per-project Citadel config | `/setup` per-project | Snapshot, can drift |')
    out.append('')
    out.append('**Plus**: `<project>/.claude/skills/*/SKILL.md` files are project-local skills, auto-discovered, **not tracked in any registry above**.')
    out.append('')
    out.append('### How to check what\'s actually loaded')
    out.append('')
    out.append('1. Start a fresh Claude Code session → the system prompt lists available skills with their descriptions')
    out.append('2. Type `/` and check autocomplete for slash-invocable skills')
    out.append('3. Run `python3 ~/dev/skill-hub/scripts/update-claude-index.py` → this index reflects current filesystem state (most reliable)')
    out.append('')
    out.append('---')
    out.append('')

    # Section 6: How-to
    out.append('## How to maintain this setup')
    out.append('')
    out.append('### Add a new skill')
    out.append('1. Decide category: data, quality, patterns, meta, tools, lifecycle')
    out.append('2. Create `~/dev/skill-hub/plugins/skill-hub-<category>/skills/<skill-name>/SKILL.md` with proper YAML frontmatter')
    out.append('3. Restart Claude Code; verify with `/<skill-name>` autocomplete')
    out.append('')
    out.append('### Remove a skill')
    out.append('1. Delete `~/dev/skill-hub/plugins/skill-hub-<category>/skills/<skill-name>/`')
    out.append('2. Restart Claude Code')
    out.append('')
    out.append('### Enable a per-project plugin')
    out.append('In the project\'s `.claude/settings.json`:')
    out.append('```json')
    out.append('{')
    out.append('  "enabledPlugins": {')
    out.append('    "skill-hub-data@skill-hub-local": true')
    out.append('  }')
    out.append('}')
    out.append('```')
    out.append('')
    out.append('### Increase skill description budget')
    out.append('In `~/.claude/settings.json`:')
    out.append('```json')
    out.append('{')
    out.append('  "skillListingBudgetFraction": 0.07')
    out.append('}')
    out.append('```')
    out.append('Default is 0.01 (1%). Currently set to ' + str(settings.get('skillListingBudgetFraction', 'default')) + '.')
    out.append('')
    out.append('### Regenerate this index')
    out.append('```bash')
    out.append('python3 ~/dev/skill-hub/scripts/update-claude-index.py')
    out.append('```')
    out.append('')
    out.append('---')
    out.append('')

    # Section 7: Key file paths
    out.append('## Key file paths')
    out.append('')
    out.append('| What | Where |')
    out.append('|---|---|')
    out.append('| Global settings | `~/.claude/settings.json` |')
    out.append('| Local-only settings | `~/.claude/settings.local.json` |')
    out.append('| Citadel harness registry | `~/.claude/harness.json` |')
    out.append('| Known marketplaces | `~/.claude/plugins/known_marketplaces.json` |')
    out.append('| Skill-hub plugin root | `~/dev/skill-hub/` |')
    out.append('| Skill-hub manifest | `~/dev/skill-hub/manifest.yaml` |')
    out.append('| Skill-hub stack context | `~/dev/skill-hub/stack-context.yaml` |')
    out.append('| Stub generator | `~/dev/skill-hub/scripts/generate-stubs.py` |')
    out.append('| Citadel plugin | `~/dev/Citadel/Citadel/` |')
    out.append('| ECC (disabled, kept for reference) | `~/everything-claude-code/` |')
    out.append('| ECC staged for consolidation | `~/dev/skill-hub/skill-lifecycle/staging/everything-claude-code/` |')
    out.append('| Audit doc (your decision log) | `~/dev/CLAUDE-CONFIG-AUDIT.md` |')
    out.append('| Drop list (cleanup log) | `~/dev/CLAUDE-DROP-LIST.md` |')
    out.append('| This index | `~/dev/CLAUDE-INDEX.md` |')

    return '\n'.join(out) + '\n'


if __name__ == '__main__':
    content = render()
    INDEX.write_text(content)
    print(f'Wrote {INDEX} ({len(content)} chars, {len(content.splitlines())} lines)')
