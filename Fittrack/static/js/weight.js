
document.addEventListener("DOMContentLoaded", () => {
  fetch("/weight_data")
    .then(res => res.json())
    .then(result => {
      if (result.status !== "success") {
        alert("Failed to load weight data");
        return;
      }
      const table = document.getElementById("weight-table-body");
      table.innerHTML = "";

      const userHeight = parseFloat(result.height);
      const targetWeight = parseFloat(result.target_weight);

      result.data.forEach(entry => {
        const row = document.createElement("tr");
        row.innerHTML = `
          <td style="border: 1px solid #ccc; padding: 8px;">${entry.date}</td>
          <td style="border: 1px solid #ccc; padding: 8px;">${entry.weight}</td>
        `;
        table.appendChild(row);
      });

      const weights = result.data.map(entry => entry.weight);
      const dates = result.data.map(entry => new Date(entry.date));

      const minWeight = Math.min(...weights);
      const maxWeight = Math.max(...weights);
      const startingWeight = weights[0];
      const currentWeight = weights[weights.length - 1];
      const oneMonthAgoDate = new Date();
      oneMonthAgoDate.setMonth(oneMonthAgoDate.getMonth() - 1);

      let weightOneMonthAgo = "N/A";
      for (let i = weights.length - 1; i >= 0; i--) {
        if (dates[i] <= oneMonthAgoDate) {
          weightOneMonthAgo = weights[i];
          break;
        }
      }

      document.getElementById("current-weight-big").textContent = currentWeight ? `${currentWeight} kg` : "N/A";
      document.getElementById("current-weight").textContent = currentWeight || "N/A";
      document.getElementById("target-weight").textContent = targetWeight || "N/A";
      document.getElementById("weight-one-month-ago").textContent = weightOneMonthAgo;

      updateBMIProgress(currentWeight, userHeight);

      const goalMessage = document.getElementById("goal-message");
      if (currentWeight && targetWeight) {
        const diff = Math.abs(currentWeight - targetWeight).toFixed(1);
        if (diff < 0.1) {
          goalMessage.innerHTML = 'Good job! You’ve reached your goal weight!';
        } else if (diff < 2) {
          goalMessage.innerHTML = `Almost there! You are <span class="gradient-text fw-bold">${diff} kg</span> away from your target weight.`;
        } else {
          goalMessage.innerHTML = `Keep going! You are <span class="gradient-text fw-bold">${diff} kg</span> away from your target weight.`;
        }
      }

      const ctx = document.getElementById("weight-chart").getContext("2d");
      new Chart(ctx, {
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
              title: {
                display: true,
                text: "Date"
              }
            },
            y: {
              title: {
                display: true,
                text: "Weight (kg)"
              },
              beginAtZero: false,
              min: Math.floor(minWeight / 5) * 5 - 5,
              max: Math.floor(maxWeight / 5) * 5 + 5,
              ticks: {
                stepSize: 5
              }
            }
          }
        }
      });
    });
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