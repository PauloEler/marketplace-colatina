(() => {
  const carousels = document.querySelectorAll("[data-partner-carousel]");
  const prefersReducedMotion = window.matchMedia(
    "(prefers-reduced-motion: reduce)",
  ).matches;

  carousels.forEach((carousel) => {
    const track = carousel.querySelector(".partner-offers-viewport");
    const previous = carousel.querySelector("[data-carousel-prev]");
    const next = carousel.querySelector("[data-carousel-next]");

    if (!track || !previous || !next) {
      return;
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
