let historyStack = [];

function loadPage(page) {
  fetch(`/static/html/${page}.html`)
    .then(res => res.text())
    .then(html => {
      document.getElementById("app").innerHTML = html;
      setupEventListeners(page);
      window.scrollTo(0, 0);
      if (historyStack[historyStack.length - 1] !== page) {
        historyStack.push(page);
      }
    });
}

function setupEventListeners(page) {
  // === Hero Page ===
  if (page === "intro") {
    const startBtn = document.getElementById("btn-start");
    if (startBtn) {
      startBtn.addEventListener("click", () => loadPage("services"));
    }
  }
  
  // === Services Page ===
  if (page === "services") {
    const recordBtn = document.getElementById("btn-record");
    const reportBtn = document.getElementById("btn-report");
    if (recordBtn) recordBtn.addEventListener("click", () => loadPage("upload"));
    if (reportBtn) reportBtn.addEventListener("click", () => loadPage("visualise"));
  }

  // === Report Page ===
  if (page === "visualise") {
    const weightBtn = document.getElementById("btn-weight");
    if (weightBtn) {
      weightBtn.addEventListener("click", () => loadPage("weight"));
    }
    
    const exerciseBtn = document.getElementById("btn-exercise-report");
    if (exerciseBtn) {
      exerciseBtn.addEventListener("click", () => loadPage("exercise"));
    }  
  }
  
  // === Weight Report Page ===
  if (page === "weight") {
    fetch("/weight_data")
      .then(res => res.json())
      .then(result => {
        if (result.status !== "success") {
          alert("Failed to load weight data");
          return;
        }
  
        const table = document.getElementById("weight-table-body");
        table.innerHTML = "";
  
        result.data.forEach(entry => {
          const row = document.createElement("tr");
          row.innerHTML = `
            <td>${entry.date}</td>
            <td>${entry.weight}</td>
          `;
          table.appendChild(row);
        });

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
                }
              }
            }
          }
        })
      });
  }

// === Exercise Report Page ===
if (page === "exercise") {

// Weekly Exercise Goal Table
fetch('/api/exercise_goal_progress')
  .then(res => res.json())
  .then(data => {
    if (data.status !== "success") {
      console.error("Failed to load goal progress");
      return;
    }

    // Add motivational message above the table
    const messageEl = document.getElementById("goalMessage");
    if (data.remaining <= 0) {
      messageEl.textContent = "🎉 Congratulations! You've met your goal for the week! 🎉";
      messageEl.style.color = "green";
    } else {
      messageEl.textContent = `Keep going! You're ${data.remaining} minutes away from your goal. 💪`;
      messageEl.style.color = "orangered";
    }
setTimeout(() => {
  messageEl.classList.add("visible");
}, 50);

    // Fill in table values
    document.getElementById("goal-minutes").textContent = data.goal;
    document.getElementById("completed-minutes").textContent = data.completed;
    document.getElementById("remaining-minutes").textContent = data.remaining;
  });


  // Line Chart: Exercise Over Time
  fetch("/api/exercise_data")
    .then(res => res.json())
    .then(result => {
      if (!result.labels || !result.minutes) {
        alert("Failed to load exercise data");
        return;
      }

      const ctxLine = document.getElementById("exerciseChart").getContext("2d");

      new Chart(ctxLine, {
        type: "line",
        data: {
          labels: result.labels,
          datasets: [{
            label: "Minutes of Exercise",
            data: result.minutes,
            borderColor: "rgba(0, 200, 200, 1)",
            backgroundColor: "rgba(0, 200, 200, 0.2)",
            fill: true,
            tension: 0.3
          }]
        },
        options: {
          responsive: true,
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
                text: "Minutes"
              },
              beginAtZero: true
            }
          }
        }
      });
    });

  // Pie Chart: Exercise Type Breakdown
  fetch("/api/exercise_type_breakdown")
    .then(res => res.json())
    .then(data => {
      if (!data.labels || !data.minutes) {
        alert("Failed to load exercise breakdown");
        return;
      }

      const ctxPie = document.getElementById("typeBreakdownChart").getContext("2d");

      new Chart(ctxPie, {
        type: "pie",
        data: {
          labels: data.labels,
          datasets: [{
            label: "Total Minutes by Type",
            data: data.minutes,
            backgroundColor: [
              "#FF6384", "#36A2EB", "#FFCE56",
              "#4BC0C0", "#9966FF", "#FF9F40"
            ],
            borderColor: "#fff",
            borderWidth: 1
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
                  const label = context.label || '';
                  const value = context.parsed || 0;
                  return `${label}: ${value} min`;
                }
              }
            }
          }
        }
      });
    });

  // Pie Chart: Exercise Intensity Breakdown
  fetch("/api/exercise_intensity_breakdown")
    .then(res => res.json())
    .then(data => {
      if (!data.labels || !data.minutes) {
        alert("Failed to load intensity breakdown");
        return;
      }

      const ctxIntensity = document.getElementById("intensityBreakdownChart").getContext("2d");

      new Chart(ctxIntensity, {
        type: "pie",
        data: {
          labels: data.labels,
          datasets: [{
            label: "Total Minutes by Intensity",
            data: data.minutes,
            backgroundColor: ["#FF6384", "#36A2EB", "#FFCE56"],
            borderColor: "#fff",
            borderWidth: 1
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
                  const label = context.label || '';
                  const value = context.parsed || 0;
                  return `${label}: ${value} min`;
                }
              }
            }
          }
        }
      });
    });
}
  
  // === Sign In Page ===
  if (page === "signin") {
    const signinForm = document.getElementById("signinForm");
    if (signinForm) {
      signinForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const res = await fetch("/signin", {
          method: "POST",
          body: new FormData(e.target),
        });

        const result = await res.json();
        if (result.status === "success") {
          window.location.href = "/";
        } else {
          alert(result.message);
        }
      });
    }

    const signupLink = document.getElementById("go-signup");
    if (signupLink) {
      signupLink.addEventListener("click", (e) => {
        e.preventDefault();
        loadPage("signup");
      });
    }
  }

  // === Sign Up Page ===
  if (page === "signup") {
    document.getElementById("go-signin").addEventListener("click", (e) => {
      e.preventDefault();
      loadPage("signin");
    });

    document.getElementById("signupForm").addEventListener("submit", async (e) => {
      e.preventDefault();
      const res = await fetch("/signup", {
        method: "POST",
        body: new FormData(e.target),
      });
      const text = await res.text();
      if (text.includes("success")) {
        loadPage("basicinfo");
      } else {
        alert(text);
      }
    });
  }

  // === Basic Info Page ===
  if (page === "basicinfo") {
    loadAvatarImages();

    document.getElementById("basicForm").addEventListener("submit", async (e) => {
      e.preventDefault();
      const res = await fetch("/basicinfo", {
        method: "POST",
        body: new FormData(e.target),
      });

      const resultText = await res.text();
      if (resultText.includes("success")) {
        window.location.href = "/";
      } else {
        console.error("Backend Error:", resultText);
        alert("Failed to save profile: " + resultText);
      }
    });
  }

