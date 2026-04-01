---
last_updated: 2026-03-27
---
## Skills

### orchestrate
keywords: [feature goal, build, start work, implement feature, create feature, dependency, task cycle, kick off, begin work on]

### measure
keywords: [cycle complete, metrics, velocity, qa pass, review iterations, task done, finished feature, completed sprint]

### report
keywords: [report, dashboard, weekly summary, status update, management report, show progress, what got done, delivery summary]

### decide
keywords: [decision, prioritise, prioritize, which option, trade-off, should we, a or b, what should we focus, rank options, recommend]

### learn
keywords: [learned, pattern, mistake, feedback, wrong, worked well, did not work, retrospective, what went wrong, improvement]

### evolve-self
keywords: [evolve, improve plugin, generate skill, self-improve, /evolve, plugin update, new skill, skill gap, auto-improve]

### prodmasterai
keywords: [/prodmasterai, prodmaster, entry point, main command, what should i do, what next, status check, show me where we are]

### smooth-dev
keywords: [pull latest, take a pull, sync code, get latest, start dev, smooth dev, pre-flight, health check, ensure up to date, clean state, ready to code, start development session, begin session]

### help
keywords: [help, what can you do, show commands, how does this work, what skills, confused, lost, guide me, tutorial, getting started]

### dev-loop
keywords: [dev loop, loop until passing, iterate until tests pass, loop mode, improvement loop, polish loop, watch mode, keep improving, run until done]

### research-resolve
keywords: [stuck, research and resolve, autonomous fix, worktree fix, can't make progress, loop stuck, investigate failure, research the problem]

### auto-pilot
keywords: [auto, autonomously, run autonomously, unattended, while I sleep, work while I sleep, autonomous pipeline, no questions, full pipeline auto]

### resume
keywords: [resume, what happened while I was away, autonomous summary, show autonomous summary, decision audit, rollback, auto-pilot review]

### checkpoint
keywords: [checkpoint, resume session, pick up where I left off, continue after limit, save progress, interrupted task, plan limit reset, auto-resume, checkpoint discard, checkpoint reset]

### token-efficiency
keywords: [token efficiency, reduce tokens, token audit, I'm hitting limits, too many tokens, optimize tokens, token waste, token usage, plan limit, efficiency audit]

### auto-pilot-revoke
- trigger: /auto-pilot-revoke
- trigger: stop auto-pilot
- trigger: cancel autonomous
- reads: memory/project-context.md, memory/autonomous-log.md
- writes: memory/project-context.md, memory/autonomous-log.md

### task-queue
- trigger: /prodmasterai queue add
- trigger: /prodmasterai queue list
- trigger: /prodmasterai queue run
- reads: memory/task-queue.md, memory/project-context.md
- writes: memory/task-queue.md

### parallel-explore
- trigger: /prodmasterai explore
- trigger: try multiple approaches
- trigger: parallel worktrees
- reads: memory/project-context.md, memory/patterns.md, memory/parallel-explore-log.md
- writes: memory/parallel-explore-log.md, memory/patterns.md

### qa
keywords: [qa, quality check, QA pass, test the app, run qa, systematic qa, health check, health score, fix bugs, regression tests, qa pipeline]

### review
keywords: [code review, review PR, review diff, review changes, pre-merge review, review before ship, two-pass review, critical review]

### deploy
keywords: [deploy, ship it, push to production, release, land and deploy, deployment pipeline, canary, rollback]

### cso
keywords: [security audit, vulnerabilities, threat model, OWASP, pentest, CSO, secrets, supply chain, LLM security, STRIDE]

### plugin-manager
- trigger: /prodmasterai plugins
- trigger: install plugin
- trigger: what plugins are installed
- reads: memory/connectors/official-plugins-registry.md
- writes: (none)

### qa-only
keywords: [qa report, test report only, findings only, what's broken, audit without fixing, qa without fix, what needs fixing, health score report, qa-only, don't fix, just show issues, read-only QA, baseline regression]

### ship
keywords: [ship, ready to merge, pre-merge, create PR, prepare for merge, ready to ship, completeness, coverage audit, changelog, pre-merge pipeline, ship it, completeness check]

### benchmark
keywords: [benchmark, performance check, perf regression, measure performance, Core Web Vitals, bundle size, how fast is this, LCP, FCP, TTFB, regression, speed, latency, CLS]

### codex
keywords: [codex, second opinion, cross-model review, adversarial review, challenge this, ask codex, blind spots, dual model, get a second opinion, PASS/FAIL gate, independent review]

### document-release
keywords: [sync docs, update docs, post-ship docs, document this release, docs sync, update readme, CHANGELOG polish, documentation sync, release notes, stale docs]

### skill-forge
keywords: [learn how to use, add skill for, teach me about, create skill for, generate skill for, add capability for, build skill from, /prodmasterai learn, skill-forge, learn topic, research topic, new skill]
