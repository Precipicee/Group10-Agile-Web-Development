function addExerciseRow() {
  const container = document.getElementById("exerciseContainer");
  const row = document.createElement("div");
  row.classList.add("exercise__entry");

  row.innerHTML = `
    <input type="text" name="exercise[]" placeholder="e.g. swimming" />
    <input type="number" name="duration[]" placeholder="Duration (min)" min="1" />
    <select name="intensity[]">
      <option value="">Intensity</option>
      <option value="light">Light</option>
      <option value="moderate">Moderate</option>
      <option value="intense">Intense</option>
    </select>
    <button type="button" class="remove-entry-btn" onclick="removeThisRow(this)">−</button>
  `;

  container.appendChild(row);
}

function removeThisRow(button) {
  const row = button.parentNode;
  const container = document.getElementById("exerciseContainer");
  if (container.children.length > 1) {
    container.removeChild(row);
  } else {
    alert("At least one activity must remain.");
  }
}

document.addEventListener("DOMContentLoaded", () => {
  const dateInput = document.getElementById("date");
  const today = new Date();
  const past = new Date();
  past.setDate(today.getDate() - 180);

  const toYMD = d => d.toISOString().split('T')[0];
  dateInput.max = toYMD(today);
  dateInput.min = toYMD(past);
  if (!dateInput.value) dateInput.value = toYMD(today);

  dateInput.addEventListener("change", () => {
    const selected = new Date(dateInput.value);
    if (selected > today) {
      alert("Future date is not allowed.");
      dateInput.value = toYMD(today);
    } else if (selected < past) {
      alert("Date is too far in the past.");
      dateInput.value = toYMD(today);
    }
  });

  const viewHistoryBtn = document.getElementById("view-history");
  if (viewHistoryBtn) {
    viewHistoryBtn.addEventListener("click", e => {
      e.preventDefault();
      window.location.href = "/history";
    });
  }

  const form = document.getElementById("recordForm");
  form.addEventListener("submit", async function (e) {
    e.preventDefault(); // Prevent default submit

    const date = document.getElementById("date").value;

    try {
      const response = await fetch(`/check_existing_record?date=${encodeURIComponent(date)}`);
      const result = await response.json();

      if (result.exists) {
        const confirmed = confirm("A record for this date already exists. Do you want to overwrite it?");
        if (!confirmed) return;
      }

      this.submit(); // If confirmed or no existing data, proceed
    } catch (err) {
      alert("Error checking existing record. Please try again.");
      console.error(err);
    }
  });
});

  document.addEventListener('DOMContentLoaded', function () {
    const calendarEl = document.getElementById("calendar");
    const calendar = new FullCalendar.Calendar(calendarEl, {
      initialView: "dayGridMonth",
      selectable: true,
      dateClick: function (info) {
        loadRecordDetails(info.dateStr);
      }
    });

    calendar.render();
    markRecordDates();

    const today = new Date().toISOString().split("T")[0];
    loadRecordDetails(today);

    async function markRecordDates() {
      const res = await fetch('/record_dates');
      const result = await res.json();
      if (result.status === "success") {
        result.dates.forEach(dateStr => {
          calendar.addEvent({
            title: "📌",
            start: dateStr,
            allDay: true,
            display: 'background',
            backgroundColor: '#ffcccc'
          });
        });
      }
    }

    async function loadRecordDetails(dateStr) {
      const res = await fetch(`/record_details/${dateStr}`);
      const result = await res.json();

      document.getElementById("record-date").textContent = dateStr;
      document.getElementById("record-weight").textContent = "—";
      document.getElementById("record-breakfast").textContent = "—";
      document.getElementById("record-lunch").textContent = "—";
      document.getElementById("record-dinner").textContent = "—";

      const tableBody = document.getElementById("exercise-table").querySelector("tbody");
      tableBody.innerHTML = "";

      if (result.status === "success") {
        const d = result.data;
        document.getElementById("record-weight").textContent = d.weight || "—";
        document.getElementById("record-breakfast").textContent = d.breakfast || "—";
        document.getElementById("record-lunch").textContent = d.lunch || "—";
        document.getElementById("record-dinner").textContent = d.dinner || "—";

        if (d.exercises && d.exercises.length > 0) {
          d.exercises.forEach(e => {
            const row = document.createElement("tr");
            row.innerHTML = `<td>${e.type}</td><td>${e.duration}</td><td>${e.intensity}</td>`;
            tableBody.appendChild(row);
          });
        } else {
          tableBody.innerHTML = `<tr><td colspan="3" class="empty-msg">No exercises</td></tr>`;
        }
      } else {
        tableBody.innerHTML = `<tr><td colspan="3" class="empty-msg">No record found</td></tr>`;
      }
      
      
      fetch(`/calorie_summary/${dateStr}`)
        .then(response => response.json())
        .then(data => {
          document.getElementById("mealCalories").innerText = data.total_calories.toFixed(1) + " kcal";
          document.getElementById("burnedCalories").innerText = data.calories_burned.toFixed(1) + " kcal";
          document.getElementById("netCalories").innerText = (data.total_calories - data.calories_burned).toFixed(1) + " kcal";
        })
        .catch(() => {
          document.getElementById("mealCalories").innerText = "N/A";
          document.getElementById("burnedCalories").innerText = "N/A";
          document.getElementById("netCalories").innerText = "N/A";
        });



    }
  });
  

window.addExerciseRow = addExerciseRow;
window.removeThisRow = removeThisRow;
