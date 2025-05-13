// === Helper: Update the line chart for exercise ===
function updateExerciseChart(range = "week") {
  const url = `/api/exercise_data?range=${range}`;
  fetch(url)
    .then(res => res.json())
    .then(result => {
      if (!result.labels || !result.minutes) return;

      const ctx = document
        .getElementById("exerciseChart")
        .getContext("2d");
      if (window.exerciseChartInstance) {
        window.exerciseChartInstance.destroy();
      }

      window.exerciseChartInstance = new Chart(ctx, {
        type: "line",
        data: {
          labels: result.labels,
          datasets: [
            {
              label: "Minutes of Exercise",
              data: result.minutes,
              borderColor: "rgba(0, 200, 200, 1)",
              backgroundColor: "rgba(0, 200, 200, 0.2)",
              fill: true,
              tension: 0.3
            }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            x: {
              title: { display: true, text: "Date" }
            },
            y: {
              title: { display: true, text: "Minutes" },
              beginAtZero: true
            }
          }
        }
      });
    })
    .catch(error => console.error("Error updating exercise chart:", error));
}

// === Main Feature Loader ===
function loadExercisePageFeatures() {
  // Weekly Goal Message + Table
  fetch("/api/exercise_goal_progress")
    .then(res => res.json())
    .then(data => {
      if (data.status !== "success") {
        console.error("Goal progress fetch failed:", data.message);
        return;
      }

      const msg = document.getElementById("goalMessage");
      const goal = document.getElementById("goal-minutes");
      const comp = document.getElementById("completed-minutes");
      const rem = document.getElementById("remaining-minutes");

      if (msg) {
        msg.innerHTML =
          data.remaining <= 0
            ? "🎉 <strong>Congratulations!</strong> You've met your goal!"
            : `You're <span class="gradient-text fw-bold">${data.remaining} minutes</span> away from your goal this week. Keep it up! 💪`;
        msg.classList.add("visible");
      }

      if (goal) goal.textContent = data.goal;
      if (comp) comp.textContent = data.completed;
      if (rem) rem.textContent = data.remaining;

      const weeklyMinutesEl = document.getElementById("exercise-minutes-this-week");
      if (weeklyMinutesEl) {
        weeklyMinutesEl.textContent = data.completed + " min";
      }

      const fill = document.getElementById("goal-progress-fill");
      const percentLabel = document.getElementById("goal-progress-percent");

      if (fill && data.goal > 0) {
        const progress = Math.min((data.completed / data.goal) * 100, 100);
        fill.style.width = progress + "%";

        fill.style.backgroundColor =
          progress >= 100 ? "#4caf50" :
          progress >= 50 ? "#ffc107" :
          "#ff5722";

        if (percentLabel) {
          percentLabel.textContent = `${Math.round(progress)}% of weekly goal`;
        }

        if (progress === 100) {
          fill.classList.add("sparkle");
          setTimeout(() => fill.classList.remove("sparkle"), 2000);
        }
      }
    })
    .catch(error => console.error("Error loading goal progress:", error));

  // Line Chart (Default: week)
  updateExerciseChart("week");

  // Range Toggle Buttons
  const exWeekBtn = document.getElementById("btn-ex-week");
  const exMonthBtn = document.getElementById("btn-ex-month");
  const exYearBtn = document.getElementById("btn-ex-year");
  [exWeekBtn, exMonthBtn, exYearBtn].forEach((btn, idx) => {
    const ranges = ["week", "month", "year"];
    btn?.addEventListener("click", () => {
      updateExerciseChart(ranges[idx]);
      [exWeekBtn, exMonthBtn, exYearBtn].forEach(b => b?.classList.remove("active"));
      btn.classList.add("active");
    });
  });

  // Pie Chart: By Type
  fetch("/api/exercise_type_breakdown")
    .then(res => res.json())
    .then(data => {
	if (!data.labels || !data.minutes || data.minutes.length === 0) {
  		const container = document.getElementById("typeBreakdownChart").parentElement;
  		container.innerHTML = `
    			<div class="alert alert-warning text-center fs-5 fw-medium" role="alert">
     			No exercise data available yet. Start logging your activity to see this chart!
    			</div>`;
  		return;
	}
      const ctx = document
        .getElementById("typeBreakdownChart")
        .getContext("2d");
      new Chart(ctx, {
        type: "pie",
        data: {
          labels: data.labels,
          datasets: [
            {
              label: "Time by Type",
              data: data.minutes,
              backgroundColor: [
                "#FF6384",
                "#36A2EB",
                "#FFCE56",
                "#4BC0C0",
                "#9966FF",
                "#FF9F40"
              ]
            }
          ]
        },
        options: {
          responsive: true,
          plugins: {
            legend: { position: "bottom" },
            tooltip: {
              callbacks: {
                label: function (context) {
                  const label = context.label || "";
                  const value = context.parsed;
                  const total = context.chart.data.datasets[0].data.reduce((a, b) => a + b, 0);
                  const percentage = ((value / total) * 100).toFixed(1);
                  return `${label}: ${percentage}%`;
                }
              }
            }
          }
        }
      });
    })
    .catch(error => console.error("Error loading type breakdown:", error));

  // Pie Chart: By Intensity
  fetch("/api/exercise_intensity_breakdown")
    .then(res => res.json())
    .then(data => {
	if (!data.labels || !data.minutes || data.minutes.length === 0) {
  		const container = document.getElementById("intensityBreakdownChart").parentElement;
  		container.innerHTML = `
    			<div class="alert alert-warning text-center fs-5 fw-medium" role="alert">
      			No exercise data available yet. Start logging your activity to see this chart!
    			</div>`;
  		return;
	}
      const ctx = document
        .getElementById("intensityBreakdownChart")
        .getContext("2d");
      new Chart(ctx, {
        type: "pie",
        data: {
          labels: data.labels,
          datasets: [
            {
              label: "Time by Intensity",
              data: data.minutes,
              backgroundColor: [
                "#FF6384",
                "#36A2EB",
                "#FFCE56"
              ]
            }
          ]
        },
        options: {
          responsive: true,
          plugins: {
            legend: { position: "bottom" },
            tooltip: {
              callbacks: {
                label: function (context) {
                  const label = context.label || "";
                  const value = context.parsed;
                  const total = context.chart.data.datasets[0].data.reduce((a, b) => a + b, 0);
                  const percentage = ((value / total) * 100).toFixed(1);
                  return `${label}: ${percentage}%`;
                }
              }
            }
          }
        }
      });
    })
    .catch(error => console.error("Error loading intensity breakdown:", error));
}

// Initialize features when DOM content is loaded
document.addEventListener("DOMContentLoaded", loadExercisePageFeatures);
