from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
import sqlite3
import os

app = Flask(__name__)

@app.before_request
def debug_request():
    print("=" * 60)
    print("METHOD:", request.method)
    print("PATH:", request.path)
    print("FORM KEYS:", list(request.form.keys()))
    print("FILE KEYS:", list(request.files.keys()))
    print("=" * 60)

print("=== RUNNING:", __file__)

import os

app.config["COMMITTEE_FOLDER"] = os.path.join(
    app.static_folder,
    "committee_photos"
)

os.makedirs(app.config["COMMITTEE_FOLDER"], exist_ok=True)



DATABASE = "festival.db"

GALLERY_FOLDER = "static/uploads"
os.makedirs(GALLERY_FOLDER, exist_ok=True)

COMMITTEE_FOLDER = "static/committee_photos"
os.makedirs(COMMITTEE_FOLDER, exist_ok=True)

app.config["GALLERY_FOLDER"] = GALLERY_FOLDER
app.config["COMMITTEE_FOLDER"] = COMMITTEE_FOLDER
app.config["UPLOAD_FOLDER"] = GALLERY_FOLDER

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp", "mp4", "mov", "avi", "mkv", "webm"}

def allowed_file(filename):
    return (
        "." in filename and
        filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )



def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# ---------------- HOME ----------------

@app.route("/")
def home():
    conn = get_db()

    announcements = conn.execute(
        "SELECT * FROM announcements ORDER BY id DESC"
    ).fetchall()

    conn.close()

    return render_template(
        "index.html",
        announcements=announcements
    )



