(function () {
  "use strict";

  function getMetaContent(selector) {
    const element = document.querySelector(selector);
    if (!element) return "";
    return (element.getAttribute("content") || "").trim();
  }

  function getCanonicalUrl() {
    const canonical = document.querySelector('link[rel="canonical"]');
    const href = canonical ? canonical.getAttribute("href") : "";
    return href && href.trim() ? href.trim() : window.location.href;
  }

  function getPageTitle() {
    return (
      getMetaContent('meta[property="og:title"]') ||
      getMetaContent('meta[name="twitter:title"]') ||
      document.title ||
      ""
    ).trim();
  }

  function getPageDescription() {
    return (
      getMetaContent('meta[property="og:description"]') ||
      getMetaContent('meta[name="twitter:description"]') ||
      getMetaContent('meta[name="description"]') ||
      ""
    ).trim();
  }

  function getOgImage() {
    return (
      getMetaContent('meta[property="og:image"]') ||
      getMetaContent('meta[name="twitter:image"]') ||
      ""
    ).trim();
  }

  function absoluteUrl(url) {
    if (!url) return "";
    try {
      return new URL(url, window.location.href).href;
    } catch (error) {
      return "";
    }
  }

  function encode(value) {
    return encodeURIComponent(value || "");
  }

  function slugifyFilename(value) {
    const cleaned = (value || "")
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, "-")
      .replace(/^-+|-+$/g, "");

    return cleaned || "share-image";
  }

  function getStatusElement(panel) {
    if (!panel) return null;
    return panel.querySelector("#share-status") || panel.querySelector(".share-status");
  }

  function setStatus(panel, message) {
    const status = getStatusElement(panel);
    if (status) {
      status.textContent = message;
    }
  }

  function clearStatusLater(panel) {
    window.setTimeout(function () {
      const status = getStatusElement(panel);
      if (status) {
        status.textContent = "";
      }
    }, 4000);
  }

  function copyToClipboard(text) {
    if (navigator.clipboard && typeof navigator.clipboard.writeText === "function") {
      return navigator.clipboard.writeText(text);
    }

    return new Promise(function (resolve, reject) {
      const helper = document.createElement("textarea");
      helper.value = text;
      helper.setAttribute("readonly", "");
      helper.setAttribute("aria-hidden", "true");
      helper.style.position = "absolute";
      helper.style.left = "-9999px";
      document.body.appendChild(helper);
      helper.select();

      try {
        const success = document.execCommand("copy");
        document.body.removeChild(helper);

        if (success) {
          resolve();
        } else {
          reject(new Error("Copy command failed."));
        }
      } catch (error) {
        document.body.removeChild(helper);
        reject(error);
      }
    });
  }

  function buildShareData() {
    const url = getCanonicalUrl();
    const title = getPageTitle();
    const description = getPageDescription();
    const image = absoluteUrl(getOgImage());
    const text = description ? title + ": " + description : title;

    return {
      url: url,
      title: title,
      description: description,
      image: image,
      text: text
    };
  }

  function buildLinks(data) {
    return {
      x:
        "https://twitter.com/intent/tweet?text=" +
        encode(data.text) +
        "&url=" +
        encode(data.url),

      facebook:
        "https://www.facebook.com/sharer/sharer.php?u=" +
        encode(data.url),

      linkedin:
        "https://www.linkedin.com/sharing/share-offsite/?url=" +
        encode(data.url),

      whatsapp:
        "https://wa.me/?text=" +
        encode(data.text + " " + data.url),

      downloadImage: data.image
    };
  }

  function disableDownloadLink(panel, downloadLink) {
    if (!downloadLink) return;

    downloadLink.removeAttribute("href");
    downloadLink.setAttribute("aria-disabled", "true");

    downloadLink.addEventListener("click", function (event) {
      event.preventDefault();
      setStatus(panel, "No share image is available for this page.");
      clearStatusLater(panel);
    });
  }

  function wireShareLinks(panel) {
    if (!panel) return;
    if (panel.dataset.shareWired === "true") return;

    const shareData = buildShareData();
    const links = buildLinks(shareData);

    const xLink = panel.querySelector('[data-share="x"]');
    const facebookLink = panel.querySelector('[data-share="facebook"]');
    const linkedinLink = panel.querySelector('[data-share="linkedin"]');
    const whatsappLink = panel.querySelector('[data-share="whatsapp"]');
    const downloadLink = panel.querySelector('[data-share="download-image"]');
    const copyButton = panel.querySelector('[data-share="copy"]');

    if (xLink) {
      xLink.href = links.x;
      xLink.target = "_blank";
      xLink.rel = "noopener noreferrer";
    }

    if (facebookLink) {
      facebookLink.href = links.facebook;
      facebookLink.target = "_blank";
      facebookLink.rel = "noopener noreferrer";
    }

    if (linkedinLink) {
      linkedinLink.href = links.linkedin;
      linkedinLink.target = "_blank";
      linkedinLink.rel = "noopener noreferrer";
    }

    if (whatsappLink) {
      whatsappLink.href = links.whatsapp;
      whatsappLink.target = "_blank";
      whatsappLink.rel = "noopener noreferrer";
    }

    if (downloadLink) {
      if (links.downloadImage) {
        downloadLink.href = links.downloadImage;
        downloadLink.setAttribute("download", slugifyFilename(shareData.title) + ".png");
        downloadLink.removeAttribute("aria-disabled");
      } else {
        disableDownloadLink(panel, downloadLink);
      }
    }

    if (copyButton) {
      copyButton.addEventListener("click", function () {
        copyToClipboard(shareData.url)
          .then(function () {
            setStatus(panel, "Link copied.");
            clearStatusLater(panel);
          })
          .catch(function () {
            setStatus(panel, "Copy failed. Please copy the link manually.");
            clearStatusLater(panel);
          });
      });
    }

    panel.dataset.shareWired = "true";
  }

  function initSharePanel() {
    const panels = document.querySelectorAll(".share-panel");

    if (!panels.length) return;

    panels.forEach(function (panel) {
      wireShareLinks(panel);
    });
  }

  window.initSharePanel = initSharePanel;

  if (document.readyState !== "loading") {
    initSharePanel();
  }
})();