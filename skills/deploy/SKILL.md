---
name: deploy
description: Platform auto-detect deployment with dry-run, canary verification, and revert escape hatch. Supports Vercel, Netlify, Railway, Fly.io, AWS, GCP, Heroku, and generic Docker.
version: 1.0.0
triggers:
  - User runs /prodmasterai deploy
  - User says "deploy", "push to production", "release to prod", "go live"
reads:
  - memory/project-context.md
writes:
  - memory/project-context.md
generated: false
generated_from: ""
---

# Deploy — Platform Auto-Detect Deployment

Deploy the current branch with automatic platform detection, dry-run safety, canary verification, and one-command revert.

## Process

### 1. Platform Detection (parallel)

Check for platform config files simultaneously:

| File | Platform | Deploy command |
|---|---|---|
| `vercel.json` or `.vercel/` | Vercel | `vercel --prod` |
| `netlify.toml` | Netlify | `netlify deploy --prod` |
| `railway.toml` or `railway.json` | Railway | `railway up` |
| `fly.toml` | Fly.io | `fly deploy` |
| `Dockerfile` + `AWS` env | AWS ECS/Fargate | `aws ecs update-service` |
| `app.yaml` (GCP) | Google Cloud Run | `gcloud run deploy` |
| `Procfile` + `heroku` remote | Heroku | `git push heroku main` |
| `Dockerfile` (generic) | Docker | `docker build && docker push` |
| `package.json` with `deploy` script | npm deploy | `npm run deploy` |

If multiple platforms detected: list them and ask which one.
If none detected: ask for platform or provide generic Docker deployment.

### 2. Pre-Deploy Checks

- Tests must be passing (run test suite)
- No critical security issues (check `memory/security-gate-state.json`)
- Branch is up-to-date with main (no merge conflicts)

If any check fails: **stop** and report.

### 3. Dry Run

Execute the deploy command with `--dry-run` or equivalent:
- Vercel: `vercel --prod --dry-run`
- Fly.io: `fly deploy --dry-run`
- Docker: `docker build` (build only, no push)
- Others: platform-specific preview command

Show what would change. Ask for confirmation.

### 4. Deploy

Execute the actual deploy command. Capture output and deployment URL.

### 5. Canary Verification

After deploy, run basic health checks:
1. HTTP GET to deployment URL — expect 200
2. Check `/health` or `/api/health` endpoint if it exists
3. Compare response time against baseline (warn if >2x slower)

If health check fails: offer immediate revert.

### 6. Revert Escape Hatch

If requested or if canary fails:
- Vercel: `vercel rollback`
- Fly.io: `fly releases rollback`
- Heroku: `heroku rollback`
- Docker: redeploy previous image tag
- Generic: `git revert HEAD && deploy`

### Completion Message

```
Deploy Complete
===============
Platform: <platform>
URL:      <deployment url>
Status:   healthy / degraded / failed
Canary:   passed / failed
Revert:   run /prodmasterai deploy revert
```

## Rules

- ALWAYS dry-run first — never deploy without preview
- ALWAYS run canary verification after deploy
- If canary fails, offer revert immediately — don't wait for user to notice
- Never deploy with failing tests or critical security issues
- Store the deploy SHA and URL for revert capability
