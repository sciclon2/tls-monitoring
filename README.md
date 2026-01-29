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

### 1. Create GitHub Secrets (Optional)

Go to your repository **Settings → Secrets and variables → Actions** and add:

| Secret | Value | Required |
|--------|-------|----------|
| `MONITOR_DOMAINS` | Comma-separated domains (e.g., `example.com,test.com`) | ❌ No (uses `.env` by default) |
| `PAT_TOKEN` | GitHub Personal Access Token | ✅ Yes (if private repo) |

**Note:** If you don't set `MONITOR_DOMAINS` secret, the workflow will use domains from the `.env` file.

**To create a PAT:**
1. Go to https://github.com/settings/tokens
2. Click "Generate new token" → "Generate new token (classic)"
3. Check scope: `repo` (Full control of private repositories)
4. Copy the token and add it as `PAT_TOKEN` secret

### 2. Enable Notifications

1. **Watch the repo**: Click **Watch** button → Select **All Activity**
2. **Enable email**: https://github.com/settings/notifications → Check "Email" under Watching

### 3. Run Locally (Optional)

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

### Configuration Priority Order

The script loads configuration in this order (highest to lowest priority):

1. **Command-line arguments** (e.g., `--domains "example.com" --threshold 30`)
2. **GitHub Secrets** (when running in GitHub Actions)
3. **Environment variables** (set locally or in `.env` file)
4. **Default values** (threshold: 30 days)

**Example**: If `.env` has `MONITOR_DOMAINS=example.com,test.com` and you run `python main.py --domains "other.com"`, it uses `other.com`.

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

If `--domains` is empty or not provided, it falls back to environment variables or `.env` file.

### Via GitHub Actions

The workflow automatically:
1. Tries to use `MONITOR_DOMAINS` secret (if set)
2. Falls back to `.env` file (if secret is empty)
3. Uses threshold from `.env` (default: 30 days)
4. Requires `PAT_TOKEN` secret (for private repos)

Example GitHub Secret with runbooks:
```
example.com:https://internal.runbook.io/fix-ssl,test.com
```

### Via Environment Variables (Local)

```bash
export MONITOR_DOMAINS="example.com,test.com"
export CERT_EXPIRATION_THRESHOLD_DAYS=30
python main.py
```

### Via .env File (Local Development Only)

Create a `.env` file for local development:
```env
MONITOR_DOMAINS=example.com,test.com
CERT_EXPIRATION_THRESHOLD_DAYS=30
```

The `.env` file is used as a fallback if command-line arguments and environment variables are not provided.

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
| Missing domains error | Add `MONITOR_DOMAINS` to `.env` or GitHub Actions secrets |
| GitHub Issues not created | Check `.env` or GitHub Secrets for `MONITOR_DOMAINS` |

## Environment Variables

| Variable | Default | Purpose |
|----------|---------|---------|
| `MONITOR_DOMAINS` | (required) | Domains to monitor (comma-separated) |
| `CERT_EXPIRATION_THRESHOLD_DAYS` | 30 | Certificate expiry threshold in days |
| `DEBUG` | false | Enable debug output |

## License

MIT