@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/aim")
def aim():
    return render_template("aim.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


@app.route("/gallery")
def gallery():
    folder = app.config["UPLOAD_FOLDER"]

    files = []

    if os.path.exists(folder):
        files = sorted(os.listdir(folder), reverse=True)

    return render_template(
        "gallery.html",
        gallery_files=files
    )



@app.route("/events")
def events():
    conn = get_db()

    events = conn.execute(
        "SELECT * FROM events ORDER BY date ASC, time ASC"
    ).fetchall()

    conn.close()

    return render_template(
        "events.html",
        events=events
    )



@app.route("/committee")
def committee():
    conn = get_db()

    members = conn.execute(
        "SELECT * FROM committee ORDER BY id DESC"
    ).fetchall()

    conn.close()

    return render_template(
        "committee.html",
        members=members
    )



# ---------------- ADMIN LOGIN ----------------

@app.route("/admin")
def admin():
    return render_template("login.html")


@app.route("/login", methods=["POST"])
def login():

    username = request.form.get("username")
    password = request.form.get("password")

    if username == "rohith" and password == "Rohith@2026":
        return redirect(url_for("dashboard"))

    return "<h2>Invalid Username or Password</h2>"


# ---------------- EVENTS MANAGEMENT ----------------

@app.route("/manage_events")
def manage_events():
    conn = get_db()
    events = conn.execute(
        "SELECT * FROM events ORDER BY id DESC"
    ).fetchall()
    conn.close()
    return render_template("manage_events.html", events=events)


@app.route("/add_event", methods=["GET", "POST"])
def add_event():

    if request.method == "POST":

        receipt = request.files.get("receipt")

        if receipt and receipt.filename:
            receipt.save(
                os.path.join(
                    "static/donation_receipts",
                    receipt.filename
                )
            )
        event = request.form["event"]
        date = request.form["date"]
        time = request.form["time"]

        conn = get_db()
        conn.execute(
            "INSERT INTO events(event,date,time) VALUES(?,?,?)",
            (event, date, time),
        )
        conn.commit()
        conn.close()

        return redirect(url_for("manage_events"))

    return render_template("add_event.html")


@app.route("/edit_event/<int:id>", methods=["GET", "POST"])
def edit_event(id):

    conn = get_db()

    if request.method == "POST":
        event = request.form["event"]
        date = request.form["date"]
        time = request.form["time"]

        conn.execute(
            """
            UPDATE events
            SET event=?,date=?,time=?
            WHERE id=?
            """,
            (event, date, time, id),
        )

        conn.commit()
        conn.close()

        return redirect(url_for("manage_events"))

    event = conn.execute(
        "SELECT * FROM events WHERE id=?",
        (id,),
    ).fetchone()

    conn.close()

    return render_template("edit_event.html", event=event)


@app.route("/delete_event/<int:id>")
def delete_event(id):

    conn = get_db()

    conn.execute(
        "DELETE FROM events WHERE id=?",
        (id,),
    )

    conn.commit()
    conn.close()

    return redirect(url_for("manage_events"))


# ---------------- COMMITTEE MANAGEMENT ----------------

@app.route("/manage_committee")
def manage_committee():
    conn = get_db()
    members = conn.execute(
        "SELECT * FROM committee ORDER BY id DESC"
    ).fetchall()
    conn.close()
    return render_template("manage_committee.html", members=members)


@app.route("/add_committee", methods=["GET", "POST"])
def add_committee():

    if request.method == "POST":

        name = request.form["name"]
        designation = request.form["designation"]
        mobile = request.form["mobile"]

        photo = request.files.get("photo")
        filename = ""

        if photo and photo.filename:
            filename = secure_filename(photo.filename)
            photo.save(os.path.join("static", "committee_photos", filename))

        conn = get_db()

        conn.execute(
            """
            INSERT INTO committee(name,designation,mobile,photo)
            VALUES(?,?,?,?)
            """,
            (name, designation, mobile, filename),
        )

        conn.commit()
        conn.close()

        return redirect(url_for("manage_committee"))

    return redirect(url_for("manage_committee"))


@app.route("/edit_committee/<int:id>", methods=["GET", "POST"])
def edit_committee(id):

    conn = get_db()

    if request.method == "POST":
        name = request.form["name"]
        designation = request.form["designation"]
        mobile = request.form["mobile"]

        conn.execute(
            """
            UPDATE committee
            SET name=?, designation=?, mobile=?
            WHERE id=?
            """,
            (name, designation, mobile, id),
        )

        conn.commit()
        conn.close()

        return redirect(url_for("manage_committee"))

    member = conn.execute(
        "SELECT * FROM committee WHERE id=?",
        (id,),
    ).fetchone()

    conn.close()

    return render_template("edit_committee.html", member=member)


@app.route("/delete_committee/<int:id>")
def delete_committee(id):

    conn = get_db()

    conn.execute(
        "DELETE FROM committee WHERE id=?",
        (id,),
    )

    conn.commit()
    conn.close()

    return redirect(url_for("manage_committee"))


@app.route("/change_committee_photo/<int:id>", methods=["GET", "POST"])
def change_committee_photo(id):

    conn = get_db()

    if request.method == "POST":

        photo = request.files.get("photo")

        if photo and photo.filename:

            filename = secure_filename(photo.filename)

            photo.save(os.path.join("static", "committee_photos", filename))

            conn.execute(
                "UPDATE committee SET photo=? WHERE id=?",
                (filename, id),
            )

            conn.commit()

        conn.close()

        return redirect(url_for("manage_committee"))

    member = conn.execute(
        "SELECT * FROM committee WHERE id=?",
        (id,),
    ).fetchone()

    conn.close()

    return render_template("change_committee_photo.html", member=member)


@app.route("/logout")
def logout():
    return redirect(url_for("home"))



@app.route("/dashboard")
def dashboard():

    conn = get_db()

    total_events = conn.execute("SELECT COUNT(*) FROM events").fetchone()[0]

    total_committee = conn.execute("SELECT COUNT(*) FROM committee").fetchone()[0]

    total_announcements = conn.execute("SELECT COUNT(*) FROM announcements").fetchone()[0]

    total_donations = conn.execute("SELECT COUNT(*) FROM donations").fetchone()[0]

    total_tshirts = conn.execute("SELECT COUNT(*) FROM tshirt_registration").fetchone()[0]

    conn.close()

    return render_template(
        "dashboard.html",
        total_events=total_events,
        total_committee=total_committee,
        total_announcements=total_announcements,
        total_donations=total_donations,
        total_tshirts=total_tshirts
    )




# ---------------- ANNOUNCEMENTS ----------------

@app.route("/announcements")
def announcements():

    conn = get_db()

    announcements = conn.execute(
        "SELECT * FROM announcements ORDER BY id DESC"
    ).fetchall()

    conn.close()

    return render_template(
        "announcements.html",
        announcements=announcements
    )


@app.route("/manage_announcements")
def manage_announcements():

    conn = get_db()

    announcements = conn.execute(
        "SELECT * FROM announcements ORDER BY id DESC"
    ).fetchall()

    conn.close()

    return render_template(
        "manage_announcements.html",
        announcements=announcements
    )


@app.route("/add_announcement", methods=["POST"])
def add_announcement():

    title = request.form["title"]
    message = request.form["message"]

    from datetime import datetime

    created_at = datetime.now().strftime("%d-%m-%Y %H:%M")

    conn = get_db()

    conn.execute(
        """
        INSERT INTO announcements(title,message,created_at)
        VALUES(?,?,?)
        """,
        (title, message, created_at),
    )

    conn.commit()
    conn.close()

    return redirect(url_for("manage_announcements"))


@app.route("/delete_announcement/<int:id>")
def delete_announcement(id):

    conn = get_db()

    conn.execute(
        "DELETE FROM announcements WHERE id=?",
        (id,),
    )

    conn.commit()
    conn.close()

    return redirect(url_for("manage_announcements"))

# ---------------- DONATIONS ----------------

@app.route("/donation", methods=["GET", "POST"])
def donation():

    if request.method == "POST":

        receipt = request.files.get("receipt")
        receipt_name = ""

        if receipt and receipt.filename:
            from werkzeug.utils import secure_filename
            receipt_name = secure_filename(receipt.filename)
            receipt.save(os.path.join("static/donation_receipts", receipt_name))

        conn = get_db()

        conn.execute(
            """
            INSERT INTO donations
            (name,mobile,amount,payment_mode,transaction_id,donation_date,receipt)
            VALUES(?,?,?,?,?,datetime('now'),?)
            """,
            (
                request.form["name"],
                request.form["mobile"],
                request.form["amount"],
                request.form.get("payment_mode","UPI"),
                request.form.get("transaction_id",""),
                receipt_name,
            ),
        )

        conn.commit()
        conn.close()

        return render_template("donation_success.html")

    return render_template("donation.html")


@app.route("/donation_admin")
def donation_admin():

    conn = get_db()

    donations = conn.execute(
        "SELECT * FROM donations ORDER BY id DESC"
    ).fetchall()

    total_amount = conn.execute(
        "SELECT COALESCE(SUM(amount),0) FROM donations"
    ).fetchone()[0]

    conn.close()

    return render_template("donation_admin.html", donations=donations, total_amount=total_amount)


@app.route("/delete_donation/<int:id>")
def delete_donation(id):

    conn = get_db()
    conn.execute("DELETE FROM donations WHERE id=?", (id,))
    conn.commit()
    conn.close()

    return redirect(url_for("donation_admin"))


# ---------------- TSHIRT ----------------

@app.route("/tshirt", methods=["GET","POST"])
def tshirt():

    if request.method == "POST":

        from werkzeug.utils import secure_filename
        import os

        screenshot = request.files.get("screenshot")
        screenshot_name = ""

        if screenshot and screenshot.filename:
            screenshot_name = secure_filename(screenshot.filename)
            screenshot.save(
                os.path.join(app.config["UPLOAD_FOLDER"], screenshot_name)
            )

        conn = get_db()

        conn.execute(
            "INSERT INTO tshirt_registration(name,mobile,tshirt_size,quantity,address) VALUES(?,?,?,?,?)",
            (
                request.form["name"],
                request.form["mobile"],
                request.form["tshirt_size"],
                request.form["quantity"],
                request.form.get("address", ""),
            ),
        )

        conn.commit()
        conn.close()

        return render_template("tshirt_success.html")

    return render_template("tshirt.html")


@app.route("/tshirt_admin")
def tshirt_admin():

    conn = get_db()

    registrations = conn.execute(
        "SELECT * FROM tshirt_registration ORDER BY id DESC"
    ).fetchall()

    conn.close()

    return render_template("tshirt_admin.html", registrations=registrations)


@app.route("/delete_tshirt/<int:id>")
def delete_tshirt(id):

    conn = get_db()
    conn.execute("DELETE FROM tshirt_registration WHERE id=?", (id,))
    conn.commit()
    conn.close()

    return redirect(url_for("tshirt_admin"))




# ---------------- GALLERY MANAGEMENT ----------------

@app.route("/manage_gallery")
def manage_gallery():

    folder = app.config["UPLOAD_FOLDER"]

    files = []

    if os.path.exists(folder):
        files = sorted(os.listdir(folder), reverse=True)

    return render_template(
        "manage_gallery.html",
        gallery_files=files
    )


@app.route("/upload_gallery", methods=["POST"])
def upload_gallery():

    print("FORM:", request.form)
    print("FILES:", list(request.files.keys()))

    if "file" not in request.files:
        return "No file field received", 400

    files = request.files.getlist("file")

    print("TOTAL FILES:", len(files))

    for file in files:
        if file and file.filename:
            filename = secure_filename(file.filename)
            file.save(
                os.path.join(
                    app.config["UPLOAD_FOLDER"],
                    filename
                )
            )

    return redirect(url_for("manage_gallery"))


@app.route("/delete_gallery/<filename>")
def delete_gallery(filename):

    path = os.path.join(
        app.config["UPLOAD_FOLDER"],
        filename
    )

    if os.path.exists(path):
        os.remove(path)

    return redirect(url_for("manage_gallery"))




@app.route("/upload_image", methods=["POST"])
def upload_image():

    file = request.files.get("file")

    if file and file.filename:
        filename = secure_filename(file.filename)

        file.save(
            os.path.join(
                app.config["UPLOAD_FOLDER"],
                filename
            )
        )

    return redirect(url_for("manage_gallery"))





# -------- RESTORE OLD ADMIN ACTION ROUTES --------


@app.route("/save_committee", methods=["POST"])
def save_committee():

    name = request.form["name"]
    designation = request.form["designation"]
    mobile = request.form["mobile"]

    photo = request.files.get("photo")
    filename = ""

    if photo and photo.filename:
        filename = secure_filename(photo.filename)
        photo.save(
            os.path.join(
                app.config["COMMITTEE_FOLDER"],
                filename
            )
        )

    conn = get_db()

    conn.execute(
        """
        INSERT INTO committee(name,designation,mobile,photo)
        VALUES(?,?,?,?)
        """,
        (name, designation, mobile, filename)
    )

    conn.commit()
    conn.close()

    return redirect(url_for("manage_committee"))



@app.route("/save_event", methods=["POST"])
def save_event():

    event = request.form["event"]
    date = request.form["date"]
    time = request.form["time"]

    conn = get_db()

    conn.execute(
        """
        INSERT INTO events(event,date,time)
        VALUES(?,?,?)
        """,
        (event, date, time)
    )

    conn.commit()
    conn.close()

    return redirect(url_for("manage_events"))



@app.route("/upload", methods=["POST"])
def upload():

    file = request.files.get("file")

    if file and file.filename:
        filename = secure_filename(file.filename)

        file.save(
            os.path.join(
                app.config["UPLOAD_FOLDER"],
                filename
            )
        )

    return redirect(url_for("manage_gallery"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
