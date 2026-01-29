# TLS Certificate Monitoring

Automated TLS/SSL certificate expiration monitoring via GitHub Actions. Checks certificate expiration daily and creates GitHub Issues when certificates approach expiration.

## Features

- ✅ Checks TLS certificate expiration for a list of domains
- ✅ Runs daily via GitHub Actions (customizable schedule)
- ✅ Creates GitHub Issues when certificates fall below threshold
- ✅ Email notifications via GitHub's native system
- ✅ No external services required
- ✅ Handles incomplete certificate chains (uses openssl fallback)

## Quick Start

### 1. Create GitHub Secrets

Go to your repository **Settings → Secrets and variables → Actions** and add:

| Secret | Value | Required |
|--------|-------|----------|
| `MONITOR_DOMAINS` | Comma-separated domains (e.g., `example.com,test.com`) | ✅ Yes |
| `PAT_TOKEN` | GitHub Personal Access Token | ✅ Yes (if private repo) |

**To create a PAT:**
1. Go to https://github.com/settings/tokens
2. Click "Generate new token" → "Generate new token (classic)"
3. Check scope: `repo` (Full control of private repositories)
4. Copy the token and add it as `PAT_TOKEN` secret

### 2. Enable Notifications

1. **Watch the repo**: Click **Watch** button → Select **All Activity**
2. **Enable email**: https://github.com/settings/notifications → Check "Email" under Watching

### Run Locally (Optional)

```bash
# Setup
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run with arguments
python main.py --domains "example.com,test.com" --threshold 30

# Or use environment variables
MONITOR_DOMAINS="example.com,test.com" python main.py

# Include runbook URLs (only shown in GitHub Issues, not console)
python main.py --domains "example.com:https://runbook.com/fix-cert,test.com" --threshold 30
```

## Configuration

### Domain Format with Runbook URLs

You can optionally include runbook URLs with domains. The runbook URL is only shown in GitHub Issues (private), not in console output:

```
domain1,domain2:https://runbook.company.com/certs,domain3:https://wiki.company.com/ssl
```

Format: `domain:runbook_url,domain,domain:runbook_url`

### Via Command-Line Arguments (Local)

```bash
python main.py --domains "example.com,test.com:https://runbook.com/fix" --threshold 30
```

### Via GitHub Actions

The workflow automatically uses:
- `MONITOR_DOMAINS` from GitHub Secrets (required, supports runbook URLs)
- Threshold: **5000 days** (hardcoded in workflow)
- `PAT_TOKEN` from GitHub Secrets (required for private repos)

Example GitHub Secret with runbooks:
```
example.com:https://internal.runbook.io/fix-ssl,test.com
```

To use different thresholds locally, pass `--threshold` argument:
```bash
python main.py --domains "example.com:https://runbook.com/fix" --threshold 30
```

### Via .env File (Local Development Only)

Create a `.env` file for local development:
```env
MONITOR_DOMAINS=example.com,test.com
CERT_EXPIRATION_THRESHOLD_DAYS=30
```

**Priority**: Command-line args > Environment variables > .env file

## How It Works

```
Daily Trigger (9 AM UTC)
    ↓
Check certificate expiration for each domain
    ↓
Compare against threshold
    ↓
If below threshold → Create GitHub Issue
    ↓
GitHub sends you email notification
```

## Manual Trigger

Run the workflow manually:
1. Go to **Actions** tab
2. Select **TLS Certificate Monitoring**
3. Click **Run workflow** → **Run workflow**

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "Repository not found" in GHA | Add `PAT_TOKEN` secret in Settings → Secrets and variables → Actions |
| No email notifications | Make sure you're **watching** the repo and have email enabled |
| Workflow not running | Check Actions are enabled in Settings → Actions → General |
| Missing domains error | Add `MONITOR_DOMAINS` secret in GitHub Actions secrets |

## License

MIT
| GitHub Issues not created | Check `.env` or GitHub Secrets for `MONITOR_DOMAINS` |

## Environment Variables

| Variable | Default | Purpose |
|----------|---------|---------|
| `MONITOR_DOMAINS` | (required) | Domains to monitor (comma-separated) |
| `DEBUG` | false | Enable debug output |
## License

MIT
