import csv
import os
import time
import base64
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import (
    Mail, Attachment, FileContent, FileName, FileType, Disposition
)

def clean_name(name: str) -> str:
    return name.strip().replace(" ", "_")

def send_certificates(
    csv_file: str,
    renamed_folder: str,
    sender_email: str,
    sendgrid_api_key: str,
    subject: str,
    email_body: str,          # ✅ NEW
    log_file: str
):
    """
    Sends certificates using SendGrid Email API.
    Supports {name} personalization in email body.
    Returns: (sent_count, failed_count)
    """

    sent_count = 0
    failed_count = 0

    # Default email body fallback
    if not email_body or email_body.strip() == "":
        email_body = (
            "Dear {name},\n\n"
            "Thank you for participating in our event.\n"
            "Please find your certificate attached.\n\n"
            "Regards,\n"
            "Event Team"
        )

    # Initialize log file
    with open(log_file, "w", encoding="utf-8") as log:
        log.write("Certificate Sending Logs (SendGrid API)\n\n")

    sg = SendGridAPIClient(sendgrid_api_key)

    with open(csv_file, newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            name = row["name"]
            email = row["email"]
            filename = clean_name(name)

            # Find certificate
            cert_file = None
            for ext in [".jpg", ".jpeg", ".png", ".pdf"]:
                path = os.path.join(renamed_folder, filename + ext)
                if os.path.exists(path):
                    cert_file = path
                    break

            if not cert_file:
                failed_count += 1
                with open(log_file, "a", encoding="utf-8") as log:
                    log.write(f"❌ Missing certificate for {name}\n")
                continue

            # 🔥 Personalize email body
            personalized_body = email_body.replace("{name}", name)

            # Create email
            message = Mail(
                from_email=sender_email,
                to_emails=email,
                subject=subject,
                plain_text_content=personalized_body
            )

            # Attach certificate
            with open(cert_file, "rb") as f:
                encoded_file = base64.b64encode(f.read()).decode()

            attachment = Attachment(
                FileContent(encoded_file),
                FileName(os.path.basename(cert_file)),
                FileType("application/octet-stream"),
                Disposition("attachment")
            )

            message.attachment = attachment

            try:
                sg.send(message)
                sent_count += 1
                with open(log_file, "a", encoding="utf-8") as log:
                    log.write(f"✅ Sent to {email}\n")
            except Exception as e:
                failed_count += 1
                with open(log_file, "a", encoding="utf-8") as log:
                    log.write(f"❌ Failed {email}: {str(e)}\n")

            time.sleep(1)  # Safe throttling

    return sent_count, failed_count
