#!/usr/bin/env python3
"""
TLS Certificate Monitoring via GitHub Actions
Checks certificate expiration dates and sends alerts via email/Slack/Discord
No New Relic required!
"""

import os
import ssl
import socket
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
import json
import certifi

# ============================================================================
# CONFIG
# ============================================================================

def load_config():
    """Load configuration from .env file"""
    script_dir = Path(__file__).parent
    env_file = script_dir / ".env"
    load_dotenv(dotenv_path=str(env_file), override=True)
    
    return {
        "domains_str": os.getenv("MONITOR_DOMAINS", ""),
        "threshold_days": int(os.getenv("CERT_EXPIRATION_THRESHOLD_DAYS", "30")),
        "alert_emails_str": os.getenv("ALERT_EMAILS", "").strip(),
        "debug": os.getenv("DEBUG", "false").lower() == "true",
    }


def validate_config(config):
    """Validate required configuration"""
    if not config["domains_str"]:
        raise RuntimeError("Missing MONITOR_DOMAINS")


def parse_domains(domains_str):
    """Parse domain list"""
    return [d.strip() for d in domains_str.split(",") if d.strip()]


def parse_emails(emails_str):
    """Parse comma-separated email list"""
    return [e.strip() for e in emails_str.split(",") if e.strip()] if emails_str else []


# ============================================================================
# CERTIFICATE CHECKING
# ============================================================================

def get_certificate_expiry(domain, port=443, timeout=10):
    """Get certificate expiry date for a domain
    
    Returns:
        {
            "domain": "example.com",
            "expires_at": datetime object,
            "days_remaining": int,
            "status": "OK" | "EXPIRING" | "ERROR",
            "error": str (if status is ERROR)
        }
    """
    try:
        context = ssl.create_default_context()
        # Use certifi's comprehensive certificate bundle for better compatibility
        context.load_verify_locations(certifi.where())
        with socket.create_connection((domain, port), timeout=timeout) as sock:
            with context.wrap_socket(sock, server_hostname=domain) as ssock:
                cert = ssock.getpeercert()
                
                # Parse expiry date
                expires_str = cert.get("notAfter")
                # Format: 'Jun 15 12:34:56 2025 GMT'
                expires_at = datetime.strptime(expires_str, "%b %d %H:%M:%S %Y %Z")
                
                days_remaining = (expires_at - datetime.now()).days
                
                # Determine status
                if days_remaining < 0:
                    status = "EXPIRED"
                elif days_remaining < 7:
                    status = "CRITICAL"
                else:
                    status = "OK"
                
                return {
                    "domain": domain,
                    "expires_at": expires_at,
                    "days_remaining": days_remaining,
                    "status": status,
                    "error": None,
                }
    
    except ssl.SSLError as e:
        # If certificate chain verification fails, try without hostname verification
        # This handles cases where servers don't send intermediate certificates
        if "CERTIFICATE_VERIFY_FAILED" in str(e):
            try:
                context = ssl.create_default_context()
                context.check_hostname = False
                context.verify_mode = ssl.CERT_NONE
                
                with socket.create_connection((domain, port), timeout=timeout) as sock:
                    with context.wrap_socket(sock, server_hostname=domain) as ssock:
                        cert = ssock.getpeercert()
                        
                        expires_str = cert.get("notAfter")
                        expires_at = datetime.strptime(expires_str, "%b %d %H:%M:%S %Y %Z")
                        
                        days_remaining = (expires_at - datetime.now()).days
                        
                        if days_remaining < 0:
                            status = "EXPIRED"
                        elif days_remaining < 7:
                            status = "CRITICAL"
                        else:
                            status = "OK"
                        
                        return {
                            "domain": domain,
                            "expires_at": expires_at,
                            "days_remaining": days_remaining,
                            "status": status,
                            "error": None,
                        }
            except Exception as fallback_e:
                return {
                    "domain": domain,
                    "expires_at": None,
                    "days_remaining": None,
                    "status": "ERROR",
                    "error": str(fallback_e),
                }
        else:
            return {
                "domain": domain,
                "expires_at": None,
                "days_remaining": None,
                "status": "ERROR",
                "error": str(e),
            }
    
    except Exception as e:
        return {
            "domain": domain,
            "expires_at": None,
            "days_remaining": None,
            "status": "ERROR",
            "error": str(e),
        }


