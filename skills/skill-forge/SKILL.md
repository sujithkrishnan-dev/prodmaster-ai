---
name: skill-forge
description: Autonomous topic research and SKILL.md generation — /prodmasterai learn <topic> triggers four-stage workflow (research → review → generate → store). Multi-source verification. Generates complete SKILL.md with proper frontmatter, triggers, process steps. Stores in skills/<name>/SKILL.md. Updates skill-pattern-manifest. Quick reference tables in output.
version: 1.0.0
triggers:
  - /prodmasterai learn
  - learn how to use
  - add skill for
  - teach me about
  - create skill for
  - generate skill for
  - add capability for
  - build skill from
reads:
  - memory/project-context.md
  - memory/research-findings.md
  - memory/skill-gaps.md
writes:
  - memory/research-findings.md
  - memory/skill-gaps.md
  - memory/connectors/skill-pattern-manifest.md
generated: false
generated_from: ""
---

# Skill Forge

Research any tool, workflow, or framework and generate a production-ready SKILL.md automatically.

Trigger with a topic argument: `/prodmasterai learn <topic>`

---

## Examples

```
/prodmasterai learn playwright
/prodmasterai learn terraform apply workflow
/prodmasterai learn conventional commits
/prodmasterai learn database migrations
/prodmasterai learn github actions
/prodmasterai learn stripe webhooks
```

---

## Phase 1 — Research

For the given topic, gather information in parallel from multiple sources:

### Source 1: Official documentation / web search
- Core concepts, getting started, best practices, commands/API
- Common error patterns and their fixes
- What experts do differently than beginners

### Source 2: This codebase's existing context
- Search `memory/research-findings.md` for prior research on this topic
- Search `memory/patterns.md` for related patterns already captured
- Check `skills/` for adjacent skills that could inform structure

### Source 3: Synthesized workflow patterns
- What is the canonical sequence of steps end-to-end?
- What are the most common failure modes at each step?
- What does recovery look like when it goes wrong?

### Research output:

Produce a structured summary and append to `memory/research-findings.md`:

```markdown
## Research: <topic> — <date>

### What it does
<1-2 sentence explanation>

### Key concepts
- <concept>: <brief definition>

### Standard workflow
1. <step> — <why this order>
2. <step>

### Common pitfalls
- <pitfall>: <how to avoid>

### Best practices
- <practice>

### Sources
- <source type>: <what it contributed>
```

---

## Phase 2 — Review

Before generating, validate research quality:

**Completeness check:**
- Workflow described end-to-end (start → finish, not just a middle step)?
- Concrete commands/examples, not just concepts?
- Failure handling and recovery steps included?
- Output format clear?

**Conflict check:**
- Does this topic overlap with an existing skill?
- If yes: is this a replacement, extension, or complement?
- If replacement: ask before overwriting

**Scope check:**
- Right scope for one skill? (Not too broad, not too narrow)
- If too broad: split into multiple skills and note which ones
- If too narrow: suggest merging with adjacent skill

If any completeness check fails: loop back to Phase 1. Maximum 2 research iterations — then generate with known gaps noted.

---

## Phase 3 — Generate

Build a complete SKILL.md following ProdMaster AI conventions exactly:

### Frontmatter:
```yaml
---
name: <kebab-case topic name>
description: <one sentence: what it does, when to use it, key differentiators>
version: 1.0.0
triggers:
  - /prodmasterai <name>
  - <natural language trigger 1>
  - <natural language trigger 2>
  - <3-5 total triggers>
reads:
  - memory/project-context.md
writes:
  - memory/<name>-log.md
generated: true
generated_from: "<original topic as provided>"
---
```

### Body structure (all required):

1. **Title + one-liner** — what it does, when to use it
2. **Phases** — numbered, named, actionable
   - Each phase: clear input, specific actions, expected output
   - Every action is concrete (command, file path, exact check)
   - Every phase has failure handling ("if X fails: do Y")
3. **Output format** — literal template showing exactly what the skill prints
4. **Log entry** — YAML block to append to `memory/<name>-log.md`
5. **Auto-pilot integration** — behavior when `autonomous_mode: true`
6. **Rules** — 5-8 hard constraints that cannot be skipped
7. **Quick reference table** — most common commands/options (if applicable)

### Quality bar:
- A developer who has never used this tool could follow it and succeed
- No vague instructions ("configure appropriately", "set up as needed")
- Self-contained — no "see documentation" without a fallback
- Failure modes are explicit at every phase

### Self-check before saving:

| Check | Pass condition |
|---|---|
| Frontmatter complete | All required fields, no empty values |
| Triggers specific | Each trigger 2-5 words, no conflicts with existing skills |
| Phases concrete | Every phase has numbered specific actions |
| Output format present | Shows exactly what the skill prints |
| Log entry present | YAML append block included |
| Auto-pilot section | Behavior in autonomous mode documented |
| Rules section | At least 5 hard constraints |
| No vague language | Zero instances of "configure as needed", "see docs" |

Rewrite any section that fails before saving.

---

## Phase 4 — Store

1. Determine skill name: kebab-case of topic (e.g. "playwright" → `playwright`, "github actions" → `github-actions`)
2. Check if `skills/<name>/SKILL.md` already exists
   - Exists: show diff summary, ask for confirmation before overwriting
   - New: proceed
3. Write to `skills/<name>/SKILL.md`
4. Update `memory/connectors/skill-pattern-manifest.md` — add new triggers:
   ```
   <trigger keyword> → <skill name>
   <trigger keyword 2> → <skill name>
   ```
5. If topic was listed in `memory/skill-gaps.md`: update status to `resolved`

---

## Multi-Skill Generation

If research reveals the topic is too broad for one skill, split automatically:

```
Topic 'github actions' is broad — splitting into 3 skills:
  1. github-actions-setup    → pipeline initialization
  2. github-actions-deploy   → deployment workflows
  3. github-actions-test     → automated test runs

Generating all 3 in parallel...
```

Generate in parallel. Register all triggers in manifest.

---

## Output Format

```
== Skill Forge: <topic> ==
Research sources:    <N>
Review iterations:   <N>
Skill generated:     skills/<name>/SKILL.md
Triggers registered: <N>

Quick reference:
  /prodmasterai <name>   <description>
  <trigger 2>            same skill
  <trigger 3>            same skill

Ready. Try: /prodmasterai <name>
```

---

## Rules

- Research minimum 2 sources — never generate from one source alone
- Every generated skill must pass the self-check before being saved
- Triggers must not conflict with existing registered skills
- Never overwrite an existing skill without explicit confirmation
- Generated skills are permanently marked `generated: true`
- The skill must be immediately usable — no unresolved setup prerequisites
- Skill name must be kebab-case, lowercase, no special characters
- **Never contribute anything upstream** — upstream is exclusively evolve-self's responsibility
