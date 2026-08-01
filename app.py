from flask import Flask, render_template, request, redirect, session, flash
import sqlite3
from werkzeug.security import check_password_hash
from flask import Flask, render_template, request, redirect, session, flash
from database import create_tables
from auth import create_admin
from flask import send_file 
import zipfile
import os
DATABASE = "leadflow.db"

app = Flask(__name__)
app.secret_key = "leadflow_secret_key"

# Create database and default admin
create_tables()
create_admin()


# ===========================
# Home Page
# ===========================
@app.route("/")
def home():
    return render_template("index.html")


# ===========================
# Login
# ===========================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM admin WHERE username=?",
            (username,)
        )

        admin = cursor.fetchone()

        conn.close()

        if admin and check_password_hash(admin[2], password):

            session["admin"] = username

            return redirect("/dashboard")

        flash("Invalid Username or Password")

    return render_template("login.html")


# ===========================
# Dashboard
# ===========================
@app.route("/dashboard")
def dashboard():

    if "admin" not in session:
        return redirect("/login")

    conn = sqlite3.connect("leadflow.db")
    cursor = conn.cursor()

    # Total Leads
    cursor.execute("SELECT COUNT(*) FROM leads")
    total_leads = cursor.fetchone()[0]

    # New Leads
    cursor.execute("SELECT COUNT(*) FROM leads WHERE status='New'")
    new_leads = cursor.fetchone()[0]

    # Contacted
    cursor.execute("SELECT COUNT(*) FROM leads WHERE status='Contacted'")
    contacted = cursor.fetchone()[0]

    # Converted
    cursor.execute("SELECT COUNT(*) FROM leads WHERE status='Converted'")
    converted = cursor.fetchone()[0]

    conn.close()

    return render_template(
        "dashboard.html",
        total_leads=total_leads,
        new_leads=new_leads,
        contacted=contacted,
        converted=converted
    )

# ===========================
# Logout
# ===========================
@app.route("/logout")
def logout():

    session.pop("admin", None)

    return redirect("/")

@app.route("/leads")
def leads():

    if "admin" not in session:
        return redirect("/login")

    conn = sqlite3.connect("leadflow.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM leads ORDER BY id DESC")

    leads = cursor.fetchall()

    conn.close()

    return render_template("leads.html", leads=leads)

@app.route("/lead/<int:id>")
def lead_details(id):

    if "admin" not in session:
        return redirect("/login")

    conn = sqlite3.connect("leadflow.db")
    cursor = conn.cursor()

    # Fetch Lead Details
    cursor.execute("SELECT * FROM leads WHERE id=?", (id,))
    lead = cursor.fetchone()

    # Fetch Follow-up Notes
    cursor.execute("""
        SELECT * FROM followups
        WHERE lead_id=?
        ORDER BY created_at DESC
    """, (id,))

    followups = cursor.fetchall()

    conn.close()

    return render_template(
        "lead_details.html",
        lead=lead,
        followups=followups
    )

@app.route("/edit-lead/<int:id>", methods=["GET", "POST"])
def edit_lead(id):

    if "admin" not in session:
        return redirect("/login")

    conn = sqlite3.connect("leadflow.db")
    cursor = conn.cursor()

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        phone = request.form["phone"]
        company = request.form["company"]
        status = request.form["status"]
        message = request.form["message"]

        cursor.execute("""
            UPDATE leads
            SET
                name=?,
                email=?,
                phone=?,
                company=?,
                status=?,
                message=?
            WHERE id=?
        """, (
            name,
            email,
            phone,
            company,
            status,
            message,
            id
        ))
        # ==========================
# Theme Settings
# ==========================

        cursor.execute("""
CREATE TABLE IF NOT EXISTS settings(

    id INTEGER PRIMARY KEY,

    theme TEXT

)
""")

        cursor.execute("""
INSERT OR IGNORE INTO settings(
    id,
    theme
)
VALUES(
    1,
    'dark'
)
""")


        
        conn.commit()
        conn.close()

        return redirect(f"/lead/{id}")

    cursor.execute("SELECT * FROM leads WHERE id=?", (id,))
    lead = cursor.fetchone()

    conn.close()

    return render_template(
        "edit_lead.html",
        lead=lead
    )

@app.route("/delete-lead/<int:id>")
def delete_lead(id):

    if "admin" not in session:
        return redirect("/login")

    conn = sqlite3.connect("leadflow.db")

    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM leads WHERE id=?",
        (id,)
    )

    conn.commit()

    conn.close()

    return redirect("/leads")
