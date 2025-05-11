let historyStack = [];

const backBtn = document.getElementById("back-button");
if (backBtn) {
  backBtn.addEventListener("click", () => {
    window.history.back();  // 更适配 Jinja 多页面结构
  });
}
