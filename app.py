import os
import datetime

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required

# Configure application
app = Flask(__name__)

confirm_today = datetime.date.today()

def reset_recurring(database):
    global confirm_today
    confirm_today = datetime.date.today()
    database.execute("UPDATE tasks SET done = 0 WHERE is_recurring = 1")

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///tasks.db")

days_of_the_week = {
    6: "Sat",
    7: "Sun",
    1: "Mon",
    2: "Tue",
    3: "Wed",
    4: "Thu",
    5: "Fri"
}

priorities = {
    1: "High",
    0: "Normal",
    -1: "Low"
}

checked = {
    None: "",
    0: "",
    1: "checked",
    "on": "checked"
}

done = {
    0: "No",
    1: "Yes"
}


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    """Info"""
    return render_template("index.html")


@app.route("/add", methods=["GET", "POST"])
@login_required
def add():
    """Add or update a task"""

    today = datetime.date.today()

    if request.method == "GET":
        return render_template("add.html", days=days_of_the_week, days_checked = [],due_date=today, start_date=today, end_date=today, priority=0, action="Add")

    task_id = request.form.get("task-id")
    update = False
    if task_id:
        update = True

    name = request.form.get("task-name")
    description = request.form.get("task-description")
    priority = request.form.get("priority")
    recurring = request.form.get("recurring")

    action = "Add"
    if update:
        action = "Edit"

    if len(name) == 0:
        flash("Task name is empty!")
        return render_template("add.html", days=days_of_the_week, days_checked = [], id=task_id, due_date=today, start_date=today, end_date=today, name=name, description=description, priority=priority, recurring=checked[recurring], action=action)

    if recurring:
        start_date = request.form.get("start-date")
        end_date = request.form.get("end-date")

        if start_date >= end_date:
            flash("Date interval is invalid")
            return render_template("add.html", days=days_of_the_week, days_checked = [], id=task_id, due_date=today, start_date=start_date, end_date=end_date, name=name, description=description, priority=priority, recurring=checked[recurring], action=action)

        days = []
        for day in days_of_the_week:
            abbreviation = days_of_the_week[day]
            if request.form.get(abbreviation):
                days.append(day)

        if len(days) == 0:
            flash("No days are checked")
            return render_template("add.html", days=days_of_the_week, days_checked = [], id=task_id, due_date=today, start_date=start_date, end_date=end_date, name=name, description=description, priority=priority, recurring=checked[recurring], action=action)

        if update:
            # Update the task
            db.execute("""
                UPDATE tasks
                SET name = ?, description = ?, priority = ?, start_date = ?, end_date = ?, is_recurring = ?
                WHERE id = ? AND user_id = ?
            """, name, description, priority, start_date, end_date, True, task_id, session["user_id"])

            # Clear existing recurrence days and insert new ones
            db.execute("DELETE FROM recurrence WHERE task_id = ?", task_id)
            for day in days:
                db.execute("INSERT INTO recurrence (task_id, day) VALUES(?, ?)", task_id, day)

        else:
            # Insert a new task
            db.execute("""
                INSERT INTO tasks (user_id, name, description, priority, start_date, end_date, is_recurring)
                VALUES(?, ?, ?, ?, ?, ?, ?)
            """, session["user_id"], name, description, priority, start_date, end_date, True)
            task_id = db.execute("""
                SELECT id FROM tasks
                WHERE user_id = ? AND name = ? AND description = ? AND priority = ? AND start_date = ? AND end_date = ? AND is_recurring = ?
            """, session["user_id"], name, description, priority, start_date, end_date, True)[0]["id"]
            for day in days:
                db.execute("INSERT INTO recurrence (task_id, day) VALUES(?, ?)", task_id, day)

    else:
        due_date = request.form.get("date")

        if update:
            # Update the task
            db.execute("""
                UPDATE tasks
                SET name = ?, description = ?, priority = ?, due_date = ?
                WHERE id = ? AND user_id = ?
            """, name, description, priority, due_date, task_id, session["user_id"])
        else:
            # Insert a new task
            db.execute("""
                INSERT INTO tasks (user_id, name, description, priority, due_date)
                VALUES(?, ?, ?, ?, ?)
            """, session["user_id"], name, description, priority, due_date)

    if update:
        if recurring:
            return redirect("/recurring")
        else:
            return redirect("/today")

    return redirect("/add")


@app.route("/history", methods=["GET", "POST"])
@login_required
def history():
    """Show history of all tasks"""

    if request.method == "POST":
        date = request.form.get("date")
        if not date:
            return apology("Invalid Date")

        tasks = db.execute("SELECT name, description, done FROM tasks WHERE due_date = ? AND user_id = ?", date, session["user_id"])
        return render_template("history.html", day=date, tasks=tasks, isDone=done)

    today = datetime.date.today()
    return render_template("history.html", day=today)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/today", methods=["GET", "POST"])
