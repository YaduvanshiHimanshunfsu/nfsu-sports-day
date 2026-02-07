# ============================================================
# NFSU TRIPURA CAMPUS SPORTS DAY – ADVANCED DATA PORTAL
# ============================================================

from flask import Flask, render_template, request
import pandas as pd
import re
from collections import Counter, defaultdict

app = Flask(__name__)

# ============================================================
# CONFIGURATION
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
# LOAD & CLEAN DATA
# ============================================================

df = pd.read_excel(EXCEL_FILE)
df.columns = df.columns.str.strip()
df = df.fillna("")

# ============================================================
# NORMALIZATION HELPERS
# ============================================================

def normalize(text: str) -> str:
    text = str(text).lower()
    text = text.replace("–", "-")
    text = re.sub(r"[^\w\s\-]", "", text)   # remove emojis/symbols
    text = re.sub(r"\s+", " ", text)
    return text.strip()

df["SPORT_NORM"] = df[COL_SPORT].apply(normalize)
df["TEAM_NORM"]  = df[COL_TEAM].apply(normalize)

# ============================================================
# SEMESTER SORTING
# ============================================================

SEM_MAP = {
    "i": 1, "ii": 2, "iii": 3, "iv": 4,
    "v": 5, "vi": 6, "vii": 7, "viii": 8,
    "ix": 9, "x": 10
}

def semester_key(value: str) -> int:
    value = normalize(value).replace("semester", "")
    return SEM_MAP.get(value, 99)

# ============================================================
# FIND TEAM MEMBER COLUMN (ROBUST)
# ============================================================

def find_team_member_column(team_name: str):
    key = normalize(team_name).split("-")[0]

    for col in df.columns:
        col_norm = normalize(col)
        if any(k in col_norm for k in [
            "team member",
            "team members",
            "enter names",
            "partner name"
        ]):
            if key in col_norm:
                return col
    return None

# ============================================================
# GROUP DATA BY BRANCH + SERIAL NUMBER
# ============================================================

def group_by_branch(data: pd.DataFrame):
    data = data.copy()
    data["_SEM_KEY"] = data[COL_SEM].apply(semester_key)
    data = data.sort_values("_SEM_KEY")

    grouped = defaultdict(list)

    for branch, rows in data.groupby(COL_BRANCH):
        for idx, row in enumerate(rows.to_dict("records"), start=1):
            row["SNO"] = idx
            grouped[branch].append(row)

    return dict(grouped)

# ============================================================
# CHART DATA BUILDERS
# ============================================================

def programme_chart(data: pd.DataFrame):
    return dict(Counter(data[COL_BRANCH]))

def semester_chart(data: pd.DataFrame):
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

    # ========================================================
    # INDIVIDUAL SPORTS
    # ========================================================

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

    # ========================================================
    # TEAM SPORTS (SMART HANDLING)
    # ========================================================

    if team:
        key = normalize(team)

        filtered = df[df["TEAM_NORM"].str.contains(key, na=False)]

        # -------------------------------
        # SINGLES (NO TEAM MEMBERS)
        # -------------------------------
        if any(k in key for k in ["single", "singles"]):

            result = filtered[
                [COL_NAME, COL_SEM, COL_GENDER, COL_BRANCH, COL_PHONE]
            ]

            return render_template(
                "result.html",
                sport=team,
                grouped_data=group_by_branch(result),
                team=False,
                programme_chart=programme_chart(result),
                semester_chart=semester_chart(result)
            )

        # -------------------------------
        # DOUBLES / TEAM SPORTS
        # -------------------------------
        team_col = find_team_member_column(team)

        if team_col:
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

        # -------------------------------
        # FALLBACK (NO TEAM COLUMN FOUND)
        # -------------------------------
        result = filtered[
            [COL_NAME, COL_SEM, COL_GENDER, COL_BRANCH, COL_PHONE]
        ]

        return render_template(
            "result.html",
            sport=f"{team} (team details not provided)",
            grouped_data=group_by_branch(result),
            team=False,
            programme_chart=programme_chart(result),
            semester_chart=semester_chart(result)
        )

    return "No sport selected"

# ============================================================
# RUN SERVER
# ============================================================

if __name__ == "__main__":
    app.run(debug=True)
