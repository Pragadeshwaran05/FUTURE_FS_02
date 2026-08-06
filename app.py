from flask import Flask, render_template, request, redirect, session, flash
from werkzeug.security import check_password_hash
from flask import Flask, render_template, request, redirect, session, flash
from flask import send_file 
import zipfile
import os
from collections import Counter
import json
from bson import json_util
from mongodb import admin_collection, leads_collection
from bson import ObjectId

from bson import ObjectId
from datetime import datetime

from mongodb import (
    admin_collection,
    leads_collection,
    followups_collection,
    settings_collection,
    admin_profile_collection,
    activities_collection
)


app = Flask(__name__)
app.secret_key = "leadflow_secret_key"

# MongoDB Initialization

def add_activity(action, description, icon):

    activities_collection.insert_one({

        "action": action,

        "description": description,

        "icon": icon,

        "created_at": datetime.utcnow()

    })

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

        admin = admin_collection.find_one({"username": username})

        if admin and check_password_hash(admin["password"], password):

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

    # Total Leads
    total_leads = leads_collection.count_documents({})

    # New Leads
    new_leads = leads_collection.count_documents({
        "status": "New"
    })

    # Contacted Leads
    contacted = leads_collection.count_documents({
        "status": "Contacted"
    })

    # Converted Leads
    converted = leads_collection.count_documents({
        "status": "Converted"
    })
    activities = list(
    activities_collection.find()
    .sort("created_at", -1)
    .limit(5)
    )
    return render_template(
        "dashboard.html",
        total_leads=total_leads,
        new_leads=new_leads,
        contacted=contacted,
        converted=converted,
        activities=activities
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

    # Fetch all leads from MongoDB
    leads = list(
        leads_collection.find().sort("_id", -1)
    )

    return render_template(
        "leads.html",
        leads=leads
    )
@app.route("/lead/<id>")
def lead_details(id):

    if "admin" not in session:
        return redirect("/login")

    # Fetch lead from MongoDB
    lead = leads_collection.find_one(
        {"_id": ObjectId(id)}
    )

    # Fetch follow-up notes
    followups = list(
        followups_collection.find(
            {"lead_id": id}
        ).sort("created_at", -1)
    )

    return render_template(
        "lead_details.html",
        lead=lead,
        followups=followups
    )

@app.route("/edit-lead/<id>", methods=["GET", "POST"])
def edit_lead(id):

    if "admin" not in session:
        return redirect("/login")

    # Get lead from MongoDB
    lead = leads_collection.find_one({"_id": ObjectId(id)})
    old_status = lead["status"]
    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        phone = request.form["phone"]
        company = request.form["company"]
        status = request.form["status"]
        message = request.form["message"]

        leads_collection.update_one(
            {"_id": ObjectId(id)},
            {
                "$set": {
                    "name": name,
                    "email": email,
                    "phone": phone,
                    "company": company,
                    "status": status,
                    "message": message
                }
            }
        )
        add_activity(
    "Lead Updated",
    f"{name}'s details were updated.",
    "✏️"
)
        if old_status != "Converted" and status == "Converted":
              add_activity(
        "Lead Converted",
        f"{name} was converted into a customer.",
        "🎉"
            )
        return redirect(f"/lead/{id}")

    return render_template(
        "edit_lead.html",
        lead=lead
    )


@app.route("/delete-lead/<id>")
def delete_lead(id):

    if "admin" not in session:
        return redirect("/login")

    lead = leads_collection.find_one({"_id": ObjectId(id)})

    if lead:
        add_activity(
        "Lead Deleted",
        f"{lead['name']} was deleted.",
        "🗑️"
    )

    leads_collection.delete_one(
    {"_id": ObjectId(id)}
)
    return redirect("/leads")
# ===========================
# Run Flask
# ===========================
from datetime import datetime

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

        leads_collection.insert_one({

            "name": name,
            "email": email,
            "phone": phone,
            "company": company,
            "source": source,
            "service": service,
            "budget": budget,
            "status": status,
            "message": message,
            "created_at": datetime.utcnow()

        })
        add_activity(
    "Lead Added",
    f"{name} was added as a new lead.",
    "🟢"
    )
        return redirect("/leads")

    return render_template("add_lead.html")
from datetime import datetime

@app.route("/add-followup/<lead_id>", methods=["POST"])
def add_followup(lead_id):

    if "admin" not in session:
        return redirect("/login")

    note = request.form["note"]

    # Save follow-up in MongoDB
    followups_collection.insert_one({
        "lead_id": lead_id,
        "note": note,
        "created_at": datetime.utcnow()
    })
    lead = leads_collection.find_one({"_id": ObjectId(id)})

    add_activity(
    "Follow-up Added",
    f"A follow-up note was added for {lead['name']}.",
    "📝"
    )
    return redirect(f"/lead/{lead_id}")

from datetime import datetime

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

    leads_collection.insert_one({
    "name": name,
    "email": email,
    "phone": phone,
    "company": company,
    "service": service,
    "message": full_message,
    "status": "New",
    "created_at": datetime.utcnow()
})
    


    return redirect("thank-you")

@app.route("/update-status/<id>", methods=["POST"])
def update_status(id):

    if "admin" not in session:
        return redirect("/login")

    status = request.form["status"]

    leads_collection.update_one(
        {"_id": ObjectId(id)},
        {
            "$set": {
                "status": status
            }
        }
    )

    return redirect(f"/lead/{id}")
@app.route("/customers")
def customers():

    if "admin" not in session:
        return redirect("/login")

    # Fetch only converted leads from MongoDB
    customers = list(
        leads_collection.find(
            {"status": "Converted"}
        ).sort("created_at", -1)
    )

    return render_template(
        "customers.html",
        customers=customers
    )


from collections import Counter
from datetime import datetime

@app.route("/reports")
def reports():

    if "admin" not in session:
        return redirect("/login")

    # Get all leads from MongoDB
    leads = list(leads_collection.find())

    # ==========================
    # Dashboard Statistics
    # ==========================

    total_leads = len(leads)

    new_leads = sum(1 for lead in leads if lead.get("status") == "New")

    contacted = sum(
        1 for lead in leads
        if lead.get("status") == "Contacted"
    )

    followup = sum(
        1 for lead in leads
        if lead.get("status") == "Follow-up"
    )

    converted = sum(
        1 for lead in leads
        if lead.get("status") == "Converted"
    )

    # ==========================
    # Lead Sources
    # ==========================

    source_counter = Counter()

    for lead in leads:

        source = lead.get("source", "Unknown")

        source_counter[source] += 1

    labels = list(source_counter.keys())

    counts = list(source_counter.values())

    # ==========================
    # Monthly Lead Growth
    # ==========================

    months = [
        "Jan", "Feb", "Mar", "Apr", "May", "Jun",
        "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
    ]

    growth_labels = months

    growth_counts = [0] * 12

    for lead in leads:

        created = lead.get("created_at")

        if isinstance(created, datetime):

            growth_counts[created.month - 1] += 1

    # ==========================
    # Conversion Rate
    # ==========================

    if total_leads > 0:

        conversion_rate = round(
            (converted / total_leads) * 100,
            1
        )

    else:

        conversion_rate = 0

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

    # Save Changes
    if request.method == "POST":

        full_name = request.form["full_name"]
        email = request.form["email"]
        phone = request.form["phone"]

        admin_profile_collection.update_one(
            {"_id": 1},
            {
                "$set": {
                    "full_name": full_name,
                    "email": email,
                    "phone": phone
                }
            },
            upsert=True
        )

        flash("Profile updated successfully!", "success")

    # Load Profile
    admin = admin_profile_collection.find_one({"_id": 1})

    if admin is None:
        admin = {
            "_id": 1,
            "full_name": "",
            "email": "",
            "phone": ""
        }

    return render_template(
        "admin_profile.html",
        admin=admin
    )



from werkzeug.security import generate_password_hash, check_password_hash
from flask import request, redirect, render_template, session, flash, url_for

@app.context_processor
def inject_theme():

    settings = settings_collection.find_one({"_id": 1})

    theme = "dark"

    if settings:
        theme = settings.get("theme", "dark")

    return {"theme": theme}

@app.context_processor
def inject_admin():

    admin = admin_profile_collection.find_one({"_id": 1})

    if admin is None:

        admin = {
            "full_name": "Administrator",
            "email": "",
            "phone": ""
        }

    return dict(admin_profile=admin)
from werkzeug.security import generate_password_hash, check_password_hash


@app.route("/change-password", methods=["GET", "POST"])
def change_password():

    if "admin" not in session:
        return redirect("/login")

    if request.method == "POST":

        current_password = request.form["current_password"]
        new_password = request.form["new_password"]
        confirm_password = request.form["confirm_password"]

        # Get admin from MongoDB
        admin = admin_collection.find_one({"username": "admin"})

        # Check current password
        if not admin or not check_password_hash(admin["password"], current_password):
            flash("Current password is incorrect!", "error")
            return render_template("change_password.html")

        # Check new passwords match
        if new_password != confirm_password:
            flash("New passwords do not match!", "error")
            return render_template("change_password.html")

        # Update password in MongoDB
        new_password_hash = generate_password_hash(new_password)

        admin_collection.update_one(
            {"username": "admin"},
            {"$set": {"password": new_password_hash}}
        )

        flash("Password updated successfully!", "success")
        return redirect(url_for("change_password"))

    return render_template("change_password.html")
@app.route("/theme", methods=["GET", "POST"])
def theme():

    if "admin" not in session:
        return redirect("/login")

    if request.method == "POST":

        selected_theme = request.form["theme"]

        settings_collection.update_one(
            {"_id": 1},
            {
                "$set": {
                    "theme": selected_theme
                }
            },
            upsert=True
        )

        flash("Theme updated successfully!", "success")

    current_theme = settings_collection.find_one({"_id": 1})

    if current_theme is None:
        current_theme = {
            "_id": 1,
            "theme": "dark"
        }

    return render_template(
        "theme.html",
        current_theme=current_theme
    )
import json
from bson import json_util
from flask import send_file
import os

@app.route("/backup")
def backup_database():

    if "admin" not in session:
        return redirect("/login")

    backup = {

        "admin": list(admin_collection.find()),

        "admin_profile": list(admin_profile_collection.find()),

        "leads": list(leads_collection.find()),

        "followups": list(followups_collection.find()),

        "settings": list(settings_collection.find())

    }

    backup_file = "LeadFlow_Backup.json"

    with open(backup_file, "w") as file:

        file.write(json_util.dumps(backup, indent=4))

    return send_file(

        backup_file,

        as_attachment=True,

        download_name="LeadFlow_Backup.json",

        mimetype="application/json"

    )
@app.route("/thank-you")
def thank_you():
    return render_template("thank_you.html")

if __name__ == "__main__":
    app.run(debug=True)
