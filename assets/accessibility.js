document.addEventListener("DOMContentLoaded", () => {
  const button = document.getElementById("fontToggle");

  if (!button) return;

  function applyFontPreference(preference) {
    const useSystem = preference === "system";

    document.body.classList.toggle("system-font", useSystem);
    button.setAttribute("aria-pressed", useSystem ? "true" : "false");
    button.textContent = useSystem ? "Use OpenDyslexic font" : "Use system font";
  }

  const saved = localStorage.getItem("fontPreference") || "default";
  applyFontPreference(saved);

  button.addEventListener("click", () => {
    const current = localStorage.getItem("fontPreference") || "default";
    const next = current === "system" ? "default" : "system";

    localStorage.setItem("fontPreference", next);
    applyFontPreference(next);
  });
});