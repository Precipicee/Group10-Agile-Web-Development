let historyStack = [];

const backBtn = document.getElementById("back-button");
if (backBtn) {
  backBtn.addEventListener("click", () => {
    window.history.back();  
  });
}

document.addEventListener("DOMContentLoaded", () => {
  const menu = document.querySelector("#mobile-menu");
  const menuLinks = document.querySelector(".navbar__menu");

  menu.addEventListener("click", () => {
    menu.classList.toggle("is-active");
    menuLinks.classList.toggle("active");
  });
});