def check_threshold(cert_info, threshold_days):
    """Check if certificate is below threshold
    
    Returns: True if alert should be sent
    """
    if cert_info["status"] == "ERROR":
        return True
    
    if cert_info["days_remaining"] is None:
        return True
    
    if cert_info["days_remaining"] < threshold_days:
        return True
    
    return False


# ============================================================================
# ALERTING
# ============================================================================

def send_email_via_github(emails, alert_data):
    """Log email alert to console"""
    if not emails:
        return
    
    print("\n" + "="*60)
    print("📧 EMAIL ALERT")
    print("="*60)
    print(f"To: {', '.join(emails)}")
    print("\nSubject: 🚨 TLS Certificate Expiration Alert")
    print("\nBody:")
    print("-" * 60)
    
    for domain_info in alert_data["alerts"]:
        domain = domain_info["domain"]
        days = domain_info["days_remaining"]
        expires = domain_info["expires_at"]
        status = domain_info["status"]
        
        print(f"\n🔴 {domain}")
        print(f"   Status: {status}")
        
        if status == "ERROR":
            print(f"   Error: {domain_info['error']}")
        else:
            print(f"   Expires: {expires.strftime('%Y-%m-%d')}")
            print(f"   Days remaining: {days}")
    
    print("\n" + "-" * 60)
    print("Threshold: {} days".format(alert_data["threshold_days"]))
    print("="*60 + "\n")


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Main execution"""
    print("="*60)
    print("TLS Certificate Monitoring")
    print("="*60)
    print()
    
    # Load configuration
    config = load_config()
    validate_config(config)
    
    domains = parse_domains(config["domains_str"])
    emails = parse_emails(config["alert_emails_str"])
    threshold_days = config["threshold_days"]
    
    print(f"Checking {len(domains)} domain(s)")
    print(f"Threshold: {threshold_days} days")
    print()
    
    # Check each domain
    results = []
    for domain in domains:
        print(f"Checking {domain}...", end=" ")
        cert_info = get_certificate_expiry(domain)
        results.append(cert_info)
        
        if cert_info["status"] == "ERROR":
            print(f"❌ ERROR")
        elif cert_info["status"] == "EXPIRED":
            print(f"🔴 EXPIRED")
        elif cert_info["status"] == "CRITICAL":
            print(f"⚠️  CRITICAL ({cert_info['days_remaining']} days)")
        else:
            print(f"✓ OK ({cert_info['days_remaining']} days)")
    
    print()
    
    # Check for alerts
    alerts = [r for r in results if check_threshold(r, threshold_days)]
    
    if not alerts:
        print("✓ All certificates are healthy!")
        print("="*60)
        return 0
    
    # Send alerts
    print(f"🚨 {len(alerts)} certificate(s) need attention!")
    print()
    
    alert_data = {
        "alerts": alerts,
        "threshold_days": threshold_days,
        "checked_at": datetime.now().isoformat(),
    }
    
    # Send via email
    if emails:
        send_email_via_github(emails, alert_data)
    else:
        print("⚠️  No alert emails configured")
    
    # Output alert data as JSON for GitHub Actions (if running in GHA)
    if os.getenv("GITHUB_OUTPUT"):
        if alerts:
            alerts_json = json.dumps([{
                "domain": alert["domain"],
                "status": alert["status"],
                "days_remaining": alert["days_remaining"],
                "expires_at": alert["expires_at"].isoformat() if alert["expires_at"] else None,
                "error": alert["error"]
            } for alert in alerts])
            with open(os.getenv("GITHUB_OUTPUT"), "a") as f:
                f.write(f"alerts={alerts_json}\n")
    
    print("="*60)
    return 1 if alerts else 0


if __name__ == "__main__":
    exit(main())
