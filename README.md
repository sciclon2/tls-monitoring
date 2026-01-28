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

### How Alerts Work in GitHub Actions

1. **Daily Trigger**: Workflow automatically runs at 9 AM UTC every day
2. **Certificate Checks**: Script connects to each domain via SSL and extracts expiration dates
3. **Threshold Comparison**: If any certificate is within the threshold days of expiration, an alert is triggered
4. **GitHub Issues Creation**: For each certificate that needs attention, the workflow creates a GitHub Issue with:
   - Domain name in the title
   - Certificate status (OK, EXPIRING, CRITICAL, ERROR)
   - Expiration date and days remaining
   - Link to the workflow logs
   - `security` and `certificate-alert` labels
5. **Email Notifications**: GitHub automatically emails you when:
   - An issue is created (if you're watching the repo)
   - Someone mentions you in the issue
   - You're subscribed to that issue

### Setting Up GitHub Actions Alerts

#### Step 1: Create a Personal Access Token (PAT)

Since this is a **private repository**, the workflow needs a PAT to access it.

1. Go to https://github.com/settings/tokens
2. Click **"Generate new token"** → **"Generate new token (classic)"**
3. Fill in the details:
   - **Note**: `newrelic-tls-monitoring-pat` (or any name you prefer)
   - **Expiration**: 90 days or No expiration (your choice)
   - **Select scopes**: Check `repo` (Full control of private repositories)
4. Click **"Generate token"** and copy the token (it won't be shown again!)

#### Step 2: Add the PAT as a Repository Secret

1. Go to your repository: https://github.com/sciclon2/newrelic-tls-monitoring
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **"New repository secret"**
4. Fill in:
   - **Name**: `PAT_TOKEN`
   - **Secret**: Paste your Personal Access Token
5. Click **"Add secret"**

#### Step 3: Watch the Repository for Notifications

1. Go to your repository: https://github.com/sciclon2/newrelic-tls-monitoring
2. Click the **Watch** button (top right, next to Star)
3. Select **All Activity** to be notified of all issues and comments

#### Step 4: Enable Email Notifications

1. Go to https://github.com/settings/notifications
2. Under **Watching** section, check the box for **Email**
3. Verify your primary email at https://github.com/settings/emails is correct

### GitHub Actions Workflow Steps

The workflow performs these steps:

1. **Checkout Code** - Uses your PAT token to access the private repo
2. **Set up Python** - Installs Python 3.9
3. **Install CA Certificates** - Ensures SSL certificate chain validation works
4. **Install Dependencies** - Installs required Python packages (`python-dotenv`, `certifi`)
5. **Run TLS Monitoring Script** - Executes the certificate check script
6. **Extract Alerts and Create Issues** - If alerts are found, creates GitHub Issues with details

When the workflow runs daily:
- ✅ Certificates are checked automatically
- ✅ GitHub Issues are created if certificates need attention
- ✅ You receive an email notification (if watching)
- ✅ Full logs available in the Actions tab

### Manual Trigger

You can also run the workflow manually:

1. Go to your repository
2. Click **Actions** tab
3. Select **"TLS Certificate Monitoring"** workflow
4. Click **"Run workflow"** → **Run workflow**

### Viewing Results

After the workflow runs:

1. **View Issues**: Go to the **Issues** tab to see created alerts
2. **View Logs**: Go to **Actions** tab → Latest workflow run to see full output
3. **Issue Details**: Each issue shows:
   - Domain name
   - Certificate status
   - Expiration date
   - Days remaining
   - Links to workflow logs

### Example GitHub Issue Created

```
Title: ⚠️ Certificate Alert: example.com

Status: CRITICAL

Expiration Date: 2026-02-12
Days Remaining: 15

Details:
- Repository: sciclon2/newrelic-tls-monitoring
- Triggered: 2026-01-28T09:00:00.000Z
- Workflow: View Logs (link to workflow run)

Take action to renew or fix the certificate.
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

### GitHub Actions Issues

- **"Repository not found" error**: 
  - Ensure you've created a PAT token and added it as `PAT_TOKEN` secret
  - Go to **Settings** → **Secrets and variables** → **Actions** to verify
  - Check that the PAT has `repo` scope access

- **Workflow not running**: 
  - Check that GitHub Actions is enabled (Settings → Actions → General)
  - Verify the workflow file is in `.github/workflows/tls-monitoring.yml`
  - Check the **Actions** tab for any error messages

- **No email notifications received**:
  - Make sure you're **watching** the repository (Watch button at top right)
  - Go to https://github.com/settings/notifications and check "Email" under Watching
  - Verify your primary email at https://github.com/settings/emails
  - Check your spam/junk folder

- **GitHub Issues not created**:
  - Check the workflow logs in the **Actions** tab
  - Verify `MONITOR_DOMAINS` is configured in `.env`
  - Ensure at least one certificate is below the threshold

### SSL/Certificate Issues

- **SSL Connection Error**: Verify domain is accessible and has a valid SSL certificate
- **Certificate Verify Failed (GHA only)**: This is automatically handled with fallback verification
- **Missing intermediate certificate**: Script uses `openssl` to parse certificates when chain verification fails

- **Threshold Not Triggering**: Check that `CERT_EXPIRATION_THRESHOLD_DAYS` is set correctly in `.env`

## License

MIT
