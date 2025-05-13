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

window.addExerciseRow = addExerciseRow;
window.removeThisRow = removeThisRow;
