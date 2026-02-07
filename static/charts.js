/* =====================================================
   NFSU SPORTS DAY – CHARTS (FINAL CLEAN VERSION)
===================================================== */

document.addEventListener("DOMContentLoaded", () => {

    const dataBox = document.getElementById("chartData");
    if (!dataBox) return;

    const programmeData = JSON.parse(dataBox.dataset.programme || "{}");
    const semesterData  = JSON.parse(dataBox.dataset.semester || "{}");

    /* ---------- COLORS ---------- */
    const COLORS = [
        "#1a237e", "#42a5f5", "#ffeb3b",
        "#66bb6a", "#ff7043", "#ab47bc"
    ];

    /* =====================================================
       PIE CHART – PROGRAMME
    ===================================================== */
    const pieCanvas = document.getElementById("programmeChart");

    if (pieCanvas && Object.keys(programmeData).length > 0) {

        new Chart(pieCanvas, {
            type: "pie",
            data: {
                labels: Object.keys(programmeData),
                datasets: [{
                    data: Object.values(programmeData),
                    backgroundColor: COLORS,
                    borderColor: "#ffffff",
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                layout: {
                    padding: 20
                },
                plugins: {
                    legend: {
                        position: "bottom",
                        labels: {
                            color: "#000",
                            font: {
                                size: 14,
                                weight: "600"
                            },
                            padding: 20
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function (ctx) {
                                const total = ctx.dataset.data.reduce((a, b) => a + b, 0);
                                const val = ctx.raw;
                                const percent = ((val / total) * 100).toFixed(1);
                                return `${ctx.label}: ${val} (${percent}%)`;
                            }
                        }
                    }
                },
                animation: {
                    animateScale: true,
                    animateRotate: true,
                    duration: 1200
                }
            }
        });
    }

    /* =====================================================
       BAR CHART – SEMESTER
    ===================================================== */
    const barCanvas = document.getElementById("semesterChart");

    if (barCanvas && Object.keys(semesterData).length > 0) {

        new Chart(barCanvas, {
            type: "bar",
            data: {
                labels: Object.keys(semesterData),
                datasets: [{
                    label: "Participants",
                    data: Object.values(semesterData),
                    backgroundColor: "#42a5f5",
                    borderRadius: 8
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: {
                        ticks: { color: "#000" },
                        grid: { display: false }
                    },
                    y: {
                        beginAtZero: true,
                        ticks: { color: "#000", stepSize: 1 }
                    }
                },
                plugins: {
                    legend: { display: false }
                },
                animation: {
                    duration: 1000,
                    easing: "easeOutQuart"
                }
            }
        });
    }
});
