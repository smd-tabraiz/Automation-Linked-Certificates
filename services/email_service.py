import smtplib
import csv
import os
import time
from email.message import EmailMessage

def clean_name(name):
    return name.strip().replace(" ", "_")

def send_certificates(
    csv_file,
    renamed_folder,
    sender_email,
    app_password,
    subject,
    log_file
):
    sent_count = 0
    failed_count = 0

    with open(log_file, "w", encoding="utf-8") as log:
        log.write("Certificate Sending Logs\n\n")

    with open(csv_file, newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(sender_email, app_password)

            for row in reader:
                name = row["name"]
                email = row["email"]
                filename = clean_name(name)

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

                msg = EmailMessage()
                msg["From"] = sender_email
                msg["To"] = email
                msg["Subject"] = subject

                msg.set_content(f"""
Dear {name},

Congratulations 🎉

Please find your certificate attached.

Regards,
Event Team
""")

                with open(cert_file, "rb") as f:
                    msg.add_attachment(
                        f.read(),
                        maintype="application",
                        subtype="octet-stream",
                        filename=os.path.basename(cert_file)
                    )

                try:
                    server.send_message(msg)
                    sent_count += 1
                    with open(log_file, "a", encoding="utf-8") as log:
                        log.write(f"✅ Sent to {email}\n")
                except Exception as e:
                    failed_count += 1
                    with open(log_file, "a", encoding="utf-8") as log:
                        log.write(f"❌ Failed {email}: {str(e)}\n")

                time.sleep(2)

    return sent_count, failed_count
