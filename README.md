# TLS Certificate Monitoring

Automated TLS/SSL certificate expiration monitoring via GitHub Actions. Checks certificate expiration dates daily and creates GitHub Issues when certificates approach expiration.

## Features

- Checks TLS certificate expiration for a list of domains
- Direct SSL connection to domains (no intermediaries needed)
- Runs daily via GitHub Actions
- Creates GitHub Issues when certificates fall below threshold
- Email notifications via GitHub's native notification system
- Simple configuration via `.env` file
- No external services required (no email server, no New Relic, no webhooks)

## Prerequisites

- Python 3.8+
- GitHub repository with Actions enabled
- A list of domains to monitor

## Setup

### 1. Clone the repository

```bash
cd /path/to/newrelic-tls-monitoring
```

### 2. Create a virtual environment (recommended)

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Edit the `.env` file with your values:

```env
# Comma-separated list of domains to monitor
MONITOR_DOMAINS=brattlecameron.com,example.com

# Certificate expiration threshold in days (default: 30)
CERT_EXPIRATION_THRESHOLD_DAYS=30

# Comma-separated list of email addresses to alert
ALERT_EMAILS=sergio.troiano@iwgplc.com

# Debug mode (default: false)
DEBUG=false
```

### 5. Run the script locally (optional)

```bash
python main.py
```

**Note**: Running locally only prints certificate details to the console. GitHub Issues are created automatically by the GitHub Actions workflow when it runs daily.

## How it Works

1. **Daily Trigger**: GitHub Actions workflow runs daily at 9 AM UTC
2. **Certificate Checks**: Script connects directly to each domain via SSL to extract expiration dates
3. **Threshold Comparison**: Expiration dates are compared against the configured threshold
4. **GitHub Issues**: If any certificate falls below threshold, the workflow creates a GitHub Issue
5. **Email Alerts**: GitHub notifies you via email (if you're watching the repo)
6. **Logs**: Full certificate details are available in the GitHub Actions workflow output

### Running Locally

You can also run the script manually to check certificate status:

```bash
python main.py
```

When run locally, it prints certificate details to the console. GitHub Issues and email notifications only happen via the GitHub Actions workflow.

### Example Output

```
============================================================
TLS Certificate Monitoring
============================================================

Checking 2 domain(s)
Threshold: 30 days

Checking brattlecameron.com... ✓ OK (365 days)
Checking example.com... ⚠️  CRITICAL (15 days)

🚨 1 certificate(s) need attention!

============================================================
📧 EMAIL ALERT
============================================================
To: sergio.troiano@iwgplc.com

Subject: 🚨 TLS Certificate Expiration Alert

Body:
------------------------------------------------------------

🔴 example.com
   Status: CRITICAL
   Expires: 2026-02-12
   Days remaining: 15

------------------------------------------------------------
Threshold: 30 days
============================================================
```

## GitHub Actions Workflow

The workflow runs daily at 9 AM UTC (customizable via cron):

```yaml
on:
  schedule:
    - cron: '0 9 * * *'  # Daily at 9 AM UTC
  workflow_dispatch:     # Allow manual trigger
```

When certificates fall below threshold:
1. Workflow step creates a GitHub Issue with alert details
2. Issue is labeled with `security` and `certificate-alert`
3. GitHub emails all repo watchers/members
4. Full certificate details available in workflow logs

## Environment Variables

- `MONITOR_DOMAINS` - Comma-separated list of domains to monitor (required)
  - Example: `brattlecameron.com,example.com`
- `CERT_EXPIRATION_THRESHOLD_DAYS` - Days before expiration to trigger alert (default: 30)
- `ALERT_EMAILS` - Email addresses displayed in GitHub Issues (optional)
- `DEBUG` - Enable debug output (default: false)

## Testing Locally

Test the certificate checker before deploying:

```bash
# Check certificate status
python main.py

# With debug output
DEBUG=true python main.py
```

## Troubleshooting

- **SSL Connection Error**: Verify domain is accessible and has a valid SSL certificate
- **Threshold Not Triggering**: Check that `CERT_EXPIRATION_THRESHOLD_DAYS` is set correctly
- **GitHub Issues Not Created**: Ensure GitHub Actions are enabled and workflow file is valid
- **No Email Notifications**: Verify you're watching the repository (GitHub Settings > Notifications)

## License

MIT
