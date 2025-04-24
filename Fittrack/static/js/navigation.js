let historyStack = [];

function loadPage(page) {
  fetch(`/static/html/${page}.html`)
    .then(res => res.text())
    .then(html => {
      document.getElementById("app").innerHTML = html;
      setupEventListeners(page);
      window.scrollTo(0, 0);  // Scroll back to the top after loading each time.
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

  // === Report Page optional events ===
  if (page === "visualise") {
    const recordBtn = document.getElementById("btn-report-record");
    if (recordBtn) recordBtn.addEventListener("click", () => loadPage("upload"));

  }

}

document.addEventListener("DOMContentLoaded", () => {
  //  hero
  loadPage("intro");

  // Back button setup
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
});