# ===========================
# Run Flask
# ===========================
@app.route("/add-lead", methods=["GET", "POST"])
def add_lead():

    if "admin" not in session:
        return redirect("/login")

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        phone = request.form["phone"]
        company = request.form["company"]
        source = request.form["source"]
        service = request.form["service"]
        budget = request.form["budget"]
        status = request.form["status"]
        message = request.form["message"]

        conn = sqlite3.connect("leadflow.db")
        cursor = conn.cursor()

        cursor.execute("""
INSERT INTO leads
(name, email, phone, company, service, budget, source, status, message)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
""", (
    name,
    email,
    phone,
    company,
    service,
    budget,
    source,
    status,
    message
))

        conn.commit()
        conn.close()

        return redirect("/leads")

    return render_template("add_lead.html")

@app.route("/add-followup/<int:lead_id>", methods=["POST"])
def add_followup(lead_id):

    if "admin" not in session:
        return redirect("/login")

    note = request.form["note"]

    conn = sqlite3.connect("leadflow.db")
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO followups (lead_id, note)
        VALUES (?, ?)
    """, (lead_id, note))

    conn.commit()
    conn.close()

    return redirect(f"/lead/{lead_id}")


@app.route("/contact", methods=["POST"])
def contact():

    name = request.form["name"]
    email = request.form["email"]
    phone = request.form["phone"]
    company = request.form["company"]
    service = request.form["service"]
    message = request.form["message"]

    full_message = f"""
Service Required : {service}

Project Details :

{message}
"""

    conn = sqlite3.connect("leadflow.db")
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO leads
        (name,email,phone,company,message,status)
        VALUES (?,?,?,?,?,?)
    """,
    (
        name,
        email,
        phone,
        company,
        full_message,
        "New"
    ))

    conn.commit()
    conn.close()


    return redirect("thank-you")

@app.route("/update-status/<int:id>", methods=["POST"])
def update_status(id):

    if "admin" not in session:
        return redirect("/login")

    status = request.form["status"]

    conn = sqlite3.connect("leadflow.db")
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE leads SET status=? WHERE id=?",
        (status, id)
    )

    conn.commit()
    conn.close()

    return redirect(f"/lead/{id}")

@app.route("/customers")
def customers():

    if "admin" not in session:
        return redirect("/login")

    conn = sqlite3.connect("leadflow.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM leads
        WHERE status = 'Converted'
        ORDER BY created_at DESC
    """)

    customers = cursor.fetchall()

    conn.close()

    return render_template(
        "customers.html",
        customers=customers
    )
@app.route("/reports")
def reports():

    if "admin" not in session:
        return redirect("/login")

    conn = sqlite3.connect("leadflow.db")
    cursor = conn.cursor()

    # ==========================
    # Dashboard Statistics
    # ==========================

    cursor.execute("SELECT COUNT(*) FROM leads")
    total_leads = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM leads WHERE status='New'")
    new_leads = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM leads WHERE status='Contacted'")
    contacted = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM leads WHERE status='Follow-up'")
    followup = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM leads WHERE status='Converted'")
    converted = cursor.fetchone()[0]

    # ==========================
    # Lead Sources
    # ==========================

    cursor.execute("""
        SELECT source, COUNT(*)
        FROM leads
        GROUP BY source
    """)

    source_data = cursor.fetchall()

    labels = []
    counts = []

    for row in source_data:
        labels.append(row[0])
        counts.append(row[1])

    # ==========================
    # ==========================
# Monthly Lead Growth
# ==========================

    cursor.execute("""
SELECT
    strftime('%m', created_at) AS month,
    COUNT(*)
FROM leads
GROUP BY month
ORDER BY month
""")

    monthly_data = cursor.fetchall()

    months = [
    "Jan", "Feb", "Mar", "Apr", "May", "Jun",
    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
]

# Show all months initially with 0 leads
    growth_labels = months
    growth_counts = [0] * 12

# Update only the months that have data
    for month, count in monthly_data:
      month_index = int(month) - 1
      growth_counts[month_index] = count
    # ==========================
    # Conversion Rate
    # ==========================

    if total_leads > 0:
        conversion_rate = round((converted / total_leads) * 100, 1)
    else:
        conversion_rate = 0

    conn.close()

    return render_template(
        "reports.html",
        total_leads=total_leads,
        new_leads=new_leads,
        contacted=contacted,
        followup=followup,
        converted=converted,
        source_labels=labels,
        source_counts=counts,
        conversion_rate=conversion_rate,
        growth_labels=growth_labels,
        growth_counts=growth_counts
    )


@app.route("/settings")
def settings():

    if "admin" not in session:
        return redirect("/login")

    return render_template("settings.html")

@app.route("/admin-profile", methods=["GET", "POST"])
def admin_profile():

    if "admin" not in session:
        return redirect("/login")

    conn = sqlite3.connect("leadflow.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Save Changes
    if request.method == "POST":

        full_name = request.form["full_name"]
        email = request.form["email"]
        phone = request.form["phone"]

        cursor.execute("""
        UPDATE admin_profile
        SET
            full_name=?,
            email=?,
            phone=?
        WHERE id=1
        """, (full_name, email, phone))

        conn.commit()

        flash("Profile updated successfully!", "success")

    # Load Profile
    cursor.execute("SELECT * FROM admin_profile WHERE id=1")
    admin = cursor.fetchone()

    conn.close()

    return render_template(
        "admin_profile.html",
        admin=admin
    )
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from flask import request, redirect, render_template, session, flash, url_for
def create_tables():

    conn = sqlite3.connect("leadflow.db")
    cursor = conn.cursor()

    # ==========================
    # Admin Login Table
    # ==========================

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS admin(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        username TEXT UNIQUE NOT NULL,

        password TEXT NOT NULL

    )
    """)

    # Default Admin
    cursor.execute("""
    INSERT OR IGNORE INTO admin(id, username, password)
    VALUES(1, 'admin', ?)
    """, (generate_password_hash("admin123"),))

    # ==========================
    # Leads Table
    # ==========================

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS leads(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        name TEXT,

        email TEXT,

        phone TEXT,

        company TEXT,

        source TEXT,

        service TEXT,

        budget TEXT,

        message TEXT,

        status TEXT DEFAULT 'New',

        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

    )
    """)

    # ==========================
    # Notes Table
    # ==========================

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS notes(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        lead_id INTEGER,

        note TEXT,

        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

        FOREIGN KEY(lead_id) REFERENCES leads(id)

    )
    """)

    # ==========================
    # Follow-up Table
    # ==========================

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS followups(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        lead_id INTEGER,

        note TEXT,

        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

        FOREIGN KEY(lead_id) REFERENCES leads(id)

    )
    """)

    # ==========================
    # Admin Profile
    # ==========================

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS admin_profile(

        id INTEGER PRIMARY KEY,

        full_name TEXT,

        email TEXT,

        phone TEXT

    )
    """)

    # Default Profile
    cursor.execute("""
    INSERT OR IGNORE INTO admin_profile(

        id,
        full_name,
        email,
        phone

    )

    VALUES(

        1,

        'Administrator',

        'admin@example.com',

        '+91 XXXXX XXXXX'

    )
    """)

    conn.commit()
    conn.close()
