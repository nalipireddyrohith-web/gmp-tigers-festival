from flask import Flask, render_template, request, redirect, url_for
import psycopg
from psycopg.rows import dict_row
import os

app = Flask(__name__)

with app.app_context():
    init_db()


DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/gmp_tigers"
)

print("DATABASE_URL =", DATABASE_URL.split("@")[-1])

UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


def get_db():
    return psycopg.connect(
        DATABASE_URL,
        row_factory=dict_row,
        autocommit=False
    )


def init_db():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS events(
        id SERIAL PRIMARY KEY,
        event TEXT,
        date TEXT,
        time TEXT
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS committee(
        id SERIAL PRIMARY KEY,
        name TEXT,
        designation TEXT,
        mobile TEXT,
        photo TEXT
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS announcements(
        id SERIAL PRIMARY KEY,
        title TEXT,
        message TEXT,
        created_at TEXT
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS donations(
        id SERIAL PRIMARY KEY,
        name TEXT,
        mobile TEXT,
        amount NUMERIC,
        payment_mode TEXT,
        transaction_id TEXT,
        donation_date TEXT,
        receipt TEXT
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS tshirt_registration(
        id SERIAL PRIMARY KEY,
        name TEXT,
        mobile TEXT,
        tshirt_size TEXT,
        quantity INTEGER,
        address TEXT
    );
    """)

    conn.commit()
    cur.close()
    conn.close()


# ---------------- HOME ----------------

@app.route("/")
def home():
    return render_template("index.html")


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
    return render_template("gallery.html")


@app.route("/events")
def events():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM events ORDER BY id DESC")
    data = cur.fetchall()
    cur.close()
    conn.close()
    return render_template("events.html", events=data)


@app.route("/committee")
def committee():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM committee ORDER BY id DESC")
    data = cur.fetchall()
    cur.close()
    conn.close()
    return render_template("committee.html", members=data)


# ---------------- ADMIN LOGIN ----------------

@app.route("/admin")
def admin():
    return render_template("login.html")


@app.route("/login", methods=["POST"])
def login():

    username = request.form.get("username")
    password = request.form.get("password")

    if username == "admin" and password == "gmp123":
        return redirect(url_for("dashboard"))

    return "<h2>Invalid Username or Password</h2>"


# ---------------- EVENTS MANAGEMENT ----------------

@app.route("/manage_events")
def manage_events():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM events ORDER BY id DESC")
    events = cur.fetchall()
    cur.close()
    conn.close()
    return render_template("manage_events.html", events=events)


@app.route("/add_event", methods=["GET", "POST"])
def add_event():

    if request.method == "POST":
        event = request.form["event"]
        date = request.form["date"]
        time = request.form["time"]

        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO events(event,date,time) VALUES(%s,%s,%s)",
            (event, date, time),
        )
        conn.commit()
        cur.close()
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

        cur = conn.cursor()
        cur.execute(
            """
            UPDATE events
            SET event=%s,date=%s,time=%s
            WHERE id=%s
            """,
            (event, date, time, id),
        )

        conn.commit()
        cur.close()
        conn.close()

        return redirect(url_for("manage_events"))

    cur = conn.cursor()
    cur.execute(
        "SELECT * FROM events WHERE id=%s",
        (id,),
    )
    event = cur.fetchone()

    cur.close()
    conn.close()

    return render_template("edit_event.html", event=event)


@app.route("/delete_event/<int:id>")
def delete_event(id):

    conn = get_db()

    cur = conn.cursor()
    cur.execute(
        "DELETE FROM events WHERE id=%s",
        (id,),
    )

    conn.commit()
    cur.close()
    conn.close()

    return redirect(url_for("manage_events"))


# ---------------- COMMITTEE MANAGEMENT ----------------

@app.route("/manage_committee")
def manage_committee():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM committee ORDER BY id DESC")
    members = cur.fetchall()
    cur.close()
    conn.close()
    return render_template("manage_committee.html", members=members)


@app.route("/add_committee", methods=["GET", "POST"])
def add_committee():

    if request.method == "POST":
        name = request.form["name"]
        designation = request.form["designation"]
        mobile = request.form["mobile"]

        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO committee(name,designation,mobile)
            VALUES(%s,%s,%s)
            """,
            (name, designation, mobile),
        )
        conn.commit()
        cur.close()
        conn.close()

        return redirect(url_for("manage_committee"))

    return render_template("edit_committee.html")


@app.route("/edit_committee/<int:id>", methods=["GET", "POST"])
def edit_committee(id):

    conn = get_db()

    if request.method == "POST":
        name = request.form["name"]
        designation = request.form["designation"]
        mobile = request.form["mobile"]

        cur = conn.cursor()
        cur.execute(
            """
            UPDATE committee
            SET name=%s, designation=%s, mobile=%s
            WHERE id=%s
            """,
            (name, designation, mobile, id),
        )

        conn.commit()
        cur.close()
        conn.close()

        return redirect(url_for("manage_committee"))

    cur = conn.cursor()
    cur.execute(
        "SELECT * FROM committee WHERE id=%s",
        (id,),
    )
    member = cur.fetchone()

    cur.close()
    conn.close()

    return render_template("edit_committee.html", member=member)


@app.route("/delete_committee/<int:id>")
def delete_committee(id):

    conn = get_db()

    cur = conn.cursor()
    cur.execute(
        "DELETE FROM committee WHERE id=%s",
        (id,),
    )

    conn.commit()
    cur.close()
    conn.close()

    return redirect(url_for("manage_committee"))


@app.route("/change_committee_photo/<int:id>", methods=["GET", "POST"])
def change_committee_photo(id):

    conn = get_db()

    if request.method == "POST":

        photo = request.files.get("photo")

        if photo and photo.filename:

            filename = photo.filename
            photo.save(
                os.path.join(app.config["UPLOAD_FOLDER"], filename)
            )

            cur = conn.cursor()
            cur.execute(
                """
                UPDATE committee
                SET photo=%s
                WHERE id=%s
                """,
                (filename, id),
            )

            conn.commit()
            cur.close()

        conn.close()
        return redirect(url_for("manage_committee"))

    cur = conn.cursor()
    cur.execute(
        "SELECT * FROM committee WHERE id=%s",
        (id,),
    )
    member = cur.fetchone()

    cur.close()
    conn.close()

    return render_template(
        "change_committee_photo.html",
        member=member
    )



@app.route("/announcements")
def announcements():
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "SELECT * FROM announcements ORDER BY id DESC"
    )
    announcements = cur.fetchall()
    cur.close()
    conn.close()

    return render_template(
        "announcements.html",
        announcements=announcements
    )

# ---------------- ANNOUNCEMENTS MANAGEMENT ----------------

@app.route("/manage_announcements")
def manage_announcements():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM announcements ORDER BY id DESC")
    announcements = cur.fetchall()
    cur.close()
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
    created_at = datetime.now().strftime("%d-%m-%Y %I:%M %p")

    conn = get_db()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO announcements
        (title,message,created_at)
        VALUES(%s,%s,%s)
        """,
        (title, message, created_at),
    )

    conn.commit()
    cur.close()
    conn.close()

    return redirect(url_for("manage_announcements"))


@app.route("/edit_announcement/<int:id>", methods=["GET", "POST"])
def edit_announcement(id):

    conn = get_db()

    if request.method == "POST":

        title = request.form["title"]
        message = request.form["message"]

        cur = conn.cursor()
        cur.execute(
            """
            UPDATE announcements
            SET title=%s, message=%s
            WHERE id=%s
            """,
            (title, message, id),
        )

        conn.commit()
        cur.close()
        conn.close()

        return redirect(url_for("manage_announcements"))

    cur = conn.cursor()
    cur.execute(
        "SELECT * FROM announcements WHERE id=%s",
        (id,),
    )
    announcement = cur.fetchone()

    cur.close()
    conn.close()

    return render_template(
        "manage_announcements.html",
        announcement=announcement
    )


@app.route("/delete_announcement/<int:id>")
def delete_announcement(id):

    conn = get_db()

    cur = conn.cursor()
    cur.execute(
        "DELETE FROM announcements WHERE id=%s",
        (id,),
    )

    conn.commit()
    cur.close()
    conn.close()

    return redirect(url_for("manage_announcements"))


# ---------------- DONATIONS ----------------

@app.route("/donation", methods=["GET", "POST"])
def donation():

    if request.method == "POST":

        name = request.form["name"]
        mobile = request.form["mobile"]
        amount = request.form["amount"]
        payment_mode = request.form["payment_mode"]
        transaction_id = request.form["transaction_id"]

        from datetime import datetime
        donation_date = datetime.now().strftime("%d-%m-%Y %I:%M %p")

        conn = get_db()
        cur = conn.cursor()

        cur.execute(
            """
            INSERT INTO donations
            (name,mobile,amount,payment_mode,transaction_id,donation_date)
            VALUES(%s,%s,%s,%s,%s,%s)
            """,
            (
                name,
                mobile,
                amount,
                payment_mode,
                transaction_id,
                donation_date,
            ),
        )

        conn.commit()
        cur.close()
        conn.close()

        return redirect(url_for("donation"))

    return render_template("donation.html")


@app.route("/donation_admin")
def donation_admin():

    conn = get_db()

    cur = conn.cursor()
    cur.execute("SELECT * FROM donations ORDER BY id DESC")
    donations = cur.fetchall()

    cur.close()
    conn.close()

    return render_template(
        "donation_admin.html",
        donations=donations,
    )


@app.route("/delete_donation/<int:id>")
def delete_donation(id):

    conn = get_db()

    cur = conn.cursor()
    cur.execute(
        "DELETE FROM donations WHERE id=%s",
        (id,),
    )

    conn.commit()
    cur.close()
    conn.close()

    return redirect(url_for("donation_admin"))


# ---------------- T-SHIRT REGISTRATION ----------------

@app.route("/tshirt", methods=["GET", "POST"])
def tshirt():

    if request.method == "POST":

        name = request.form["name"]
        mobile = request.form["mobile"]
        tshirt_size = request.form["tshirt_size"]
        quantity = request.form["quantity"]
        address = request.form["address"]

        conn = get_db()
        cur = conn.cursor()

        cur.execute(
            """
            INSERT INTO tshirt_registration
            (name,mobile,tshirt_size,quantity,address)
            VALUES(%s,%s,%s,%s,%s)
            """,
            (
                name,
                mobile,
                tshirt_size,
                quantity,
                address,
            ),
        )

        conn.commit()
        cur.close()
        conn.close()

        return redirect(url_for("tshirt"))

    return render_template("tshirt.html")


@app.route("/tshirt_admin")
def tshirt_admin():

    conn = get_db()

    cur = conn.cursor()
    cur.execute(
        """
        SELECT * FROM tshirt_registration
        ORDER BY id DESC
        """
    )
    registrations = cur.fetchall()

    cur.close()
    conn.close()

    return render_template(
        "tshirt_admin.html",
        registrations=registrations,
    )


@app.route("/delete_tshirt/<int:id>")
def delete_tshirt(id):

    conn = get_db()

    cur = conn.cursor()
    cur.execute(
        "DELETE FROM tshirt_registration WHERE id=%s",
        (id,),
    )

    conn.commit()
    cur.close()
    conn.close()

    return redirect(url_for("tshirt_admin"))


# ---------------- GALLERY & UPLOAD ----------------

# ---------------- GALLERY & UPLOAD ----------------

from werkzeug.utils import secure_filename

@app.route("/upload")
def upload():
    return render_template("upload.html")


@app.route("/upload_image", methods=["POST"])
def upload_image():

    files = request.files.getlist("photos")
    uploaded = 0

    for file in files:

        if file and allowed_file(file.filename):

            filename = secure_filename(file.filename)

            file.save(
                os.path.join(
                    app.config["UPLOAD_FOLDER"],
                    filename
                )
            )

            uploaded += 1

    return redirect(url_for("manage_gallery"))


@app.route("/manage_gallery")
def manage_gallery():

    folder = app.config["UPLOAD_FOLDER"]

    files = []

    if os.path.exists(folder):
        files = sorted(os.listdir(folder))

    return render_template(
        "manage_gallery.html",
        files=files
    )


@app.route("/delete_media/<filename>")
def delete_media(filename):

    path = os.path.join(
        app.config["UPLOAD_FOLDER"],
        filename
    )

    if os.path.exists(path):
        os.remove(path)

    return redirect(url_for("manage_gallery"))


# ---------------- ADMIN DASHBOARD ----------------

@app.route("/dashboard")
def dashboard():

    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) AS c FROM events")
    total_events = cur.fetchone()["c"]

    cur.execute("SELECT COUNT(*) AS c FROM committee")
    total_committee = cur.fetchone()["c"]

    cur.execute("SELECT COUNT(*) AS c FROM announcements")
    total_announcements = cur.fetchone()["c"]

    cur.execute("SELECT COUNT(*) AS c FROM donations")
    total_donations = cur.fetchone()["c"]

    cur.execute("SELECT COUNT(*) AS c FROM tshirt_registration")
    total_tshirts = cur.fetchone()["c"]

    cur.close()
    conn.close()

    return render_template(
        "dashboard.html",
        total_events=total_events,
        total_committee=total_committee,
        total_announcements=total_announcements,
        total_donations=total_donations,
        total_tshirts=total_tshirts
    )


@app.route("/logout")
def logout():
    return redirect(url_for("home"))

if __name__ == "__main__":
    init_db()
    app.run(debug=True, port=5001)