// === Profile Page ===
if (page === "profile") {
  fetch("/profile_data")
    .then(res => res.json())
    .then(result => {
      if (result.status !== "success") {
        alert("Failed to load profile");
        return;
      }

      const data = result.data;
      document.getElementById("profile-username").textContent = data.username || "";
      document.getElementById("profile-avatar").src = data.avatar
        ? `/static/userimages/${data.avatar}`
        : "/static/userimages/default.png";
      document.getElementById("profile-birthday").textContent = data.birthday || "-";
      document.getElementById("profile-age").textContent = data.age || "-";
      document.getElementById("profile-gender").textContent = data.gender || "-";
      document.getElementById("profile-height").textContent = data.height ? `${data.height} cm` : "-";
      document.getElementById("profile-weight-reg").textContent = data.weight_reg ? `${data.weight_reg} kg` : "-";
      document.getElementById("profile-register-date").textContent = data.register_date || "-";
      document.getElementById("profile-weight-now").textContent = data.current_weight ? `${data.current_weight} kg` : "-";
      document.getElementById("profile-weight-target").textContent = data.target_weight ? `${data.target_weight} kg` : "-";
      document.getElementById("profile-bmi-reg").textContent = data.bmi_reg || "-";
      document.getElementById("profile-bmi-now").textContent = data.bmi_now || "-";
      document.getElementById("profile-target-weight-days").textContent = data.target_weight_time_days || "-";
      document.getElementById("profile-exercise-weekly").textContent = data.target_exercise_time_per_week || "-";
      document.getElementById("profile-exercise-days").textContent = data.target_exercise_timeframe_days || "-";
      
      window.profileOriginalData = data;
    });

  const editableFields = [
    { id: "profile-birthday", key: "birthday", type: "date" },
    { id: "profile-gender", key: "gender", type: "select" },
    { id: "profile-height", key: "height", type: "number", unit: " cm" },
    { id: "profile-weight-reg", key: "weight_reg", type: "number", unit: " kg" },
    { id: "profile-weight-target", key: "target_weight", type: "number", unit: " kg" },
    { id: "profile-target-weight-days", key: "target_weight_time_days", type: "number" },
    { id: "profile-exercise-weekly", key: "target_exercise_time_per_week", type: "number" },
    { id: "profile-exercise-days", key: "target_exercise_timeframe_days", type: "number" }
  ];
    

  const editBtn = document.getElementById("edit-profile-btn");
  editBtn.addEventListener("click", async () => {
    const editing = editBtn.textContent === "✏️";
    editBtn.textContent = editing ? "💾" : "✏️";

    if (editing) {
      // Switch to editing mode
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
          input.value = value != null ? value : "";
        }

        input.className = "profile-edit-input";
        container.innerHTML = "";
        container.appendChild(input);
      });

    } else {
      // Save mode
      const payload = {};

      editableFields.forEach(field => {
        const input = document.querySelector(`#${field.id} input, #${field.id} select`);
        if (input) {
          let val = input.value.trim();
          if (field.type === "number") val = parseFloat(val);
          payload[field.key] = val;
        }
      });

      alert("Data to upload - for debug:\n" + JSON.stringify(payload, null, 2));

      const res = await fetch("/update_profile_fields", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });

      const result = await res.json();
      if (result.status === "success") {
        alert("save successful！ - for debug");
        loadPage("profile");
      } else {
        alert("fail to save - for debug: " + result.message);
        console.error(result.debug); 
      }
    }
  });
}









