# ============================================================
# NFSU TRIPURA CAMPUS SPORTS DAY – FINAL BULLETPROOF BACKEND
# ------------------------------------------------------------
# Author   : Himanshu Yadav
# Purpose  : Display & analyze Sports Day participation data
# Tech     : Flask + Pandas
# Data Src : Google Form → Excel (real-world messy headers)
# ============================================================

from flask import Flask, render_template, request
import pandas as pd
import re
from collections import Counter, defaultdict

# ============================================================
# FLASK APP INIT
# ============================================================

app = Flask(__name__)

# ============================================================
# EXCEL CONFIGURATION
# ============================================================

EXCEL_FILE = "NFSU Tripura Campus Sports Day (Responses).xlsx"

COL_NAME   = "Full Name"
COL_PHONE  = "Phone Number"
COL_BRANCH = "Programme / Branch"
COL_SEM    = "Semester"
COL_GENDER = "Gender"
COL_SPORT  = "Select the Sports You Want to Participate In"
COL_TEAM   = "Sports ( Team)"

# ============================================================
# LOAD DATA
# ============================================================

df = pd.read_excel(EXCEL_FILE)
df.columns = df.columns.str.strip()
df = df.fillna("")

# ============================================================
# NORMALIZATION
# ============================================================

def normalize(text):
    text = str(text).lower()
    text = text.replace("–", "-")
    text = re.sub(r"[^\w\s\-]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()

df["SPORT_NORM"] = df[COL_SPORT].apply(normalize)
df["TEAM_NORM"]  = df[COL_TEAM].apply(normalize)

# ============================================================
# NORMALIZED COLUMN MAP
# ============================================================

NORMALIZED_COLUMNS = {
    normalize(col): col for col in df.columns
}

def find_column_by_keywords(keywords):
    for norm_col, original_col in NORMALIZED_COLUMNS.items():
        if all(k in norm_col for k in keywords):
            return original_col
    return None

# ============================================================
# SEMESTER SORT
# ============================================================

SEM_MAP = {
    "i":1,"ii":2,"iii":3,"iv":4,
    "v":5,"vi":6,"vii":7,"viii":8,
    "ix":9,"x":10
}

def semester_key(val):
    val = normalize(val).replace("semester", "")
    return SEM_MAP.get(val, 99)

# ============================================================
# GROUPING
# ============================================================

def group_by_branch(data):
    data = data.copy()
    data["_SEM_KEY"] = data[COL_SEM].apply(semester_key)
    data = data.sort_values("_SEM_KEY")

    grouped = defaultdict(list)
    for branch, rows in data.groupby(COL_BRANCH):
        for i, row in enumerate(rows.to_dict("records"), start=1):
            row["SNO"] = i
            grouped[branch].append(row)

    return dict(grouped)

# ============================================================
# CHART HELPERS
# ============================================================

def programme_chart(data):
    return dict(Counter(data[COL_BRANCH]))

def semester_chart(data):
    return dict(Counter(data[COL_SEM]))

# ============================================================
# ROUTES
# ============================================================

@app.route("/")
def home():
    return render_template("index.html")

# ============================================================
# SEARCH HANDLER
# ============================================================

@app.route("/search", methods=["POST"])
def search():

    individual = request.form.get("sport")
    team = request.form.get("team_sport")

    # --------------------------------------------------------
    # INDIVIDUAL SPORTS
    # --------------------------------------------------------
    if individual:
        key = normalize(individual).split("(")[0]
        filtered = df[df["SPORT_NORM"].str.contains(key, na=False)]

        result = filtered[
            [COL_NAME, COL_SEM, COL_GENDER, COL_BRANCH, COL_PHONE]
        ]

        return render_template(
            "result.html",
            sport=individual,
            grouped_data=group_by_branch(result),
            team=False,
            programme_chart=programme_chart(result),
            semester_chart=semester_chart(result)
        )

    # --------------------------------------------------------
    # TEAM SPORTS (FIXED)
    # --------------------------------------------------------
    if team:
        team_norm = normalize(team)

        # ✅ BASE SPORT FILTER (THIS FIXES EVERYTHING)
        if "table tennis" in team_norm:
            base_key = "table tennis"
        elif "badminton" in team_norm:
            base_key = "badminton"
        elif "carrom" in team_norm:
            base_key = "carrom"
        elif "relay" in team_norm:
            base_key = "relay"
        else:
            base_key = team_norm

        filtered = df[df["TEAM_NORM"].str.contains(base_key, na=False)]

        # ================= RELAY =================
        if "relay" in team_norm:
            team_col = find_column_by_keywords(["relay", "team"])

        # ================= CARROM =================
        elif "carrom" in team_norm:
            team_col = find_column_by_keywords(["carrom"])

        # ================= TABLE TENNIS MIXED =================
        elif "table tennis" in team_norm and "mixed" in team_norm:
            team_col = find_column_by_keywords(["table", "tennis", "mixed"])

        # ================= TABLE TENNIS DOUBLES =================
        elif "table tennis" in team_norm:
            team_col = find_column_by_keywords(["table", "tennis", "double"])

        # ================= BADMINTON MIXED =================
        elif "badminton" in team_norm and "mixed" in team_norm:
            team_col = find_column_by_keywords(["badminton", "mixed"])

        # ================= BADMINTON DOUBLES =================
        elif "badminton" in team_norm:
            team_col = find_column_by_keywords(["badminton", "double"])

        else:
            team_col = None

        # ---------------- FAIL SAFE ----------------
        if not team_col or team_col not in df.columns:
            result = filtered[
                [COL_NAME, COL_SEM, COL_GENDER, COL_BRANCH, COL_PHONE]
            ]

            return render_template(
                "result.html",
                sport=f"{team} (team details not available in form)",
                grouped_data=group_by_branch(result),
                team=False,
                programme_chart=programme_chart(result),
                semester_chart=semester_chart(result)
            )

        # ---------------- TEAM MEMBERS OK ----------------
        result = filtered[
            [COL_NAME, COL_SEM, COL_GENDER, COL_BRANCH, COL_PHONE, team_col]
        ]

        return render_template(
            "result.html",
            sport=team,
            grouped_data=group_by_branch(result),
            team=True,
            team_col=team_col,
            programme_chart=programme_chart(result),
            semester_chart=semester_chart(result)
        )

    return "No sport selected"

# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    app.run(debug=True)
