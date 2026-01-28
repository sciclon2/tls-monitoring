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

### 1. Local Setup (Optional)

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Create GitHub Secrets

Go to your repository **Settings → Secrets and variables → Actions** and add:

| Secret | Value | Required |
|--------|-------|----------|
| `MONITOR_DOMAINS` | Comma-separated domains (e.g., `example.com,test.com`) | ✅ Yes |
| `ALERT_EMAILS` | Email addresses for alerts | ❌ Optional |
| `CERT_EXPIRATION_THRESHOLD_DAYS` | Days before expiration to alert (default: 30) | ❌ Optional |
| `PAT_TOKEN` | GitHub Personal Access Token (for private repos) | ✅ Yes (if private) |

### 3. For Private Repositories

1. Create a PAT: https://github.com/settings/tokens → Generate new token (classic)
   - Scopes: Check `repo`
2. Add as `PAT_TOKEN` secret (see step 2)

### 4. Enable Notifications

1. Watch the repo: Click **Watch** button → Select **All Activity**
2. Enable email: https://github.com/settings/notifications → Check "Email" under Watching

### 5. Run Locally (Optional)

```bash
# Use .env file or set environment variables
python main.py
```

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

## Configuration

### Via GitHub Secrets (Recommended for GHA)

Set these as GitHub Secrets:
- `MONITOR_DOMAINS=example.com,test.com`
- `ALERT_EMAILS=your@email.com`
- `CERT_EXPIRATION_THRESHOLD_DAYS=30`

### Via .env File (Local Development)

```env
MONITOR_DOMAINS=example.com,test.com
CERT_EXPIRATION_THRESHOLD_DAYS=30
ALERT_EMAILS=your@email.com
DEBUG=false
```

**Priority**: Environment variables override `.env` file settings.

## Manual Trigger

Run the workflow manually:
1. Go to **Actions** tab
2. Select **TLS Certificate Monitoring**
3. Click **Run workflow** → **Run workflow**

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "Repository not found" in GHA | Add `PAT_TOKEN` secret (private repos only) |
| No email notifications | Watch the repo and enable email in https://github.com/settings/notifications |
| Workflow not running | Check Actions are enabled in Settings → Actions → General |
| GitHub Issues not created | Check `.env` or GitHub Secrets for `MONITOR_DOMAINS` |

## Environment Variables

| Variable | Default | Purpose |
|----------|---------|---------|
| `MONITOR_DOMAINS` | (required) | Domains to monitor (comma-separated) |
| `CERT_EXPIRATION_THRESHOLD_DAYS` | 30 | Days before expiration to alert |
| `ALERT_EMAILS` | (empty) | Email addresses shown in alerts |
| `DEBUG` | false | Enable debug output |

## License

MIT
