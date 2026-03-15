from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from supabase import create_client, Client
from dotenv import load_dotenv

# ─── Load Environment Variables ───────────────────────────────────────────────
load_dotenv()

# ─── Flask App ────────────────────────────────────────────────────────────────
app = Flask(__name__, static_folder="static", template_folder="templates")
app.secret_key = os.environ.get("SECRET_KEY", "mentor-portal-secret")

CORS(app)

# ─── Supabase Configuration ───────────────────────────────────────────────────
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_ANON_KEY = os.environ.get("SUPABASE_ANON_KEY")

if not SUPABASE_URL or not SUPABASE_ANON_KEY:
    raise RuntimeError("SUPABASE_URL and SUPABASE_ANON_KEY must be set")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

# ─── Email Configuration ──────────────────────────────────────────────────────
EMAIL_USER = os.environ.get("EMAIL")
EMAIL_PASS = os.environ.get("EMAIL_PASSWORD")


def send_email(to, subject, body):
    if not EMAIL_USER or not EMAIL_PASS:
        raise Exception("Email credentials not configured")

    msg = MIMEMultipart()
    msg["From"] = EMAIL_USER
    msg["To"] = to
    msg["Subject"] = subject

    msg.attach(MIMEText(body, "plain"))

    with smtplib.SMTP("smtp.gmail.com", 587, timeout=15) as server:
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASS)
        server.sendmail(EMAIL_USER, to, msg.as_string())


# ─── Auth Helpers ─────────────────────────────────────────────────────────────
def get_token():
    auth = request.headers.get("Authorization", "")
    return auth.replace("Bearer ", "").strip()


def get_client_with_token(token):
    from supabase.client import ClientOptions

    return create_client(
        SUPABASE_URL,
        SUPABASE_ANON_KEY,
        options=ClientOptions(headers={"Authorization": f"Bearer {token}"})
    )


# ─── Main Page ────────────────────────────────────────────────────────────────
@app.route("/")
def index():
    return render_template("index.html")


# ─── Authentication API ───────────────────────────────────────────────────────
@app.route("/api/auth/signup", methods=["POST"])
def signup():
    data = request.get_json() or {}

    email = data.get("email", "").strip()
    password = data.get("password", "")
    full_name = data.get("full_name", "").strip()

    if not all([email, password, full_name]):
        return jsonify({"error": "All fields required"}), 400

    try:
        res = supabase.auth.sign_up({"email": email, "password": password})

        if res.user:
            supabase.table("mentors").insert({
                "id": res.user.id,
                "email": email,
                "full_name": full_name
            }).execute()

            return jsonify({
                "user": {"id": res.user.id, "email": email},
                "access_token": res.session.access_token if res.session else None,
                "full_name": full_name
            })

        return jsonify({"error": "Signup failed"}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route("/api/auth/signin", methods=["POST"])
def signin():
    data = request.get_json() or {}

    email = data.get("email")
    password = data.get("password")

    try:
        res = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })

        if res.user and res.session:

            mentor = supabase.table("mentors") \
                .select("*") \
                .eq("id", res.user.id) \
                .maybe_single() \
                .execute()

            return jsonify({
                "user": {"id": res.user.id, "email": res.user.email},
                "access_token": res.session.access_token,
                "full_name": mentor.data["full_name"] if mentor.data else email
            })

        return jsonify({"error": "Invalid credentials"}), 401

    except Exception as e:
        return jsonify({"error": str(e)}), 401


# ─── Students API ─────────────────────────────────────────────────────────────
@app.route("/api/students", methods=["GET"])
def get_students():

    token = get_token()

    try:
        client = get_client_with_token(token)

        res = client.table("students") \
            .select("*") \
            .order("created_at", desc=True) \
            .execute()

        return jsonify(res.data or [])

    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route("/api/students", methods=["POST"])
def add_student():

    token = get_token()
    data = request.get_json() or {}

    try:
        client = get_client_with_token(token)

        user = client.auth.get_user(token)

        data["mentor_id"] = user.user.id
        data["cgpa"] = float(data.get("cgpa") or 0)
        data["gpa"] = float(data.get("gpa") or 0)

        res = client.table("students").insert(data).execute()

        return jsonify(res.data[0]), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route("/api/students/<student_id>", methods=["PUT"])
def update_student(student_id):

    token = get_token()
    data = request.get_json() or {}

    try:
        client = get_client_with_token(token)

        data["cgpa"] = float(data.get("cgpa") or 0)
        data["gpa"] = float(data.get("gpa") or 0)

        res = client.table("students") \
            .update(data) \
            .eq("id", student_id) \
            .execute()

        return jsonify(res.data[0])

    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route("/api/students/<student_id>", methods=["DELETE"])
def delete_student(student_id):

    token = get_token()

    try:
        client = get_client_with_token(token)

        client.table("students") \
            .delete() \
            .eq("id", student_id) \
            .execute()

        return jsonify({"success": True})

    except Exception as e:
        return jsonify({"error": str(e)}), 400


# ─── Stats API ────────────────────────────────────────────────────────────────
@app.route("/api/stats")
def stats():

    token = get_token()

    try:
        client = get_client_with_token(token)

        res = client.table("students").select("*").execute()

        students = res.data or []

        return jsonify({
            "totalStudents": len(students),
            "studentsWithArrears": len([s for s in students if (s.get("arrears_details") or "").strip()]),
            "lowCGPAStudents": len([s for s in students if float(s.get("cgpa") or 0) < 7]),
            "scholarshipStudents": len([s for s in students if (s.get("scholarship_details") or "").strip()])
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 400


# ─── Email Announcement ───────────────────────────────────────────────────────
@app.route("/api/announcement", methods=["POST"])
def send_announcement():

    try:

        data = request.get_json() or {}
        message = data.get("message", "").strip()

        if not message:
            return jsonify({"error": "Message required"}), 400

        token = get_token()
        client = get_client_with_token(token)

        res = client.table("students").select("email, student_name").execute()
        students = res.data or []

        sent = 0
        errors = []

        for student in students:
            try:

                send_email(
                    student["email"],
                    "New Announcement",
                    f"Dear {student['student_name']},\n\n{message}"
                )

                sent += 1

            except Exception as e:
                errors.append(str(e))

        return jsonify({
            "sent": sent,
            "total": len(students),
            "errors": errors
        })

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500

# ─── Health Check ─────────────────────────────────────────────────────────────
@app.route("/health")
def health():
    return jsonify({"status": "ok"})


# ─── Run App ──────────────────────────────────────────────────────────────────
if __name__ == "__main__":

    port = int(os.environ.get("PORT", 5000))

    app.run(
        host="0.0.0.0",
        port=port
    )
