(() => {
  const carousels = document.querySelectorAll("[data-partner-carousel]");
  const prefersReducedMotion = window.matchMedia(
    "(prefers-reduced-motion: reduce)",
  ).matches;

  const getDevice = () =>
    window.matchMedia("(max-width: 767px)").matches ? "mobile" : "desktop";

  const sendAnalytics = (carousel, eventType, offerId) => {
    const endpoint = carousel.dataset.analyticsEndpoint;
    const csrfToken = carousel.dataset.analyticsCsrf;
    if (!endpoint || !csrfToken || !offerId) {
      return;
    }

    const payload = JSON.stringify({
      event_type: eventType,
      offer_id: offerId,
      device: getDevice(),
      source: "home",
      csrf_token: csrfToken,
    });
    const body = new Blob([payload], { type: "application/json" });

    if (navigator.sendBeacon?.(endpoint, body)) {
      return;
    }
    window.fetch(endpoint, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: payload,
      credentials: "same-origin",
      keepalive: true,
    }).catch(() => {});
  };

  carousels.forEach((carousel) => {
    const track = carousel.querySelector(".partner-offers-viewport");
    const previous = carousel.querySelector("[data-carousel-prev]");
    const next = carousel.querySelector("[data-carousel-next]");

    if (!track || !previous || !next) {
      return;
    }

    track.addEventListener("click", (event) => {
      const link = event.target.closest(".partner-offer-link");
      if (!link || !track.contains(link)) {
        return;
      }
      sendAnalytics(carousel, "click", link.dataset.destino);
    });

    if ("IntersectionObserver" in window) {
      const viewedOffers = new Set();
      const observer = new IntersectionObserver(
        (entries) => {
          entries.forEach((entry) => {
            if (!entry.isIntersecting || entry.intersectionRatio < 0.5) {
              return;
            }
            const offerId = entry.target.dataset.affiliateOffer;
            if (viewedOffers.has(offerId)) {
              return;
            }
            viewedOffers.add(offerId);
            sendAnalytics(carousel, "impression", offerId);
            observer.unobserve(entry.target);
          });
        },
        { threshold: 0.5 },
      );
      track
        .querySelectorAll("[data-affiliate-offer]")
        .forEach((card) => observer.observe(card));
    }

    const getStep = () => {
      const card = track.querySelector(".partner-offer-card");
      if (!card) {
        return track.clientWidth;
      }

      const styles = window.getComputedStyle(track);
      const gap = Number.parseFloat(styles.columnGap || styles.gap || "0");
      return card.getBoundingClientRect().width + gap;
    };

    const move = (direction) => {
      const step = getStep() * direction;
      const nearEnd = track.scrollLeft + track.clientWidth >= track.scrollWidth - 8;
      const nearStart = track.scrollLeft <= 8;

      if (direction > 0 && nearEnd) {
        track.scrollTo({ left: 0, behavior: "smooth" });
        return;
      }

      if (direction < 0 && nearStart) {
        track.scrollTo({ left: track.scrollWidth, behavior: "smooth" });
        return;
      }

      track.scrollBy({ left: step, behavior: "smooth" });
    };

    previous.addEventListener("click", () => move(-1));
    next.addEventListener("click", () => move(1));

    const activateControl = (event, direction) => {
      if (event.key !== "Enter" && event.key !== " ") {
        return;
      }

      event.preventDefault();
      move(direction);
    };

    previous.addEventListener("keydown", (event) => activateControl(event, -1));
    next.addEventListener("keydown", (event) => activateControl(event, 1));
    track.addEventListener("keydown", (event) => {
      if (event.key === "ArrowLeft") {
        event.preventDefault();
        move(-1);
      }
      if (event.key === "ArrowRight") {
        event.preventDefault();
        move(1);
      }
    });

    if (prefersReducedMotion) {
      return;
    }

    let timer = window.setInterval(() => move(1), 5200);

    const pause = () => {
      window.clearInterval(timer);
    };
    const resume = () => {
      window.clearInterval(timer);
      timer = window.setInterval(() => move(1), 5200);
    };

    carousel.addEventListener("mouseenter", pause);
    carousel.addEventListener("mouseleave", resume);
    carousel.addEventListener("focusin", pause);
    carousel.addEventListener("focusout", resume);
  });
})();
