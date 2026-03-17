document.addEventListener("DOMContentLoaded", () => {
  const button = document.getElementById("fontToggle");
  const status = document.getElementById("font-status");

  if (!button || !status) return;

  function announceStatus(message) {
    status.textContent = "";
    window.setTimeout(() => {
      status.textContent = message;
    }, 50);
  }

  function applyFontPreference(preference, announce = false) {
    const useSystem = preference === "system";

    document.body.classList.toggle("system-font", useSystem);
    button.setAttribute("aria-pressed", useSystem ? "true" : "false");
    button.textContent = useSystem ? "Use OpenDyslexic font" : "Use system font";

    if (announce) {
      announceStatus(useSystem ? "System font active" : "OpenDyslexic font active");
    } else {
      status.textContent = useSystem ? "System font active" : "OpenDyslexic font active";
    }
  }

  const saved = localStorage.getItem("fontPreference") || "default";
  applyFontPreference(saved, false);

  button.addEventListener("click", () => {
    const current = localStorage.getItem("fontPreference") || "default";
    const next = current === "system" ? "default" : "system";

    localStorage.setItem("fontPreference", next);
    applyFontPreference(next, true);
  });
});