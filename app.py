# ============================================================
# NFSU TRIPURA CAMPUS SPORTS DAY - DATA PORTAL (FINAL VERSION)
# ============================================================

from flask import Flask, render_template, request
import pandas as pd
import re

app = Flask(__name__)

# ------------------------------------------------------------
# LOAD EXCEL
# ------------------------------------------------------------

FILE = "NFSU Tripura Campus Sports Day (Responses).xlsx"
df = pd.read_excel(FILE)

# ------------------------------------------------------------
# CLEAN COLUMN HEADERS & DATA
# ------------------------------------------------------------

df.columns = df.columns.str.strip()
df = df.fillna("")

# ------------------------------------------------------------
# MAIN COLUMN NAMES
# ------------------------------------------------------------

COL_SPORT  = "Select the Sports You Want to Participate In"
COL_TEAM   = "Sports ( Team)"

COL_NAME   = "Full Name"
COL_PHONE  = "Phone Number"
COL_BRANCH = "Programme / Branch"
COL_SEM    = "Semester"
COL_GENDER = "Gender"

# ------------------------------------------------------------
# TEXT NORMALIZER
# ------------------------------------------------------------

def normalize(text):
    text = str(text).lower()
    text = text.replace("–", "-")
    text = re.sub(r"\s+", " ", text)
    return text.strip()

df["SPORT_NORM"] = df[COL_SPORT].apply(normalize)
df["TEAM_NORM"]  = df[COL_TEAM].apply(normalize)

# ------------------------------------------------------------
# SEMESTER ORDER MAP
# ------------------------------------------------------------

SEM_MAP = {
    "i":1,
    "ii":2,
    "iii":3,
    "iv":4,
    "v":5,
    "vi":6,
    "vii":7,
    "viii":8,
    "ix":9,
    "x":10
}

def semester_key(val):
    text = normalize(val)
    text = text.replace("semester", "").strip()
    return SEM_MAP.get(text, 99)

# ------------------------------------------------------------
# AUTO FIND TEAM MEMBER COLUMN
# ------------------------------------------------------------

def find_team_member_column(team_name):

    key = normalize(team_name).split("-")[0]

    for col in df.columns:
        if "enter names of team members" in normalize(col):
            if key in normalize(col):
                return col
    return None

# ------------------------------------------------------------
# GROUP BY BRANCH + SORT + SERIAL NUMBER
# ------------------------------------------------------------

def group_branch(data):

    data = data.sort_values(
        by=COL_SEM,
        key=lambda x: x.map(semester_key)
    )

    grouped = {}

    for branch, rows in data.groupby(COL_BRANCH):

        temp = rows.to_dict(orient="records")

        for i, r in enumerate(temp, start=1):
            r["SNO"] = i

        grouped[branch] = temp

    return grouped

# ------------------------------------------------------------
# HOME PAGE
# ------------------------------------------------------------

@app.route("/")
def home():
    return render_template("index.html")

# ------------------------------------------------------------
# SEARCH HANDLER
# ------------------------------------------------------------

@app.route("/search", methods=["POST"])
def search():

    individual = request.form.get("sport")
    team = request.form.get("team_sport")

    # ================= INDIVIDUAL SPORTS =================

    if individual:

        key = normalize(individual).split("(")[0]

        filtered = df[
            df["SPORT_NORM"].str.contains(key)
        ]

        result = filtered[
            [COL_NAME, COL_SEM, COL_GENDER, COL_BRANCH, COL_PHONE]
        ]

        grouped = group_branch(result)

        return render_template(
            "result.html",
            sport=individual,
            grouped_data=grouped,
            team=False
        )

    # ================= TEAM SPORTS =================

    if team:

        key = normalize(team).split("-")[0]

        filtered = df[
            df["TEAM_NORM"].str.contains(key)
        ]

        team_col = find_team_member_column(team)

        if team_col is None:
            return f"Team column not found for {team}"

        result = filtered[
            [COL_NAME, COL_SEM, COL_GENDER,
             COL_BRANCH, COL_PHONE, team_col]
        ]

        grouped = group_branch(result)

        return render_template(
            "result.html",
            sport=team,
            grouped_data=grouped,
            team=True,
            team_col=team_col
        )

    return "No sport selected"

# ------------------------------------------------------------
# RUN SERVER
# ------------------------------------------------------------

if __name__ == "__main__":
    app.run(debug=True)
