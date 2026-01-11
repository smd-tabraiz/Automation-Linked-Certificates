from flask import Flask, render_template, request, redirect, url_for, flash, session
import os
import csv

from services.rename_service import rename_certificates
from services.email_service import send_certificates

app = Flask(__name__)
app.secret_key = "9fb28e216def0dfbb430f1bcb12c30e1caa20e2d12cee3a3e490aab30a4a3d6a"

# ================= CONFIG =================
UPLOAD_CSV = "uploads/csv"
UPLOAD_CERTS = "uploads/certificates"
RENAMED_FOLDER = "certificates_renamed"
LOG_FILE = "logs.txt"

os.makedirs(UPLOAD_CSV, exist_ok=True)
os.makedirs(UPLOAD_CERTS, exist_ok=True)
os.makedirs(RENAMED_FOLDER, exist_ok=True)

# ================= INDEX =================
@app.route("/")
def index():
    return render_template("index.html")

# ================= PREVIEW =================
@app.route("/preview", methods=["POST"])
def preview():
    if "csv_file" not in request.files:
        flash("CSV file missing", "danger")
        return redirect(url_for("index"))

    csv_file = request.files["csv_file"]
    cert_files = request.files.getlist("cert_files")

    if csv_file.filename == "" or not cert_files:
        flash("CSV or certificates missing", "danger")
        return redirect(url_for("index"))

    csv_path = os.path.join(UPLOAD_CSV, csv_file.filename)
    csv_file.save(csv_path)

    for f in cert_files:
        f.save(os.path.join(UPLOAD_CERTS, f.filename))

    preview_data = []

    with open(csv_path, newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for idx, row in enumerate(reader, start=1):
            name = row["name"]
            email = row["email"]

            cert_name = "Missing"
            for ext in [".jpg", ".jpeg", ".png", ".pdf"]:
                path = os.path.join(UPLOAD_CERTS, f"{idx}{ext}")
                if os.path.exists(path):
                    cert_name = f"{idx}{ext}"
                    break

            preview_data.append({
                "name": name,
                "email": email,
                "certificate": cert_name,
                "status": "Ready" if cert_name != "Missing" else "Missing"
            })

    return render_template(
        "preview.html",
        preview_data=preview_data,
        csv_filename=csv_file.filename
    )

# ================= RESULT =================
@app.route("/preview-result")
def preview_result():
    return render_template(
        "preview_result.html",
        total=session.get("total", 0),
        sent=session.get("sent", 0),
        failed=session.get("failed", 0)
    )

# ================= SEND =================
@app.route("/process", methods=["POST"])
def process():
    try:
        if "csv_filename" not in request.form:
            flash("Please preview certificates before sending.", "danger")
            return redirect(url_for("index"))

        sender_email = request.form["sender_email"]
        sendgrid_api_key = request.form["app_password"]  # SendGrid API Key
        subject = request.form["subject"]
        email_body = request.form.get("email_body", "")  # ✅ NEW
        csv_filename = request.form["csv_filename"]

        # Basic API key validation
        if not sendgrid_api_key.startswith("SG."):
            flash("Invalid SendGrid API Key", "danger")
            return redirect(url_for("index"))

        csv_path = os.path.join(UPLOAD_CSV, csv_filename)

        # Rename certificates
        rename_certificates(csv_path, UPLOAD_CERTS, RENAMED_FOLDER)

        # Send emails (UPDATED CALL)
        sent_count, failed_count = send_certificates(
            csv_path,
            RENAMED_FOLDER,
            sender_email,
            sendgrid_api_key,
            subject,
            email_body,   # ✅ PASSED HERE
            LOG_FILE
        )

        # Store results for result page
        session["sent"] = sent_count
        session["failed"] = failed_count
        session["total"] = sent_count + failed_count

    except Exception as e:
        flash(f"❌ Error: {str(e)}", "danger")
        return redirect(url_for("index"))

    return redirect(url_for("preview_result"))

# ================= RUN =================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)

