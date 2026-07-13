(() => {
  const announcement = document.querySelector("[data-announcement-id]");
  if (!announcement) return;

  const storageKey = `mercado-colatina:announcement:${announcement.dataset.announcementId}`;
  try {
    if (window.localStorage.getItem(storageKey) === "dismissed") {
      announcement.hidden = true;
      return;
    }
  } catch (_error) {
    // O comunicado continua utilizável quando o armazenamento local não está disponível.
  }

  const closeButton = announcement.querySelector("[data-announcement-dismiss]");
  closeButton?.addEventListener("click", () => {
    announcement.hidden = true;
    try {
      window.localStorage.setItem(storageKey, "dismissed");
    } catch (_error) {
      // Fechar durante a sessão já atende à ação mesmo sem persistência local.
    }
  });
})();
