let weightChartInstance = null;

function updateWeightChart(range = "week") {
  const pathParts = window.location.pathname.split('/');
  const userId = (pathParts[1] === 'shared_view') ? pathParts[2] : null;

  let url = `/weight_data?range=${range}`;
  if (userId) url += `&user_id=${userId}`;

  fetch(url)
    .then(res => res.json())
    .then(result => {
      if (result.status !== "success") {
        alert("Failed to load weight data");
        return;
      }

      // Update table
      const table = document.getElementById("weight-table-body");
      table.innerHTML = "";
      result.data.forEach(entry => {
        const row = document.createElement("tr");
        row.innerHTML = `
          <td style="border: 1px solid #ccc; padding: 8px;">${entry.date}</td>
          <td style="border: 1px solid #ccc; padding: 8px;">${entry.weight}</td>
        `;
        table.appendChild(row);
      });

      // Update summary
      const weights = result.data.map(entry => entry.weight);
      const dates = result.data.map(entry => new Date(entry.date));
      const userHeight = parseFloat(result.height);
      const targetWeight = parseFloat(result.target_weight);

      const minWeight = Math.min(...weights);
      const maxWeight = Math.max(...weights);
      const currentWeight = weights[weights.length - 1];
      document.getElementById("current-weight-big").textContent = currentWeight ? `${currentWeight} kg` : "N/A";
      document.getElementById("current-weight").textContent = currentWeight || "N/A";
      document.getElementById("target-weight").textContent = targetWeight || "N/A";

      updateBMIProgress(currentWeight, userHeight);

      // Update chart
      const ctx = document.getElementById("weight-chart").getContext("2d");
      if (weightChartInstance) {
        weightChartInstance.destroy();
      }
      weightChartInstance = new Chart(ctx, {
        type: "line",
        data: {
          labels: result.data.map(entry => entry.date),
          datasets: [{
            label: "Weight",
            data: result.data.map(entry => entry.weight),
            borderColor: "rgba(75, 192, 192, 1)",
            backgroundColor: "rgba(75, 192, 192, 0.2)",
            fill: true,
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            x: {
              title: { display: true, text: "Date" }
            },
            y: {
              title: { display: true, text: "Weight (kg)" },
              beginAtZero: false,
              min: Math.floor(minWeight / 5) * 5 - 5,
              max: Math.floor(maxWeight / 5) * 5 + 5,
              ticks: { stepSize: 5 }
            }
          }
        }
      });
    });
}

document.addEventListener("DOMContentLoaded", () => {
  const pathParts = window.location.pathname.split('/');
  const userId = (pathParts[1] === 'shared_view') ? pathParts[2] : null;
  const ranges = ["week", "month", "year"];
  ranges.forEach(range => {
    const btn = document.getElementById(`btn-weight-${range}`);
    if (btn) {
      btn.addEventListener("click", () => {
        updateWeightChart(range);
        // Set active class
        ranges.forEach(r => {
          const b = document.getElementById(`btn-weight-${r}`);
          if (b) b.classList.remove("active");
        });
        btn.classList.add("active");
      });
    }
  });

  updateWeightChart("week");
});


function updateBMIProgress(currentWeight, userHeight) {
  const bmiLabel = document.getElementById("bmi-label");
  const bmiArrow = document.getElementById("bmi-arrow");

  if (!bmiLabel || !bmiArrow) return;

  if (!currentWeight || !userHeight) {
    bmiLabel.textContent = "BMI: N/A";
    bmiArrow.style.left = "0%";
    return;
  }

  const bmi = (currentWeight / ((userHeight / 100) ** 2)).toFixed(1);
  document.getElementById("bmi-value").textContent = bmi;
  const bmiClamped = Math.min(Math.max(bmi, 10), 40);
  const percent = ((bmiClamped - 10) / 30) * 100;

  bmiLabel.textContent = `BMI: ${bmi}`;
  // Center the arrow by shifting left by half its width (assume ~40px)
  bmiArrow.style.left = `calc(${percent}% - 20px)`;
}