function initAccessibility() {
  const button = document.getElementById("fontToggle");
  const status = document.getElementById("font-status");

  if (!button) return;

  function announceStatus(message) {
    if (!status) return;
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

    if (status) {
      const message = useSystem ? "System font active" : "OpenDyslexic font active";

      if (announce) {
        announceStatus(message);
      } else {
        status.textContent = message;
      }
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
}

initAccessibility();