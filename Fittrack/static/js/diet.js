function toTitleCase(str) {
  return str
    .toLowerCase()
    .split(" ")
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(" ");
}

// check share view
function getSharedUserIdIfAny() {
  const match = window.location.pathname.match(/^\/shared_view\/(\d+)\/diet$/);
  return match ? parseInt(match[1]) : null;
}

function loadDietPageFeatures() {
  const todayStr = new Date().toISOString().split("T")[0];
  document.getElementById("calorie-date").value = todayStr;

  loadDietData(todayStr);
  loadCalorieIntakeTrend();
  loadEnergyGapTrend();
  loadCalorieRecommendation();

  document.getElementById("calorie-date").addEventListener("change", (e) => {
    const selectedDate = e.target.value;
    if (selectedDate) loadDietData(selectedDate);
  });

  const activitySelect = document.getElementById("activity-level-select");
  if (activitySelect) {
    activitySelect.addEventListener("change", () => {
      loadCalorieRecommendation();
    });
  }
}

async function loadDietData(dateStr) {
  try {
    const sharedUserId = getSharedUserIdIfAny();
    const url = sharedUserId
      ? `/diet_data/${dateStr}?user_id=${sharedUserId}`
      : `/diet_data/${dateStr}`;
    const res = await fetch(url);
    const result = await res.json();
    if (result.status !== "success") return;

    const intake = result.total_calories;
    const recommended = parseFloat(document.getElementById("calorie-recommended").innerText) || 0;
    const gap = intake - recommended;

    document.getElementById("calorie-intake").innerText = intake.toFixed(1) + " kcal";

    const diffElem = document.getElementById("calorie-diff");
    diffElem.innerText = `${gap.toFixed(1)} kcal`;
    diffElem.style.color = gap > 0
      ? "#d32f2f"
      : gap < -0.2 * recommended
        ? "#f57c00"
        : "#388e3c";

    const adviceElem = document.getElementById("intake-diff-box").querySelector("p");
    if (gap < 0) {
      const ratio = Math.abs(gap) / recommended;
      adviceElem.innerHTML = ratio >= 0.2
        ? `<em>Your intake is <strong>far below</strong> recommendation (&gt;20%). Consider adjusting meals to avoid metabolic slowdown. A healthier strategy is increasing activity, not excessive dieting.</em>`
        : `<em>Your intake is <strong>below</strong> recommendation. Consider adjusting meals to avoid metabolic slowdown.</em>`;
    } else if (gap > 0) {
      adviceElem.innerHTML = `<em>You consumed more than recommended today. Consider balancing with exercise.</em>`;
    } else {
      adviceElem.innerHTML = `<em>Your intake matches the recommendation. Great job!</em>`;
    }
  } catch (err) {
    console.error("Failed to load diet data", err);
  }
}

async function loadCalorieRecommendation() {
  const level = document.getElementById("activity-level-select").value || "moderate";
  const sharedUserId = getSharedUserIdIfAny();

  let url = `/api/recommended_calories?activity=${level}`;
  if (sharedUserId) {
    url += `&user_id=${sharedUserId}`;
  }

  try {
    const res = await fetch(url);
    const result = await res.json();
    if (result.recommended) {
      document.getElementById("calorie-recommended").innerText = `${result.recommended} kcal`;

      const intakeText = document.getElementById("calorie-intake").innerText;
      const intake = parseFloat(intakeText) || 0;
      const recommended = result.recommended;
      const gap = intake - recommended;

      const diffElem = document.getElementById("calorie-diff");
      diffElem.innerText = `${gap.toFixed(1)} kcal`;
      diffElem.style.color = gap > 0
        ? "#d32f2f"
        : gap < -0.2 * recommended
          ? "#f57c00"
          : "#388e3c";

      const adviceElem = document.getElementById("intake-diff-box").querySelector("p");
      if (gap < 0) {
        const ratio = Math.abs(gap) / recommended;
        adviceElem.innerHTML = ratio >= 0.2
          ? `<em>Your intake is <strong>far below</strong> recommendation (&gt;20%). Consider adjusting meals to avoid metabolic slowdown. A healthier strategy is increasing activity, not excessive dieting.</em>`
          : `<em>Your intake is <strong>below</strong> recommendation. Consider adjusting meals to avoid metabolic slowdown.</em>`;
      } else if (gap > 0) {
        adviceElem.innerHTML = `<em>You consumed more than recommended today. Consider balancing with exercise.</em>`;
      } else {
        adviceElem.innerHTML = `<em>Your intake matches the recommendation. Great job!</em>`;
      }
    }
  } catch (err) {
    console.error("Failed to fetch recommended calorie with level:", level);
  }
}


