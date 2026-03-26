async function loadPartials() {
  const partials = [
    { url: "/nav.html", target: "nav-placeholder", required: true },
    { url: "/access.html", target: "access-placeholder", required: false },
    { url: "/latest-satire.html", target: "latest-satire-placeholder", required: false },
    { url: "/share.html", target: "share-placeholder", required: false },
    { url: "/foot.html", target: "footer-placeholder", required: false }
  ];

  try {
    const results = await Promise.all(
      partials.map(async ({ url, target, required }) => {
        const container = document.getElementById(target);

        if (!container) {
          if (required) {
            throw new Error(`Missing required placeholder: #${target}`);
          }
          return null;
        }

        try {
          const response = await fetch(url, { cache: "no-store" });

          if (!response.ok) {
            if (required) {
              throw new Error(`Failed to load ${url}: ${response.status} ${response.statusText}`);
            }

            console.warn(`Optional partial failed: ${url}: ${response.status} ${response.statusText}`);
            return null;
          }

          const html = await response.text();
          return { container, html };
        } catch (error) {
          if (required) {
            throw error;
          }

          console.warn(`Optional partial failed: ${url}`, error);
          return null;
        }
      })
    );

    for (const result of results) {
      if (!result) continue;
      result.container.innerHTML = result.html;
    }
  } catch (error) {
    console.error("Partial load failed:", error);
  }

  buildEmailLink();
  loadAccessibilityScript();
  initSharePanel();
}

function buildEmailLink() {
  const emailContainer = document.getElementById("email-link");
  if (!emailContainer) return;

  const addressCodes = [
    99, 111, 110, 116, 97, 99, 116,
    64,
    98, 115, 116, 101, 101, 110, 107, 97, 109, 112, 119, 114, 105, 116, 101, 115,
    46,
    99, 111, 109
  ];

  const subjectCodes = [
    87, 101, 98, 115, 105, 116, 101, 32, 67, 111, 110, 116, 97, 99, 116
  ];

  const decode = (codes) => String.fromCharCode(...codes);

  const email = decode(addressCodes);
  const subject = decode(subjectCodes);

  const link = document.createElement("a");
  link.href = `mailto:${email}?subject=${encodeURIComponent(subject)}`;
  link.textContent = email;

  emailContainer.replaceChildren(link);
}

function loadAccessibilityScript() {
  const accessContainer = document.getElementById("access-placeholder");

  if (!accessContainer) return;
  if (!accessContainer.innerHTML.trim()) return;
  if (document.querySelector('script[src="/assets/accessibility.js"]')) return;

  const script = document.createElement("script");
  script.src = "/assets/accessibility.js";
  script.defer = true;
  document.body.appendChild(script);
}

function initSharePanel() {
  if (typeof window.initSharePanel === "function") {
    window.initSharePanel();
  }
}

document.addEventListener("DOMContentLoaded", loadPartials);