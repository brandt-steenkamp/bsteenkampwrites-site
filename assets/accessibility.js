function initAccessibility() {
  const body = document.body;
  const fontToggle = document.getElementById("fontToggle");
  const status = document.getElementById("accessibility-status");
  const widthRadios = document.querySelectorAll('input[name="reading-width"]');

  function announceStatus(message) {
    if (!status) return;

    status.textContent = "";

    window.setTimeout(() => {
      status.textContent = message;
    }, 50);
  }

  function applyFontPreference(preference, announce = false) {
    const useDyslexic = preference === "dyslexic";

    body.classList.toggle("font-dyslexic", useDyslexic);

    if (fontToggle) {
      fontToggle.setAttribute("aria-pressed", useDyslexic ? "true" : "false");
      fontToggle.textContent = useDyslexic
        ? "Use system font"
        : "Use OpenDyslexic font";
    }

    const message = useDyslexic
      ? "OpenDyslexic font active"
      : "System font active";

    if (announce) {
      announceStatus(message);
    } else if (status) {
      status.textContent = message;
    }
  }

  function applyWidthPreference(preference, announce = false) {
    const validWidths = ["standard", "narrow", "extra"];
    const width = validWidths.includes(preference) ? preference : "standard";

    body.classList.remove("width-standard", "width-narrow", "width-extra");
    body.classList.add(`width-${width}`);

    widthRadios.forEach((radio) => {
      radio.checked = radio.value === width;
    });

    let message = "Standard reading width active";

    if (width === "narrow") {
      message = "Narrow reading width active";
    } else if (width === "extra") {
      message = "Extra narrow reading width active";
    }

    if (announce) {
      announceStatus(message);
    }
  }

  const savedFont = localStorage.getItem("fontPreference") || "system";
  const savedWidth = localStorage.getItem("readingWidth") || "standard";

  applyFontPreference(savedFont, false);
  applyWidthPreference(savedWidth, false);

  if (fontToggle) {
    fontToggle.addEventListener("click", () => {
      const current = localStorage.getItem("fontPreference") || "system";
      const next = current === "dyslexic" ? "system" : "dyslexic";

      localStorage.setItem("fontPreference", next);
      applyFontPreference(next, true);
    });
  }

  widthRadios.forEach((radio) => {
    radio.addEventListener("change", () => {
      if (!radio.checked) return;

      localStorage.setItem("readingWidth", radio.value);
      applyWidthPreference(radio.value, true);
    });
  });
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", initAccessibility);
} else {
  initAccessibility();
}