@app.context_processor
def inject_theme():

    conn = sqlite3.connect("leadflow.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT theme FROM settings WHERE id=1")
    data = cursor.fetchone()

    conn.close()

    theme = data["theme"] if data else "dark"

    return {"theme": theme}
@app.context_processor
def inject_admin():

    conn = sqlite3.connect("leadflow.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM admin_profile WHERE id=1")
    admin = cursor.fetchone()

    conn.close()

    return dict(admin_profile=admin)

@app.route("/change-password", methods=["GET", "POST"])
def change_password():

    if "admin" not in session:
        return redirect("/login")

    if request.method == "POST":

        current_password = request.form["current_password"]
        new_password = request.form["new_password"]
        confirm_password = request.form["confirm_password"]

        conn = sqlite3.connect("leadflow.db")
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM admin WHERE username='admin'")
        admin = cursor.fetchone()

        # Check current password
        if not check_password_hash(admin["password"], current_password):
            flash("Current password is incorrect!", "error")
            conn.close()
            return render_template("change_password.html")

        # Check new passwords match
        if new_password != confirm_password:
            flash("New passwords do not match!", "error")
            conn.close()
            return render_template("change_password.html")

        # Update password
        new_password_hash = generate_password_hash(new_password)

        cursor.execute("""
            UPDATE admin
            SET password=?
            WHERE username='admin'
        """, (new_password_hash,))

        conn.commit()
        conn.close()

        flash("Password updated successfully!", "success")
        return redirect(url_for("change_password"))

    return render_template("change_password.html")


@app.route("/theme", methods=["GET", "POST"])
def theme():

    if "admin" not in session:
        return redirect("/login")

    conn = sqlite3.connect("leadflow.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    if request.method == "POST":

        selected_theme = request.form["theme"]

        cursor.execute("""
        UPDATE settings
        SET theme=?
        WHERE id=1
        """, (selected_theme,))

        conn.commit()

        flash("Theme updated successfully!", "success")

    cursor.execute("SELECT * FROM settings WHERE id=1")
    current_theme = cursor.fetchone()

    conn.close()

    return render_template(
        "theme.html",
        current_theme=current_theme
    )
@app.route("/backup")
def backup_database():

    if "admin" not in session:
        return redirect("/login")

    zip_filename = "LeadFlow_Backup.zip"

    with zipfile.ZipFile(zip_filename, "w", zipfile.ZIP_DEFLATED) as backup_zip:

        backup_zip.write("leadflow.db")
        
    return send_file(
        zip_filename,
        as_attachment=True,
        download_name="LeadFlow_Backup.zip"
    )

@app.route("/thank-you")
def thank_you():
    return render_template("thank_you.html")

if __name__ == "__main__":
    app.run(debug=True)
