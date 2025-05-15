// helper function
function toTitleCase(str) {
  return str
    .toLowerCase()
    .split(" ")
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(" ");
}

function loadDietPageFeatures() {
  fetch('/api/recommended_calories')
    .then(res => res.json())
    .then(data => {
      if (data.error) {
        console.warn("Profile incomplete:", data.error);
        document.getElementById("recommended-calories").textContent = "Unavailable";
        document.getElementById("goal-message").textContent =
          "Please complete your profile to view your recommended intake.";
        return;
      }

      // Populate recommended intake
      document.getElementById("recommended-calories").textContent = `${data.recommended} kcal`;

      // Populate user stats
      document.getElementById("profile-age").textContent = data.age ?? "--";
      document.getElementById("profile-height").textContent = data.height ?? "--";
      document.getElementById("profile-weight").textContent = data.current_weight ?? "--";
      document.getElementById("profile-gender").textContent = data.gender ?? "--";

      // Populate goal and activity message
      document.getElementById("goal-type").textContent = toTitleCase(data.goal);
document.getElementById("activity-level").textContent = toTitleCase(data.activity_level.replace("_", " "));
    })
    .catch(err => {
      console.error("Error fetching recommended calorie info:", err);
    });
}

// Ensure it runs after page load
document.addEventListener("DOMContentLoaded", loadDietPageFeatures);
