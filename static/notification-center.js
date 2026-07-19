document.addEventListener("DOMContentLoaded", () => {
  const center = document.querySelector("[data-notification-center]");
  if (!center) return;

  document.addEventListener("click", (event) => {
    if (center.open && !center.contains(event.target)) center.open = false;
  });

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && center.open) {
      center.open = false;
      center.querySelector("summary")?.focus();
    }
  });
});
