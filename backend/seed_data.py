"""
Scam Shield - Seed Simulations Script
Populates 20 realistic phishing and legitimate scenarios matching the exact check constraints.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent / ".env")
from app.core.supabase_client import supabase_admin

scenarios = [
    # EASY PHISHING (5)
    {
        "title": "Urgent Account Suspension Notice",
        "type": "email",
        "difficulty": "easy",
        "sender_name": "PayPal Security Team",
        "sender_email": "security-alert@paypa1-support.com",
        "subject": "URGENT: Your Account Will Be Suspended in 24 Hours!!!",
        "body": "Dear Valued Customer,\n\nWe have detected unusual activity on your PayPal account. Click here to verify your identity immediately: http://paypa1-secure-login.tk/verify\n\nIf you do not comply, your account will be frozen permanently.",
        "is_phishing": True,
        "explanation": "High urgency threat, suspicious misspelled domain (paypa1-support.com), and insecure link (.tk TLD).",
        "category": "credential_harvesting",
    },
    {
        "title": "You've Won a $1,000 Gift Card!",
        "type": "email",
        "difficulty": "easy",
        "sender_name": "Amazon Rewards Department",
        "sender_email": "rewards@amazon-prizes-winner.net",
        "subject": "🎉 Congratulations! You've Won a $1,000 Amazon Gift Card!",
        "body": "Dear Lucky Winner,\n\nYou have been randomly selected to win a $1,000 gift card! Claim now by paying a small $4.99 processing fee: http://amazon-gift-prizes.xyz/claim",
        "is_phishing": True,
        "explanation": "Classic advance fee prize scam asking for credit card information under the guise of a shipping/processing fee.",
        "category": "financial_scam",
    },
    {
        "title": "IRS Tax Refund Notification",
        "type": "email",
        "difficulty": "easy",
        "sender_name": "Internal Revenue Service",
        "sender_email": "refunds@irs-gov-refund.com",
        "subject": "Tax Refund Notification - Action Required",
        "body": "You are eligible for a tax refund of $3,247.65. Submit your SSN, banking details, and date of birth at: http://irs-refund-portal.co/verify",
        "is_phishing": True,
        "explanation": "The IRS never initiates contact with taxpayers by email to request personal or financial information.",
        "category": "identity_theft",
    },
    {
        "title": "Password Expiry Warning",
        "type": "email",
        "difficulty": "easy",
        "sender_name": "IT Help Desk",
        "sender_email": "helpdesk@it-aboracorp.com",
        "subject": "[ACTION REQUIRED] Your Password Expires Today!",
        "body": "Your email password will expire TODAY. Click here to reset your password: http://aboracorp-password-reset.tk/reset",
        "is_phishing": True,
        "explanation": "Unsolicited urgency and external non-corporate domain for internal corporate password management.",
        "category": "credential_harvesting",
    },
    {
        "title": "Wire Transfer Request",
        "type": "email",
        "difficulty": "easy",
        "sender_name": "Prince Abubakar",
        "sender_email": "prince.abubakar@diplomat-mail.org",
        "subject": "Confidential Transfer Request - $15.5 Million USD",
        "body": "I need your assistance transferring $15,500,000 USD out of the country. Reply with your bank details to receive 30% commission.",
        "is_phishing": True,
        "explanation": "Classic advance-fee fraud from an unknown sender promising exorbitant financial reward.",
        "category": "financial_scam",
    },

    # MEDIUM PHISHING (3)
    {
        "title": "HR Benefit Plan Enrollment",
        "type": "email",
        "difficulty": "medium",
        "sender_name": "Corporate HR Benefits",
        "sender_email": "hr-benefits@company-internal-portal.net",
        "subject": "Annual Open Enrollment - Action Required by Friday",
        "body": "Please log in to review your 2026 health insurance selections before Friday: https://hr-portal-benefits-login.com/enroll",
        "is_phishing": True,
        "explanation": "Spoofed internal HR notification pointing to an external domain designed to harvest corporate Single Sign-On credentials.",
        "category": "credential_harvesting",
    },
    {
        "title": "Shared OneDrive Document",
        "type": "email",
        "difficulty": "medium",
        "sender_name": "Microsoft OneDrive",
        "sender_email": "no-reply@sharepoint-online-verify.com",
        "subject": "Sarah Jenkins shared 'Q3 Financial Projections.xlsx' with you",
        "body": "Sarah Jenkins has shared an encrypted spreadsheet with you. Access document: https://1drv-secure-access.com/doc/98712",
        "is_phishing": True,
        "explanation": "Lookalike domain mimicking SharePoint/OneDrive sharing notifications.",
        "category": "credential_harvesting",
    },
    {
        "title": "CEO Urgent Wire Transfer",
        "type": "email",
        "difficulty": "medium",
        "sender_name": "David Miller (CEO)",
        "sender_email": "david.miller.ceo@exec-mail-secure.com",
        "subject": "Confidential Acquisition - Urgent Wire Today",
        "body": "I am in an all-day confidential board meeting. Please immediately process a $45,000 wire to our partner vendor using the attached instructions.",
        "is_phishing": True,
        "explanation": "Executive impersonation / Business Email Compromise (BEC) pressuring finance staff to bypass standard verification protocols.",
        "category": "business_email_compromise",
    },

    # HARD PHISHING (3)
    {
        "title": "DocuSign: Vendor Contract Signature Request",
        "type": "email",
        "difficulty": "hard",
        "sender_name": "DocuSign Signature Service",
        "sender_email": "dse@docusign-envelope-service.com",
        "subject": "Please DocuSign: Master Services Agreement Amendment #3",
        "body": "All parties have completed review. Please sign your portion of the agreement: https://na3.docusign-envelope-service.com/Signing/Start?token=847f9",
        "is_phishing": True,
        "explanation": "High-fidelity mimicry of a genuine DocuSign notification with brand assets and subtle typo-squatted domain.",
        "category": "credential_harvesting",
    },
    {
        "title": "GitHub: Personal Access Token Expiring",
        "type": "email",
        "difficulty": "hard",
        "sender_name": "GitHub Security",
        "sender_email": "notifications@git-hub-security.com",
        "subject": "[GitHub] Your personal access token 'deploy-token' is expiring soon",
        "body": "Your personal access token will expire in 3 days. Review and renew it in settings: https://github-security-review.com/settings/tokens",
        "is_phishing": True,
        "explanation": "Targeted developer phishing mimicking legitimate GitHub token expiry alerts to gain repository access.",
        "category": "credential_harvesting",
    },
    {
        "title": "Zoom Meeting Client Update",
        "type": "email",
        "difficulty": "hard",
        "sender_name": "Zoom Video Communications",
        "sender_email": "invites@zoom-videomeeting.us",
        "subject": "Q4 Strategy Planning - Zoom Conference Link",
        "body": "Join the Zoom meeting: https://zoom-videomeeting.us/j/9817246510\n\nIf prompt appears, run Zoom_Meeting_Client.exe to enable HD audio.",
        "is_phishing": True,
        "explanation": "Trojanized link requesting the user download and execute an executable file to join a video call.",
        "category": "malware",
    },

    # LEGITIMATE EMAILS (3)
    {
        "title": "Company All-Hands Meeting Notification",
        "type": "email",
        "difficulty": "easy",
        "sender_name": "Corporate Internal Communications",
        "sender_email": "communications@aboracorp.com",
        "subject": "All-Hands Meeting - This Thursday at 2 PM EST",
        "body": "Team, please join us for our monthly all-hands meeting in the auditorium or on the internal intranet stream. No action required.",
        "is_phishing": False,
        "explanation": "Legitimate internal communication from a validated company domain without suspicious links or requests.",
        "category": "legitimate",
    },
    {
        "title": "Slack Notification: You Were Mentioned",
        "type": "email",
        "difficulty": "medium",
        "sender_name": "Slack",
        "sender_email": "notification@slack.com",
        "subject": "Alex Chen mentioned you in #general",
        "body": "Alex Chen: 'Hey team, the deployment went smoothly!' Open Slack to reply.",
        "is_phishing": False,
        "explanation": "Authentic notification from verified Slack domain with valid DKIM/SPF signatures.",
        "category": "legitimate",
    },
    {
        "title": "Google Cloud: Monthly Invoice Ready",
        "type": "email",
        "difficulty": "medium",
        "sender_name": "Google Cloud Billing",
        "sender_email": "cloud-billing-noreply@google.com",
        "subject": "Your Google Cloud invoice for October 2026 is available",
        "body": "Your monthly billing statement is now available directly in your Google Cloud Console. Log into console.cloud.google.com to view.",
        "is_phishing": False,
        "explanation": "Legitimate invoice advisory directing the user to navigate to the official portal rather than clicking an ambiguous external link.",
        "category": "legitimate",
    },

    # SMS / SMISHING (3)
    {
        "title": "Bank Fraud Alert SMS",
        "type": "sms",
        "difficulty": "easy",
        "sender_name": "+1 (800) 555-0199",
        "sender_email": None,
        "subject": "Chase Fraud Alert",
        "body": "CHASE ALERT: Did you attempt a $492.00 charge at Best Buy? If NO, secure your card immediately: http://chase-security-verify.link/id84",
        "is_phishing": True,
        "explanation": "Smishing scam creating panic about fraudulent charges to steal banking credentials.",
        "category": "financial_scam",
    },
    {
        "title": "USPS Package Delivery Smishing",
        "type": "sms",
        "difficulty": "easy",
        "sender_name": "+1 (888) 234-5678",
        "sender_email": None,
        "subject": "USPS Notification",
        "body": "USPS: Package #US948194 cannot be delivered due to incomplete address. Update info within 12 hours: http://usps-address-update.xyz/parcel",
        "is_phishing": True,
        "explanation": "Fake shipping update requiring card details or personal info to 'reschedule delivery'.",
        "category": "credential_harvesting",
    },
    {
        "title": "Automated Phone Verification Code (SMS)",
        "type": "sms",
        "difficulty": "easy",
        "sender_name": "22000",
        "sender_email": None,
        "subject": "Verification Code",
        "body": "Your authentication code is 849201. It expires in 5 minutes. Do not share this code with anyone.",
        "is_phishing": False,
        "explanation": "Legitimate short-code SMS one-time password explicitly warning against sharing.",
        "category": "legitimate",
    },

    # QR CODE PHISHING (QUISHING) (2)
    {
        "title": "Cafeteria Parking Payment QR Code",
        "type": "qr",
        "difficulty": "medium",
        "sender_name": "Parking Services",
        "sender_email": None,
        "subject": "Parking Fee QR Code",
        "body": "Scan the QR code sticker placed on the payment terminal to settle your daily parking rate.",
        "is_phishing": True,
        "explanation": "Quishing attack where malicious stickers are placed over legitimate physical QR codes to redirect to credential theft sites.",
        "category": "quishing",
    },
    {
        "title": "Two-Factor Authentication Setup QR",
        "type": "qr",
        "difficulty": "hard",
        "sender_name": "Security Operations",
        "sender_email": "soc-alert@mfa-enroll-system.com",
        "subject": "Urgent: Migrate to New Authenticator App",
        "body": "Our organization is migrating to hardware-backed tokens. Scan this QR code with your mobile camera to register your device immediately.",
        "is_phishing": True,
        "explanation": "Quishing scam evading email URL filters by embedding the phishing link inside a visual QR code image.",
        "category": "quishing",
    },

    # LEGITIMATE EMAIL SECURITY
    {
        "title": "GitHub Security Advisory: Dependency Update",
        "type": "email",
        "difficulty": "easy",
        "sender_name": "GitHub Support",
        "sender_email": "support@github.com",
        "subject": "Dependabot Advisory",
        "body": "Dependabot has created a pull request in your repo to patch a known dependency vulnerability. Review on github.com.",
        "is_phishing": False,
        "explanation": "Standard automated repository security notice without external credential requests.",
        "category": "legitimate",
    },
]

def seed():
    print(f"Checking existing scenarios...")
    existing = supabase_admin.table("simulations").select("id", count="exact").execute()
    count = existing.count if existing.count is not None else len(existing.data or [])
    if count > 0:
        print(f"Table already contains {count} scenarios. Skipping duplicate seed.")
        return True

    print(f"Inserting {len(scenarios)} scenarios into 'simulations' table...")
    res = supabase_admin.table("simulations").insert(scenarios).execute()
    inserted = len(res.data or [])
    print(f"✅ Successfully inserted {inserted} simulation scenarios!")
    return True

if __name__ == "__main__":
    success = seed()
    sys.exit(0 if success else 1)
