import json
from datetime import datetime

from flask import Flask, render_template, request, redirect, flash, url_for


CLUB_FILE: str = "clubs.json"
COMPETITIONS_FILE: str = "competitions.json"
DATE_FORMAT: str = "%Y-%m-%d %H:%M:%S"

app = Flask(__name__)
app.secret_key = "something_special"


def load_data(filename: str) -> list[dict]:
    with open(filename) as file:
        return json.load(file)[filename.split(".")[0]]


def update_files(filename: str, content: list) -> None:
    with open(filename, "w") as file:
        json.dump({filename.split(".")[0]: content}, file)


def date_is_in_paste(date: str) -> bool:
    if datetime.strptime(date, DATE_FORMAT).date() > datetime.today().date():
        return False
    return True


clubs: list[dict] = load_data(CLUB_FILE)
competitions: list[dict] = load_data(COMPETITIONS_FILE)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/showSummary", methods=["POST"])
def show_summary():
    selected_club = [club for club in clubs if club["email"] == request.form["email"]]
    if not selected_club:
        flash("Sorry, that email wasn't found.")
        return render_template("index.html")
    return render_template("welcome.html", club=selected_club[0], competitions=competitions)


@app.route("/book/<competition>/<club>")
def book(competition, club):
    found_club = [c for c in clubs if c["name"] == club]
    found_competition = [c for c in competitions if c["name"] == competition]
    if found_club and found_competition:
        if date_is_in_paste(found_competition[0].get("date")):
            flash("The event is finish")
            return render_template("welcome.html", club=found_club[0], competitions=competitions)
        return render_template("booking.html", club=found_club[0], competition=found_competition[0])
    flash("Something went wrong-please try again")
    return render_template("welcome.html", club=club, competitions=competitions)


@app.route("/purchasePlaces", methods=["POST"])
def purchase_places():
    competition_index = [index for index, c in enumerate(competitions) if c["name"] == request.form["competition"]][0]
    club_index = [index for index, c in enumerate(clubs) if c["name"] == request.form["club"]][0]
    current_places = int(competitions[competition_index]["numberOfPlaces"])
    needed_places = int(request.form["places"])
    club_points = int(clubs[club_index]["points"])
    if date_is_in_paste(competitions[competition_index]["date"]):
        flash("The event is finish")
        return render_template("welcome.html", club=clubs[club_index], competitions=competitions)
    clubs[club_index]["points"] = str(club_points - needed_places)
    competitions[competition_index]["numberOfPlaces"] = str(current_places - needed_places)
    update_files(COMPETITIONS_FILE, competitions)
    update_files(CLUB_FILE, clubs)
    flash("Great-booking complete!")
    return render_template("welcome.html", club=clubs[club_index], competitions=competitions)


@app.route("/logout")
def logout():
    return redirect(url_for("index"))


@app.route("/showPoints")
def show_points():
    return render_template("show_points.html", clubs=clubs)
