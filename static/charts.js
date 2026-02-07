/* ============================================================
   NFSU SPORTS DAY – CHART ENGINE
   Handles Pie + Bar charts with % and responsiveness
============================================================ */

/* ---------------- SAFE JSON PARSER ---------------- */

function readJSON(id) {
    const el = document.getElementById(id);
    if (!el) return null;
    try {
        return JSON.parse(el.textContent);
    } catch (e) {
        console.error("Invalid JSON in", id);
        return null;
    }
}

/* ---------------- COLOR PALETTE ---------------- */

const COLORS = [
    "#42a5f5",
    "#ffeb3b",
    "#66bb6a",
    "#ef5350",
    "#ab47bc",
    "#ffa726",
    "#26c6da",
    "#8d6e63"
];

/* ============================================================
   PIE CHART – PROGRAMME WISE
============================================================ */

function renderProgrammePie() {

    const data = readJSON("programme-data");
    if (!data) return;

    const labels = Object.keys(data);
    const values = Object.values(data);

    const ctx = document.getElementById("programmeChart");
    if (!ctx) return;

    new Chart(ctx, {
        type: "pie",
        data: {
            labels: labels,
            datasets: [{
                data: values,
                backgroundColor: COLORS
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: "bottom"
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const total = context.dataset.data.reduce((a,b)=>a+b,0);
                            const value = context.raw;
                            const percent = ((value / total) * 100).toFixed(1);
                            return `${context.label}: ${value} (${percent}%)`;
                        }
                    }
                }
            }
        }
    });
}

/* ============================================================
   BAR CHART – SEMESTER WISE
============================================================ */

function renderSemesterBar() {

    const data = readJSON("semester-data");
    if (!data) return;

    const labels = Object.keys(data);
    const values = Object.values(data);

    const ctx = document.getElementById("semesterChart");
    if (!ctx) return;

    new Chart(ctx, {
        type: "bar",
        data: {
            labels: labels,
            datasets: [{
                label: "Number of Students",
                data: values,
                backgroundColor: "#1a237e"
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        precision: 0
                    }
                }
            },
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `Students: ${context.raw}`;
                        }
                    }
                }
            }
        }
    });
}

/* ============================================================
   INITIALIZE ALL CHARTS
============================================================ */

document.addEventListener("DOMContentLoaded", () => {
    renderProgrammePie();
    renderSemesterBar();
});
