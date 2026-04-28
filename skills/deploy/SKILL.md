---
name: deploy
description: Deployment pipeline — auto-detects platform (Fly/Vercel/Render/Railway/custom), runs dry-run validation first, checks pre-merge readiness gates, waits for CI, verifies the live deployment with canary checks, and provides a revert escape hatch if production breaks.
version: 1.1.1
argument-hint: "[--dry-run] [--env staging|prod]"
disable-model-invocation: true
effort: medium
triggers:
  - /prodmasterai deploy
  - deploy this
  - ship it
  - push to production
  - deploy to prod
  - land and deploy
  - release this
reads:
  - memory/project-context.md
writes:
  - memory/deploy-log.md
  - memory/project-context.md
generated: false
generated_from: ""
---

# Deploy

End-to-end deployment pipeline. Validates before touching production, waits for CI, verifies the live result, and reverts automatically if health checks fail. Never deploys without a passing gate sequence.

---

## Phase 1 — Platform Detection

Detect the deployment target automatically:

| Signal | Platform |
|---|---|
| `fly.toml` present | Fly.io |
| `vercel.json` or `.vercel/` present | Vercel |
| `render.yaml` present | Render |
| `railway.json` or `railway.toml` | Railway |
| `.github/workflows/` with deploy job | GitHub Actions |
| `Dockerfile` + no above | Generic Docker |
| None of the above | Unknown — ask user |

Record `platform` and `deploy_command` before proceeding.

For **docs-only changes** (all changed files match `*.md`, `docs/**`, `*.txt`): skip Phases 3–7, jump directly to Phase 2 → Phase 8 (report only). No deployment needed.

---

## Phase 2 — Pre-Merge Readiness Gates

Check all gates in parallel. Block if any gate fails:

| Gate | Check | Block condition |
|---|---|---|
| Tests | Run test suite | Any test failure |
| Lint | Run linter | Errors (not warnings) |
| Review verdict | Read `memory/review-log.md` last entry | `verdict: REWORK REQUIRED` |
| Stale reviews | Check PR for requested-changes reviews | Any unresolved requested changes |
| CHANGELOG | Check if CHANGELOG.md updated since last release | Missing entry for this feature |
| Branch | Confirm current branch is NOT main/master | Deploying directly from main is blocked |

On gate failure: output which gates failed and why. Stop. Do not proceed to deploy.

---

## Phase 3 — Dry Run

Run the deployment in dry-run mode to show exactly what will happen:

```bash
# Fly
fly deploy --dry-run

# Vercel
vercel --dry-run

# Render / Railway / custom
# Check for --dry-run flag; if absent, describe what deploy would do from config
```

Output the dry-run summary to the user. Confirm it matches the expected scope (correct app, correct region, correct build).

On dry-run failure: stop, output error. Do not proceed.

---

## Phase 4 — Merge Queue Awareness

Check if the target repository uses a merge queue:

- GitHub merge queue: check if branch protection requires merge queue (`gh api repos/:owner/:repo/branches/main`)
- If merge queue active: enqueue the PR and wait — do not force-merge outside the queue
- If no merge queue: proceed to deploy directly

If waiting in merge queue: poll every 60 seconds. Report status. Continue when position = 0 (merged or ready).

---

## Phase 5 — Deploy

Execute the deployment:

1. Record `pre_deploy_sha: git rev-parse HEAD` as the revert anchor.
2. Run the deploy command.
3. Stream output. On non-zero exit: stop, log error, output failure card with pre_deploy_sha for manual revert reference.
4. On success: extract the deployment URL or version identifier from output.

---

## Phase 6 — CI Wait

After deploy command succeeds, wait for CI checks to complete:

- Poll CI status every 30 seconds (GitHub Actions: `gh run list --branch <branch>`, or platform-specific CLI).
- Timeout: 10 minutes. On timeout: output warning, continue to canary with caveat.
- On CI failure: trigger revert (Phase 7). Output: "CI failed post-deploy — reverting."

---

## Phase 7 — Canary Verification

Verify the live deployment is healthy. Skip this phase for docs-only or non-web deployments.

Run all checks in parallel:

| Check | Method | Pass condition |
|---|---|---|
| HTTP reachability | Fetch root URL | 2xx response |
| Load time | Measure time-to-first-byte | < 3 seconds |
| Console errors | Check for JS errors (if browser automation available) | Zero critical errors |
| Health endpoint | GET `/health` or `/api/health` if present | 200 + `status: ok` |
| Key user flow | Fetch primary authenticated route | 2xx, no redirect loop |

On any check failure:
- Severity critical (reachability, health endpoint): trigger automatic revert immediately.
- Severity high (load time >5s, console errors): flag and ask user before reverting.
- Severity low (load time 3–5s): log warning, do not revert.

---

## Phase 7b — Automatic Revert

Triggered when a critical canary check fails.

1. Output: "Canary failed — reverting to pre_deploy_sha."
2. Run platform-specific rollback:
   - Fly: `fly deploy --image <previous_image>` or `fly releases rollback`
   - Vercel: `vercel rollback`
   - Generic: `git revert HEAD && git push` (creates a revert commit, never force-push)
3. Verify revert deployed successfully by re-running Phase 7 checks.
4. Log revert in `memory/deploy-log.md` with reason.
5. Append blocker to `memory/project-context.md ## Blockers`.
6. Output failure card with revert confirmation.

---

## Phase 8 — Report

```
== Deploy Report: <feature or branch> ==
Platform:   <platform>
Strategy:   <full | docs-skip>

Pre-merge gates:  <all pass | N failed>
Dry run:          <pass | failed>
Deploy:           <success | failed>
CI:               <pass | timeout | failed>
Canary:           <pass | N warnings | failed + reverted>

Deployment URL:   <url or n/a>
Pre-deploy SHA:   <sha>  (revert anchor)

Verdict: <LIVE | REVERTED | BLOCKED>

Next:
  <"Feature is live at <url>" | "Deployment reverted — fix canary failures before retrying" | "Gates blocked — resolve N issues before deploying">
```

Append to `memory/deploy-log.md`:

```yaml
---
date: <YYYY-MM-DD>
feature: <active_feature>
platform: <platform>
verdict: LIVE | REVERTED | BLOCKED
deployment_url: <url or n/a>
pre_deploy_sha: <sha>
canary_failures: N
reverted: true | false
session_id: <session_id>
---
```

---

## Integration with Auto-Pilot

When `autonomous_mode: true`:
- Run all phases automatically
- On canary critical failure: revert and park auto-pilot with blocker
- On canary high failure: revert and park (do not ask — safe default)
- On gate failure: park auto-pilot, list failed gates as blockers
- Never deploy from main/master even in autonomous mode

---

## Rules

- Never deploy without passing all pre-merge gates
- Never force-push to revert — always use platform rollback or revert commits
- Docs-only changes skip deployment entirely — never waste a deploy slot
- Dry run must succeed before live deploy runs
- Revert anchor (pre_deploy_sha) must be recorded before every deploy
- **Never contribute anything upstream** — upstream is exclusively evolve-self's responsibility
