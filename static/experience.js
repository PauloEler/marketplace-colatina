(() => {
  const skipLink = document.querySelector(".skip-link");
  const mainContent = document.querySelector("#conteudo-principal");
  skipLink?.addEventListener("click", () => {
    window.requestAnimationFrame(() => mainContent?.focus());
  });

  const imageContainers = [
    ".card-media",
    ".gallery-item",
    ".order-media",
    ".seller-product-media",
    ".owner-listing-media",
    ".checkout-product-media",
  ];

  const finishImageLoading = (container) => {
    container.classList.remove("is-image-loading");
    container.removeAttribute("aria-busy");
  };

  document.querySelectorAll(`${imageContainers.join(" img,")} img`).forEach((image) => {
    const container = image.closest(imageContainers.join(","));
    if (!container || image.complete) return;

    container.classList.add("is-image-loading");
    container.setAttribute("aria-busy", "true");
    image.addEventListener("load", () => finishImageLoading(container), { once: true });
    image.addEventListener("error", () => finishImageLoading(container), { once: true });
  });

  document.querySelectorAll("details").forEach((details) => {
    const summary = details.querySelector(":scope > summary");
    if (!summary) return;

    const syncExpandedState = () => summary.setAttribute("aria-expanded", String(details.open));
    syncExpandedState();
    details.addEventListener("toggle", syncExpandedState);
  });

  document.querySelectorAll(".desktop-nav, .mobile-nav-panel").forEach((navigation) => {
    const matchingLinks = [...navigation.querySelectorAll("a")].filter((link) => {
      const target = new URL(link.href, window.location.origin);
      return target.origin === window.location.origin && target.pathname === window.location.pathname;
    });
    const currentLink = matchingLinks.find((link) => !link.textContent.includes("Anunciar")) || matchingLinks[0];
    currentLink?.setAttribute("aria-current", "page");
  });

  const resetSubmittingState = () => {
    document.querySelectorAll("form[aria-busy='true']").forEach((form) => {
      form.removeAttribute("aria-busy");
    });
    document.querySelectorAll("form[data-submitting='true']").forEach((form) => {
      delete form.dataset.submitting;
    });
    document.querySelectorAll(".is-submitting").forEach((button) => {
      button.classList.remove("is-submitting");
      button.removeAttribute("aria-disabled");
      button.disabled = false;
    });
  };

  document.querySelectorAll("form[method='POST'], form[method='post']").forEach((form) => {
    form.addEventListener("submit", (event) => {
      const submitter = event.submitter;
      if (!submitter || submitter.disabled) return;
      if (form.dataset.submitting === "true") {
        event.preventDefault();
        return;
      }
      form.dataset.submitting = "true";

      window.setTimeout(() => {
        if (!document.documentElement.contains(submitter)) return;
        form.setAttribute("aria-busy", "true");
        submitter.classList.add("is-submitting");
        submitter.setAttribute("aria-disabled", "true");
        submitter.disabled = true;
      }, 300);
    });
  });

  window.addEventListener("pageshow", resetSubmittingState);
})();