@login_required
def today():
    """Get today tasks."""

    if request.method == "POST":
        task_id = request.form.get("task-id")
        if request.form.get("delete-task"):
            db.execute("DELETE FROM tasks WHERE id = ? AND user_id = ?", task_id, session["user_id"])
            return redirect("/today")
        elif request.form.get("edit-task"):
            task = db.execute("SELECT * FROM tasks WHERE id = ? AND user_id = ?", task_id, session["user_id"])[0]

            if task["is_recurring"]:
                days_queried, days_checked = db.execute("SELECT day FROM recurrence WHERE task_id = ?", task_id), {}
                for day in days_queried:
                    days_checked[day["day"]] = "checked"

                return render_template("add.html", days=days_of_the_week, id=task_id, name=task["name"], description=task["description"], recurring=checked[task["is_recurring"]], priority=task["priority"], start_date=task["start_date"], end_date=task["end_date"], action="Edit", days_checked=days_checked)

            return render_template("add.html", days=days_of_the_week, days_checked = [], id=task_id, name=task["name"], description=task["description"], recurring=checked[task["is_recurring"]], priority=task["priority"], due_date=task["due_date"], action="Edit")

        new_value = not db.execute("SELECT done FROM tasks WHERE id = ? AND user_id = ?", task_id, session["user_id"])[0]["done"]
        print("Here", new_value)
        db.execute("UPDATE tasks SET done = ? WHERE tasks.id = ? AND user_id = ?", new_value, task_id, session["user_id"])
        return redirect("/today")

    global confirm_today
    today = datetime.date.today()
    if today != confirm_today:
        reset_recurring(db)

    tasks = db.execute("""
        SELECT DISTINCT tasks.*
        FROM tasks
        LEFT JOIN recurrence ON tasks.id = recurrence.task_id
        WHERE
            tasks.user_id = ? AND
            ((tasks.due_date = ?)
            OR
            (tasks.is_recurring = 1
            AND tasks.start_date <= ?
            AND tasks.end_date >= ?
            AND recurrence.day = ?))
        ORDER BY tasks.priority DESC;
    """, session["user_id"], today, today, today, today.strftime("%w"))
    print("Here------> ",today.strftime("%w"))
    return render_template("today.html", tasks=tasks, priorities=priorities, isChecked=checked)


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "GET":
        return render_template("register.html")

    username = request.form.get("username")
    password = request.form.get("password")
    confirm_password = request.form.get("confirmation")

    if password != confirm_password:
        return apology("PASSWARDS DON'T MATCH")

    users = db.execute("SELECT * FROM users WHERE username = ?;", username)
    if len(users) > 0:
        return apology("USERNAME IS USED")

    id = db.execute("SELECT COUNT(*) AS n FROM users;")[0]["n"] + 1

    if not username or not password:
        return apology("EMPTY FIELDS")

    password = generate_password_hash(password)
    db.execute("INSERT INTO users (id, username, hash) VALUES(?, ?, ?)", id, username, password)
    return redirect("/")


@app.route("/recurring", methods=["GET", "POST"])
@login_required
def recurring():
    """Get all recurring tasks"""

    if request.method == "POST":
        task_id = request.form.get("task-id")
        if request.form.get("delete-task"):
            db.execute("DELETE FROM tasks WHERE user_id = ? AND id = ?", session["user_id"], task_id)
            return redirect("/recurring")
        else:
            task = db.execute("SELECT * FROM tasks WHERE id = ? AND user_id = ?", task_id, session["user_id"])[0]
            days_queried, days_checked = db.execute("SELECT day FROM recurrence WHERE task_id = ?", task_id), {}
            for day in days_queried:
                days_checked[day["day"]] = "checked"

            return render_template("add.html", days=days_of_the_week, id=task_id, name=task["name"], description=task["description"], recurring=checked[task["is_recurring"]], priority=task["priority"], start_date=task["start_date"], end_date=task["end_date"], action="Edit", days_checked=days_checked)


    tasks = db.execute("""
        SELECT
            tasks.id,
            tasks.name,
            tasks.description,
            tasks.priority,
            tasks.start_date,
            tasks.end_date,
            GROUP_CONCAT(recurrence.day) AS recurrence_days
        FROM tasks
        LEFT JOIN recurrence ON tasks.id = recurrence.task_id
        WHERE tasks.is_recurring = 1 AND user_id = ?
        GROUP BY tasks.id
        ORDER BY tasks.priority;
    """, session["user_id"])
    return render_template("recurring.html", tasks=tasks, priorities=priorities, days_of_the_week=days_of_the_week)


sort = '0'


@app.route("/overdue", methods=["GET", "POST"])
@login_required
def overdue():
    """Get all overdue tasks"""
    global sort
    queries = {
        '0': """
        SELECT DISTINCT tasks.*
        FROM tasks
        WHERE
            tasks.user_id = ? AND tasks.due_date < ?
        ORDER BY tasks.due_date DESC;
    """,
        '1': """
        SELECT DISTINCT tasks.*
        FROM tasks
        WHERE
            tasks.user_id = ? AND tasks.due_date < ?
        ORDER BY tasks.priority DESC;
    """
    }

    today = datetime.date.today()
    if request.method == "POST":
        new_sort = request.form.get("sort")
        if new_sort:
            if new_sort != sort:
                sort = new_sort
                return redirect("/overdue")

        task_id = request.form.get("task-id")
        db.execute("UPDATE tasks SET due_date = ?, priority = 1 WHERE user_id = ? AND id = ? AND done = 0",
                   today, session["user_id"], task_id)
        flash("Added to today tasks!")
        return redirect("/today")

    tasks = db.execute(queries[sort], session["user_id"], today)

    return render_template("overdue.html", tasks=tasks, priorities=priorities, sort=sort)