// === Upload Page ===
if (page === "upload") {
  const form = document.getElementById("recordForm");
  if (!form) return;

  // add
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
  

  // delete
  function removeThisRow(button) {
    const row = button.parentNode;
    const container = document.getElementById("exerciseContainer");
    if (container.children.length > 1) {
      container.removeChild(row);
    } else {
      alert("At least one activity must remain.");
    }
  }

  // submit
  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const exercises = document.getElementsByName("exercise[]");
    const durations = document.getElementsByName("duration[]");
    const intensities = document.getElementsByName("intensity[]");
    let combined = [];

    for (let i = 0; i < exercises.length; i++) {
      const name = exercises[i].value.trim();
      const duration = durations[i].value.trim();
      const level = intensities[i].value.trim();
      if (name && duration) {
        combined.push(`${name} (${duration}min, ${level || 'unknown'})`);
      }
    }


    const formData = new FormData(form);
    formData.set("exercise", combined.join("; "));

    // upload
    const res = await fetch("/add_record", {
      method: "POST",
      body: formData
    });

    const result = await res.json();

    if (result.status === "success") {
      alert("Record saved!");
      loadPage("services");
    } else if (result.status === "exists") {
      if (confirm("This date already has a record. Do you want to overwrite it?")) {
        const updateRes = await fetch("/update_record", {
          method: "POST",
          body: formData
        });
        const updateResult = await updateRes.json();
        if (updateResult.status === "success") {
          alert("Record updated.");
          loadPage("services");
        } else {
          alert("Update failed: " + updateResult.message);
        }
      }
    } else {
      alert("Error: " + result.message);
    }
  });

  // onclick 
  window.addExerciseRow = addExerciseRow;
  window.removeThisRow = removeThisRow;

  // View History button event
  document.getElementById("view-history").addEventListener("click", (e) => {
    e.preventDefault();
    loadPage("history");
});

  
  
}
// === Friends Page ===
if (page === "friends") {
  console.log("👥 Friends page JS loaded");

  document.getElementById("btn-send-request").addEventListener("click", async () => {
    const username = document.getElementById("friend-username").value.trim();
    if (!username) return alert("Please enter a username");

    const res = await fetch("/add_friend", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ to_username: username })  
    });
    

    const result = await res.json();
    alert(result.message || "Friend request sent");
    loadPage("friends");  // reload page
  });

  fetch("/get_friend_data")
    .then(res => res.json())
    .then(data => {
      renderFriendRequests("received", data.received_requests, "received-requests-container");
      renderFriendRequests("sent", data.sent_requests, "sent-requests-container");
      renderFriendList(data.friends);
    });
}

function renderFriendRequests(type, list, containerId) {
  const container = document.getElementById(containerId);
  if (!list.length) {
    container.innerHTML = `<p>No ${type} requests.</p>`;
    return;
  }

  container.innerHTML = "";
  list.forEach(req => {
    const div = document.createElement("div");
    div.className = "friend-request-entry";
    div.innerHTML = `
      <span>${type === "received" ? "From" : "To"}: ${type === "received" ? req.from_user : req.to_user}</span>
      ${type === "received" ? `
        <button onclick="handleRequest(${req.id}, 'accept')">Accept</button>
        <button onclick="handleRequest(${req.id}, 'reject')">Reject</button>
      ` : `<span>Status: ${req.status}</span>`}
    `;
    container.appendChild(div);
  });
}

