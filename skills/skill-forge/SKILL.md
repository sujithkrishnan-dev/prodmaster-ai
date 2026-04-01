---
name: skill-forge
description: Research any topic and generate a production-ready SKILL.md. Explores best practices, existing patterns, and project context to produce a skill that integrates with the plugin's architecture.
version: 1.0.0
triggers:
  - User runs /prodmasterai learn <topic>
  - User says "create a skill for", "generate skill", "build a skill", "I need a skill that"
reads:
  - memory/project-context.md
  - memory/connectors/skill-pattern-manifest.md
writes:
  - memory/connectors/skill-pattern-manifest.md
generated: false
generated_from: ""
---

# Skill Forge — Research and Generate Skills

Research a topic and generate a production-ready SKILL.md that integrates with the ProdMaster AI plugin architecture.

## Process

### 1. Understand the Topic

Parse the user's request to extract:
- **Domain:** What area does this skill cover?
- **Trigger:** When should this skill fire?
- **Output:** What does the user expect when it runs?

### 2. Research Phase

Dispatch a research subagent to explore:
1. **Existing skills:** Read `skills/*/SKILL.md` to understand the pattern and quality bar
2. **Project context:** Read `memory/project-context.md` for active features and conventions
3. **Best practices:** Search for established approaches in the domain
4. **Tool availability:** Check what tools/CLIs are available for the topic

### 3. Design the Skill

Based on research, design:
- **Process steps:** Clear, actionable steps (not vague guidance)
- **Reads/writes:** Which memory files it needs
- **Integration points:** How it connects to orchestrate, measure, learn
- **Edge cases:** What happens when data is missing, tools unavailable, etc.

### 4. Generate SKILL.md

Create `skills/<name>/SKILL.md` with full frontmatter:

```markdown
---
name: <name>
description: <one-line description>
version: 1.0.0
triggers:
  - <trigger 1>
  - <trigger 2>
reads:
  - <file 1>
writes:
  - <file 1>
generated: true
generated_from: "skill-forge"
---

# <Title>

<What this skill does>

## Process

<Detailed, actionable steps>

## Rules

<5-7 specific rules>
```

### 5. Update Manifest

Append to `memory/connectors/skill-pattern-manifest.md`:
```markdown
### <skill-name>
keywords: [<5-10 keywords>]
```

### 6. Validate

- Check all frontmatter fields present
- Check reads/writes declarations match body references
- Check no conflicting rules
- Run test suite to verify skill appears in ALL_SKILLS (if test exists)

### Completion Message

```
Skill forged: <name>
Location: skills/<name>/SKILL.md
Version: 1.0.0
Triggers: <list>

Add to test_skills.py ALL_SKILLS and run tests to verify.
```

## Rules

- Generated skills must follow the exact same frontmatter schema as existing skills
- Process steps must be specific and actionable — no vague "consider doing X"
- Always include at least 5 rules
- Always update the skill-pattern-manifest
- Mark `generated: true` and `generated_from: "skill-forge"` in frontmatter
- Never overwrite an existing skill — check for name collision first
