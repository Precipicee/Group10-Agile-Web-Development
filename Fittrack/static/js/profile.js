window.addEventListener("DOMContentLoaded", () => {
  initProfilePage();
});

function initProfilePage() {
  fetch("/profile_data")
    .then(res => res.json())
    .then(result => {
      if (result.status !== "success") {
        alert("Failed to load profile");
        return;
      }

      const data = result.data;
      window.profileOriginalData = data;

      document.getElementById("profile-username").textContent = data.username || "";
      document.getElementById("profile-avatar").src = data.avatar
        ? `/static/userimages/${data.avatar}`
        : "/static/userimages/default.png";

      updateDisplayMode(data);
    });

  const editBtn = document.getElementById("edit-profile-btn");

  const editableFields = [
    { id: "profile-birthday", key: "birthday", type: "date" },
    { id: "profile-gender", key: "gender", type: "select" },
    { id: "profile-height", key: "height", type: "number", unit: " cm", min: 1, step: 1 },
    { id: "profile-weight-reg", key: "weight_reg", type: "number", unit: " kg", min: 0.01, step: 0.01 },
    { id: "profile-weight-target", key: "target_weight", type: "number", unit: " kg", min: 0.01, step: 0.01 },
    { id: "profile-target-weight-days", key: "target_weight_time_days", type: "number", min: 1, step: 1 },
    { id: "profile-exercise-weekly", key: "target_exercise_time_per_week", type: "number", min: 1, step: 1 },
    { id: "profile-exercise-days", key: "target_exercise_timeframe_days", type: "number", min: 1, step: 1 }
  ];

  editBtn.addEventListener("click", async () => {
    const editing = editBtn.textContent === "✏️";

    if (editing) {
      editBtn.textContent = "💾";
      editableFields.forEach(field => {
        const container = document.getElementById(field.id);
        const value = window.profileOriginalData[field.key];

        let input;
        if (field.type === "select") {
          input = document.createElement("select");
          ["Male", "Female", "Other"].forEach(opt => {
            const option = document.createElement("option");
            option.value = opt;
            option.textContent = opt;
            if (opt === value) option.selected = true;
            input.appendChild(option);
          });
        } else {
          input = document.createElement("input");
          input.type = field.type;

          if (field.min !== undefined) input.min = field.min;
          if (field.step !== undefined) input.step = field.step;

          if (field.type === "date" && value) {
            const dateObj = new Date(value);
            const yyyy = dateObj.getFullYear();
            const mm = String(dateObj.getMonth() + 1).padStart(2, '0');
            const dd = String(dateObj.getDate()).padStart(2, '0');
            input.value = `${yyyy}-${mm}-${dd}`;
          } else {
            input.value = value != null ? value : "";
          }
        }

        input.className = "profile-edit-input";
        container.innerHTML = "";
        container.appendChild(input);
      });

    } else {
      // Save
      const payload = {};

      for (const field of editableFields) {
        const input = document.querySelector(`#${field.id} input, #${field.id} select`);
        if (input) {
          let val = input.value.trim();

          if (field.type === "number") {
            const floatVal = parseFloat(val);
            if (field.min !== undefined && floatVal < field.min) {
              alert(`${field.key} must be ≥ ${field.min}`);
              return; //  Stop save if invalid
            }
            val = floatVal;
          }

          payload[field.key] = val;
        }
      }

      console.log("Sending payload:", payload);

      const res = await fetch("/update_profile_fields", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });

      const result = await res.json();
      if (result.status === "success") {
        if (result.bmi) {
          window.profileOriginalData.bmi_now = result.bmi;
          window.profileOriginalData.bmi_reg = result.bmi;
        }
        if (result.age) {
          window.profileOriginalData.age = result.age;
        }

        Object.assign(window.profileOriginalData, payload);
        updateDisplayMode(window.profileOriginalData);
        editBtn.textContent = "✏️";  
      } else {
        alert("Save failed: " + result.message);
        console.error(result.debug);
      }
    }
  });
}

function updateDisplayMode(data) {
  const render = (val, unit = "") =>
    val !== undefined && val !== null && val !== "" ? `${val}${unit}` : "-";

  const formatDate = (d) => {
    try {
      const dateObj = new Date(d);
      return dateObj.toISOString().split("T")[0]; // yyyy-mm-dd
    } catch {
      return "-";
    }
  };

  document.getElementById("profile-birthday").textContent = formatDate(data.birthday);
  document.getElementById("profile-gender").textContent = render(data.gender);
  document.getElementById("profile-age").textContent = render(data.age);
  document.getElementById("profile-height").textContent = render(data.height, " cm");
  document.getElementById("profile-weight-reg").textContent = render(data.weight_reg, " kg");
  document.getElementById("profile-register-date").textContent = formatDate(data.register_date);
  document.getElementById("profile-weight-now").textContent = render(data.current_weight, " kg");
  document.getElementById("profile-weight-target").textContent = render(data.target_weight, " kg");
  document.getElementById("profile-bmi-reg").textContent = render(data.bmi_reg);
  document.getElementById("profile-bmi-now").textContent = render(data.bmi_now);
  document.getElementById("profile-target-weight-days").textContent = render(data.target_weight_time_days);
  document.getElementById("profile-exercise-weekly").textContent = render(data.target_exercise_time_per_week);
  document.getElementById("profile-exercise-days").textContent = render(data.target_exercise_timeframe_days);
}
