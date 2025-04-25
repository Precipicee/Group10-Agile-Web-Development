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
        document.getElementById("profile-age").textContent = data.age || "-";
        document.getElementById("profile-gender").textContent = data.gender || "-";
        document.getElementById("profile-weight-reg").textContent = data.weight_reg ? `${data.weight_reg} kg` : "-";
        document.getElementById("profile-register-date").textContent = data.register_date || "-";
        document.getElementById("profile-weight-now").textContent = data.current_weight ? `${data.current_weight} kg` : "-";
        document.getElementById("profile-weight-target").textContent = data.target_weight ? `${data.target_weight} kg` : "-";
        document.getElementById("profile-bmi-reg").textContent = data.bmi_reg || "-";
        document.getElementById("profile-bmi-now").textContent = data.bmi_now || "-";

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
    const intensities = document.getElementsByName("intensity[]");
    let combined = [];

    for (let i = 0; i < exercises.length; i++) {
      const name = exercises[i].value.trim();
      const level = intensities[i].value.trim();
      if (name) {
        combined.push(`${name} (${level || 'unknown'})`);
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

  waitForUsernameButton(); // Retry attaching event to username span
});