function loadCalorieIntakeTrend() {
  const sharedUserId = getSharedUserIdIfAny();
  const url = sharedUserId
    ? `/diet_calorie_trend?user_id=${sharedUserId}`
    : `/diet_calorie_trend`;

  fetch(url)
    .then(res => res.json())
    .then(result => {
      if (result.status !== "success") return;

      const dates = result.data.map(r => r.date);
      const values = result.data.map(r => r.total_calories);

      const tbody = document.getElementById("calorie-intake-table-body");
      tbody.innerHTML = "";
      result.data.forEach(entry => {
        const row = document.createElement("tr");
        row.innerHTML = `<td>${entry.date}</td><td>${entry.total_calories}</td>`;
        tbody.appendChild(row);
      });

      const ctx = document.getElementById("calorie-intake-chart").getContext("2d");
      new Chart(ctx, {
        type: "line",
        data: {
          labels: dates,
          datasets: [{
            label: "Calories Consumed",
            data: values,
            borderColor: "#42a5f5",
            backgroundColor: "rgba(66, 165, 245, 0.2)",
            borderWidth: 2,
            fill: true,
            tension: 0.3
          }]
        },
        options: {
          responsive: true,
          scales: {
            x: { title: { display: true, text: "Date" } },
            y: { title: { display: true, text: "Calories" }, beginAtZero: true }
          }
        }
      });
    })
    .catch(err => console.error("Failed to load calorie intake chart", err));
}

function loadEnergyGapTrend() {
  const sharedUserId = getSharedUserIdIfAny();
  const url = sharedUserId
    ? `/diet_energy_gap_trend?user_id=${sharedUserId}`
    : `/diet_energy_gap_trend`;

  fetch(url)
    .then(res => res.json())
    .then(result => {
      if (result.status !== "success") return;

      const tableBody = document.getElementById("energy-gap-table-body");
      tableBody.innerHTML = "";
      result.data.forEach(entry => {
        const row = document.createElement("tr");
        row.innerHTML = `
          <td>${entry.date}</td>
          <td style="color: ${entry.energy_gap > 0 ? '#d32f2f' : '#388e3c'}">
            ${entry.energy_gap.toFixed(1)} kcal
          </td>
        `;
        tableBody.appendChild(row);
      });

      const ctx = document.getElementById("energy-gap-chart").getContext("2d");
      new Chart(ctx, {
        type: "line",
        data: {
          labels: result.data.map(e => e.date),
          datasets: [{
            label: "Energy Gap (kcal)",
            data: result.data.map(e => e.energy_gap),
            borderColor: "#f57c00",
            backgroundColor: "rgba(255, 152, 0, 0.2)",
            fill: true,
            tension: 0.3
          }]
        },
        options: {
          responsive: true,
          plugins: { legend: { display: true } },
          scales: {
            y: { title: { display: true, text: "kcal" }, beginAtZero: false },
            x: { title: { display: true, text: "Date" } }
          }
        }
      });
    })
    .catch(err => console.error("Failed to load energy gap trend", err));
}

// check
const sharedUserId = getSharedUserIdIfAny();
if (!sharedUserId) {
  loadCalorieRecommendation();
}


document.addEventListener("DOMContentLoaded", loadDietPageFeatures);
