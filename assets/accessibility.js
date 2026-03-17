document.addEventListener("DOMContentLoaded", () => {
  const button = document.getElementById("fontToggle");

  if (!button) return;

  const saved = localStorage.getItem("fontPreference");

  if (saved === "system") {
    document.body.classList.add("system-font");
    button.setAttribute("aria-pressed", "true");
  }

  button.addEventListener("click", () => {
    const active = document.body.classList.toggle("system-font");

    if (active) {
      localStorage.setItem("fontPreference", "system");
      button.setAttribute("aria-pressed", "true");
    } else {
      localStorage.setItem("fontPreference", "default");
      button.setAttribute("aria-pressed", "false");
    }
  });
});