(() => {
  "use strict";

  const message = document.querySelector("[data-city-balloon-message]");
  const source = document.querySelector("[data-city-balloon-phrases]");
  if (!message || !source) return;

  const phrases = Array.from(source.querySelectorAll("li"))
    .map((item) => item.textContent.trim())
    .filter(Boolean);
  const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
  if (phrases.length < 2 || reduceMotion.matches) return;

  let index = 0;
  let timer = null;
  const rotate = () => {
    index = (index + 1) % phrases.length;
    message.classList.add("is-changing");
    window.setTimeout(() => {
      message.textContent = phrases[index];
      message.classList.remove("is-changing");
    }, 180);
  };
  const start = () => {
    if (timer === null) timer = window.setInterval(rotate, 5200);
  };
  const stop = () => {
    if (timer !== null) window.clearInterval(timer);
    timer = null;
  };

  document.addEventListener("visibilitychange", () => {
    if (document.hidden) stop();
    else start();
  });
  reduceMotion.addEventListener("change", (event) => {
    if (event.matches) stop();
    else start();
  });
  start();
})();