function renderFriendList(friends) {
  const container = document.getElementById("friends-list-container");
  if (!friends.length) {
    container.innerHTML = "<p>You have no friends yet.</p>";
    return;
  }

  container.innerHTML = "";
  friends.forEach(f => {
    const div = document.createElement("div");
    div.className = "friend-entry";
    div.textContent = f.username;
    container.appendChild(div);
  });
}

async function handleRequest(requestId, action) {
  const res = await fetch(`/respond_request`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ request_id: requestId, action })
  });

  const result = await res.json();
  alert(result.message || "Updated");
  loadPage("friends");
}
window.handleRequest = handleRequest;


 // === History Page ===
if (page === "history") {
  console.log("📅 History page JS running");

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
    try {
      const res = await fetch('/record_dates');
      const result = await res.json();
  
      if (result.status === "success") {
        const dates = result.dates;
  
        dates.forEach(dateStr => {
          calendar.addEvent({
            title: "📌",  // simple mark
            start: dateStr,
            allDay: true,
            display: 'background',  
            backgroundColor: '#ffcccc'  
          });
        });
      }
    } catch (err) {
      console.error("Error loading marked dates", err);
    }
  }
  

  async function loadRecordDetails(dateStr) {
    try {
      const res = await fetch(`/record_details/${dateStr}`);
      const result = await res.json();
  
      if (result.status === "success") {
        const d = result.data;
  
        document.getElementById("record-date").textContent = dateStr;
        document.getElementById("record-weight").textContent = d.weight || "—";
        document.getElementById("record-breakfast").textContent = d.breakfast || "—";
        document.getElementById("record-lunch").textContent = d.lunch || "—";
        document.getElementById("record-dinner").textContent = d.dinner || "—";
  
        // exercises data from backend
        const tableBody = document.getElementById("exercise-table").querySelector("tbody");
        tableBody.innerHTML = "";
  
        if (d.exercises && d.exercises.length > 0) {
          d.exercises.forEach(e => {
            const row = document.createElement("tr");
            row.innerHTML = `
              <td>${e.type}</td>
              <td>${e.duration}</td>
              <td>${e.intensity}</td>
            `;
            tableBody.appendChild(row);
          });
        } else {
          const row = document.createElement("tr");
          row.innerHTML = `<td colspan="3" style="text-align: center;">No exercises</td>`;
          tableBody.appendChild(row);
        }
  
      } else {
        // Clear the display
        document.getElementById("record-date").textContent = dateStr;
        document.getElementById("record-weight").textContent = "—";
        document.getElementById("record-breakfast").textContent = "—";
        document.getElementById("record-lunch").textContent = "—";
        document.getElementById("record-dinner").textContent = "—";
  
        const tableBody = document.getElementById("exercise-table").querySelector("tbody");
        tableBody.innerHTML = `<tr><td colspan="3" style="text-align: center;">No exercises</td></tr>`;
      }
  
    } catch (err) {
      console.error("Failed to fetch record:", err);
      document.getElementById("recordDetails").innerHTML = `
        <h2>Record Details</h2>
        <p style="color: red;">Error loading data. Please try again.</p>
      `;
    }
  }
  
}







  // === Avatar Picker ===
  async function loadAvatarImages() {
    const container = document.getElementById("avatar-options");
    if (!container) return;
    const images = ["a.png", "b.png", "c.png", "d.png", "e.png", "f.png"];
    images.forEach(img => {
      const image = document.createElement("img");
      image.src = `/static/userimages/${img}`;
      image.classList.add("avatar-option");
      image.onclick = () => {
        document.getElementById("selected-avatar").value = img;
        document.querySelectorAll(".avatar-option").forEach(i => i.classList.remove("selected"));
        image.classList.add("selected");
      };
      container.appendChild(image);
    });
  }
}





function waitForUsernameButton(attempts = 10) {
  const usernameBtn = document.getElementById("navbar-username");
  if (usernameBtn) {
    usernameBtn.style.cursor = "pointer";
    usernameBtn.addEventListener("click", () => {
      loadPage("profile");
    });
  } else if (attempts > 0) {
    setTimeout(() => waitForUsernameButton(attempts - 1), 200);
  }
}

document.addEventListener("DOMContentLoaded", () => {
  loadPage("intro");

  const backBtn = document.getElementById("back-button");
  if (backBtn) {
    backBtn.addEventListener("click", () => {
      if (historyStack.length > 1) {
        historyStack.pop();
        const previous = historyStack[historyStack.length - 1];
        loadPage(previous);
      }
    });
  }
  const friendsBtn = document.getElementById("nav-friends");
  if (friendsBtn) {
    friendsBtn.addEventListener("click", () => {
      loadPage("friends");
    });
  }

  waitForUsernameButton(); // Retry attaching event to username span
})
